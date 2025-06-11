from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
import getpass
import os
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

model = init_chat_model("llama3-8b-8192", model_provider="groq")

trimmer = trim_messages(
    max_tokens=500,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
         You are a friendly and supportive productivity assistant.

Your job is to understand the user's daily activities and score their productivity with clarity and warmth.

Step 1: Start by asking the user how their day went in a kind and engaging way.

Step 2: After receiving a natural language description of their day, do the following:

- Score the user's productivity out of 5 for the following categories:
   - Exercise
   - Study
   - Meditation
   - Hobby
   - Rest Time

**Scoring Guidelines:**
- If the user mentions doing a category for **2 to 3 hours or more with full concentration**, score it **4 or 5**.
- If the activity was done for less time or with low focus, give a **lower score**.
- If a category is **not mentioned**, ask only once (and kindly) for more detail. Do not repeat follow-ups.

Step 3: Once you have scores for all categories:
- Summarize the scores clearly.
- Calculate and share the **overall productivity score** (average of all categories, rounded to 2 decimal places).

Step 4: Add a encouraging and motivational message for the user.
- Then ask:
**"Are you satisfied with this result? Please reply with 'yes' or 'no'."**

---

Step 4: Final response logic:

- If the user replies with **"no"**, say:
  "No worries! I will restart again. Let's begin once more."
  Then restart from Step 1.

- If the user replies with **"yes"**, return the following JSON format(Don't return any other text or explanation):
```json
  "Success": True,
{{
  "exercise": <score>,
  "study": <score>,
  "meditation": <score>,
  "hobby": <score>,
  "rest_time": <score>
}}
            """,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

class State(TypedDict):
    messages: Annotated[List, add_messages]

workflow = StateGraph(state_schema=State)

def call_model(state: State):
    messages = trimmer.invoke(state["messages"])
    print(f"-----------------------------------------------------Trimmed messages: {messages}")  # Debugging line to check trimmed messages
    result = model.invoke(prompt_template.format_messages(messages=messages))
    return {"messages": [result]}

workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
workflow.set_entry_point("model")

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)
graph = workflow.compile(checkpointer=memory)

def productivity_assistant(user_input: str, thread_id: str, messages_state: List = None) -> tuple[str, List]:
    config = {"configurable": {"thread_id": thread_id}}

    if messages_state is None:
        messages_state = []

    messages_state.append(HumanMessage(content=user_input))

    state = {"messages": messages_state}
    result = graph.invoke(state, config=config)
    messages_state.extend(result["messages"])

    return {"result": result["messages"][-1].content, "messages": messages_state}

if __name__ == "__main__":
    # response = productivity_assistant("I didn't do much today.")
    # response = productivity_assistant("")
    # response = productivity_assistant("I did 30 minutes of exercise, studied for 2 hours, meditated for 15 minutes, and spent some time on my hobby. I also took a short nap.")
    response = productivity_assistant("yes")
    print(response)  