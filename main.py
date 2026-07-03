from pydantic import BaseModel , field_validator ,ConfigDict
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class ResumeReview(BaseModel):
    model_config = {"extra": "forbid"}
    score: int
    feedback: str

    @field_validator("score")
    @classmethod
    def validate_score(cls, value: int) -> int:
        if value < 0 or value > 100:
            raise ValueError("Score must be between 0 and 100")
        return value

schema = ResumeReview.model_json_schema()
schema["additionalProperties"] = False


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.responses.create(
    model = "openai/gpt-oss-120b",
    input = [
        {
            "role" : "developer",
            "content": """ You are a Senior Agentic AI Engineer.Review the candidate's resume 
            Give a score from 0 to 100, where 100 means an excellent fit and 0 means no relevant experience at all"""
        },
        {
            "role" : "user",
            "content":  """
                            Name: Rahul Sharma
                            Built AI agents using OpenAI Agents SDK and PydanticAI.
                            Developed a Patient Health Assistant Agent with FastAPI and structured outputs.
                            Experienced in Python, function calling, REST APIs, and LLM application development.
                        """
        }
    ] ,
            text = {
            "format" : {
                "type" : "json_schema",
                "name" : "resume_review",
                "schema" : schema,
                "strict" : True
            }
        }
)
print(response.output_text)
review = ResumeReview.model_validate_json(response.output_text)
print(review.score)
print(review.feedback)