"""
Backend for the Resume Reviewer frontend.

This wraps your existing resume-scoring logic in a small FastAPI server so the
browser has something safe to talk to. The Groq API key stays on this server
and is never sent to the browser.

Run it with:
    pip install fastapi uvicorn openai pydantic python-dotenv --break-system-packages
    uvicorn backend:app --reload --port 8000

Make sure GROQ_API_KEY is set in a .env file in this same folder.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Allows a locally opened HTML file (or localhost dev server) to call this API.
# Tighten this to your real frontend URL once you deploy anywhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


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


class ReviewRequest(BaseModel):
    name: str
    resume_text: str


schema = ResumeReview.model_json_schema()
schema["additionalProperties"] = False


@app.post("/review")
def review_resume(payload: ReviewRequest):
    if not payload.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty.")

    user_content = f"Name: {payload.name}\n\n{payload.resume_text}"

    response = client.responses.create(
        model="openai/gpt-oss-120b",
        input=[
            {
                "role": "developer",
                "content": """You are a Senior Agentic AI Engineer. Review the candidate's resume.
                Give a score from 0 to 100, where 100 means an excellent fit and 0 means no relevant experience at all.""",
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "resume_review",
                "schema": schema,
                "strict": True,
            }
        },
    )

    try:
        review = ResumeReview.model_validate_json(response.output_text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Model returned invalid data: {e}")

    return {"score": review.score, "feedback": review.feedback}
