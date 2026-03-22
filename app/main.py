"""
Insight-Agent: Text Analysis Service
A simple REST API that performs basic text analysis on customer feedback.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Insight-Agent",
    description="Core service for AI-powered customer feedback analysis",
    version="1.0.0",
)


class TextInput(BaseModel):
    """Input model for text analysis."""

    text: str = Field(..., min_length=1, description="Text to analyze")


class AnalysisResult(BaseModel):
    """Output model for text analysis results."""

    original_text: str
    word_count: int
    character_count: int


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text(input_data: TextInput):
    """
    Analyze the provided text and return word and character counts.

    Args:
        input_data: JSON object containing the text to analyze

    Returns:
        Analysis results including original text, word count, and character count
    """
    text = input_data.text

    # Count words (split by whitespace)
    words = text.split()
    word_count = len(words)

    # Count characters (excluding leading/trailing whitespace for consistency)
    character_count = len(text)

    return AnalysisResult(
        original_text=text,
        word_count=word_count,
        character_count=character_count,
    )
