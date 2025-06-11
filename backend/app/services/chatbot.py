from app.services.productivity_chat import productivity_assistant
from app.services.update_productivity import update_productivity_scores
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from typing_extensions import TypedDict
from typing import Annotated, List, Optional

class GraphState(TypedDict):
    messages: Annotated[List, add_messages]
    result: str
    scores: dict

def productivity_node(state: GraphState) -> GraphState:
    user_input = state["messages"][-1].content
    response = productivity_assistant(user_input=user_input,messages_state= state["messages"])
    print("----------------------------------------------------------Response from the productivity node: ", response)
    return {
        "messages": response["messages"],
        "result": response["result"],
        "scores": {}
    }

def check_success_in_result(state: GraphState) -> str:
    if '"success": true' in state["result"].lower():
        print("------------------------Success present in the result")
        return "success"
    
    print("--------------------------------Success not present in the result")
    return "continue"

def update_scores_node(state: GraphState) -> GraphState:
    scores = update_productivity_scores(state["result"])
    print("-------------------------------------Updated scores", scores)
    final_msg = "✅ Daily scores updated. Thanks for your time."
    return {
        "messages": state["messages"] + [AIMessage(content=final_msg)],
        "result": state["result"],
        "scores": scores
    }

workflow = StateGraph(GraphState)

workflow.add_node("run_productivity", productivity_node)
workflow.add_node("update_scores", update_scores_node)

workflow.set_entry_point("run_productivity")

workflow.add_conditional_edges(
    "run_productivity",
    check_success_in_result,
    {
        "success": "update_scores",
        "continue": END
    }
)

graph = workflow.compile()
message_history: List = []

def chatbot(user_input: str, history: Optional[List] = None) -> dict:
    """
    Wraps the LangGraph execution. Takes a user string input,
    updates message state, runs the graph, and returns the full state.

    Args:
        user_input (str): The user's input.
        history (List, optional): Previous message history.

    Returns:
        dict: Final GraphState with 'messages', 'result', and 'scores'.
    """
    state_messages = history or []
    state_messages.append(HumanMessage(content=user_input))

    state = {
        "messages": state_messages,
        "result": "",
        "scores": {}
    }
    print("-------------------------------state passed from chatbot: ", state)
    final_state = graph.invoke(state)
    return final_state

# chatbot("Hi")