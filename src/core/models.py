"""
Data models and schemas for the Self-Quiz Generator Agent.
"""

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions that can be generated."""
    MULTIPLE_CHOICE = "multiple-choice"
    SHORT_ANSWER = "short"
    TRUE_FALSE = "true-false"


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizQuestion(BaseModel):
    """Represents a single quiz question."""
    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="The correct answer")
    type: QuestionType = Field(..., description="Type of question")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    options: Optional[List[str]] = Field(None, description="Multiple choice options (if applicable)")
    explanation: Optional[str] = Field(None, description="Explanation for the answer")
    topic: Optional[str] = Field(None, description="Topic or subject area")


class Quiz(BaseModel):
    """Represents a complete quiz."""
    title: str = Field(..., description="Title of the quiz")
    source: str = Field(..., description="Source of the content")
    questions: List[QuizQuestion] = Field(..., description="List of questions")
    total_questions: int = Field(..., description="Total number of questions")
    difficulty_distribution: dict = Field(default_factory=dict, description="Distribution of difficulty levels")
    topics: List[str] = Field(default_factory=list, description="Topics covered in the quiz")


class SourceType(str, Enum):
    """Types of sources that can be processed."""
    URL = "url"
    PDF = "pdf"
    TEXT = "text"
    FILE = "file"


class ProcessingRequest(BaseModel):
    """Request for processing a source and generating a quiz."""
    source: str = Field(..., description="Source content (URL, file path, or text)")
    source_type: SourceType = Field(..., description="Type of source")
    num_questions: int = Field(default=10, ge=1, le=50, description="Number of questions to generate")
    difficulty_preference: Optional[DifficultyLevel] = Field(None, description="Preferred difficulty level")
    topics: Optional[List[str]] = Field(None, description="Specific topics to focus on")
    question_types: Optional[List[QuestionType]] = Field(None, description="Types of questions to generate")


class ProcessingResponse(BaseModel):
    """Response from processing a source."""
    success: bool = Field(..., description="Whether processing was successful")
    quiz: Optional[Quiz] = Field(None, description="Generated quiz (if successful)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    source_info: dict = Field(default_factory=dict, description="Information about the source")
