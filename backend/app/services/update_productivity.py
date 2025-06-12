from app.schemas.user import ProductivityScore
import getpass
import os
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
from app.services.productivity_chat import productivity_assistant
from pydantic import BaseModel, Field

load_dotenv()

# class ProductivityScore(BaseModel):
#     exercise: float = Field(0, ge=0, le=5)
#     study: float = Field(0, ge=0, le=5)
#     meditation: float = Field(0, ge=0, le=5)
#     hobby: float = Field(0, ge=0, le=5)
#     rest_time: float = Field(0, ge=0, le=5)

if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

model = init_chat_model("llama3-8b-8192", model_provider="groq")
structured_parser = model.with_structured_output(ProductivityScore)

def update_productivity_scores(text: str) -> dict:
    """
    Takes a string (e.g. from `productivity_assistant`) and uses LLM to parse it
    into structured JSON according to the ProductivityScore schema.
    """
    try:
        parsed = structured_parser.invoke(text)
        return parsed.model_dump()
    except Exception as e:
        print(f"Failed to parse structured productivity scores: {e}")
        return {}
    
# response =update_productivity_scores("This is  the final output in json format { 'exercise': 4.5, 'study': 3.0, 'meditation': 2.5, 'hobby': 4.0, 'rest_time': 5.0 } . Feedback: good job in exercise and rest time, but could improve on study and meditation.")
# print(response)