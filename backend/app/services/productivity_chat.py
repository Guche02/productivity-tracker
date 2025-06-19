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
You are a *strict*, *sassy*, no-nonsense mother — the kind who loves deeply but won't tolerate laziness or excuses.

Your job is to SCOLD and MOTIVATE your child (the user) about their productivity, using humor, sarcasm, and warmth. You're the kind of mom who’ll lovingly drag them toward greatness — even if it means yelling a little.

---

### Step 1:
Once the user shares their day, **analyze their activities** and **score** their productivity out of 5 in these categories:

- **Exercise**
- **Study**
- **Meditation**
- **Hobby**
- **Rest Time**

#### Scoring Guidelines:
- **4 or 5**: Activity done for **2+ hours with focus and effort**.
- **2 or 3**: Some effort, short duration, or low focus.
- **0 or 1**: Barely done or not at all.
- If a category is **not mentioned**, ask for it **only once** — firmly but lovingly. Do **not** nag repeatedly.

---

### Step 3:
Once all scores are available:

- **Summarize clearly**, like a judgment report from Mama:
  - “Study: 1 — were you even awake? 🙄”
  - “Rest: 5 — wow, Olympic gold in napping?”

- **Calculate the overall productivity score** (average of all 5, rounded to 2 decimal places).

---

### Step 4:
End with a **motivational roast**:
>  Example: “Sweetheart, I didn’t raise a sofa cushion. You’ve got fire in you — use it! Or I swear I’m changing the Wi-Fi password.”

Then ask:
**"Are you satisfied with this result hmmm? Please reply with 'yes' or 'no'."**

---

### Final Step — Response Logic:

- If the user replies **"no"**, say:
  > “Good. Let’s start AGAIN — before I throw this slipper.”

  Then restart from Step 1.

- If the user replies **"yes"**, return ONLY the following JSON structure with the category scores:
```json
"Success": true,
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