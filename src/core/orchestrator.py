"""
Orchestrator for coordinating Reader and Quiz Maker agents.
Main entry point for the Self-Quiz Generator system.
"""

import time
from typing import Optional, Dict, Any
from ..agents.reader_agent import ReaderAgent
from ..agents.quiz_maker_agent import QuizMakerAgent
from .models import (
    ProcessingRequest, ProcessingResponse, Quiz, 
    SourceType, QuestionType, DifficultyLevel
)


class QuizGenerator:
    """Main orchestrator class that coordinates Reader and Quiz Maker agents."""
    
    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialize the Quiz Generator with agents.
        
        Args:
            google_api_key: Google API key (if not provided, will use environment variable)
        """
        self.reader_agent = ReaderAgent()
        self.quiz_maker_agent = QuizMakerAgent(google_api_key)
    
    def generate_quiz(self, request: ProcessingRequest) -> ProcessingResponse:
        """
        Generate a quiz from the provided source.
        
        Args:
            request: Processing request with source and parameters
            
        Returns:
            Processing response with generated quiz or error information
        """
        start_time = time.time()
        
        try:
            # Step 1: Read content from source
            print(f"Reading content from {request.source_type.value} source...")
            content_data = self.reader_agent.read(request.source, request.source_type)
            
            if not content_data.get('success', False):
                return ProcessingResponse(
                    success=False,
                    error=f"Failed to read source: {content_data.get('source_info', {}).get('error', 'Unknown error')}",
                    processing_time=time.time() - start_time,
                    source_info=content_data.get('source_info', {})
                )
            
            # Check if we have enough content
            text = content_data.get('text', '')
            if len(text.strip()) < 50:  # Reduced from 100 to 50
                return ProcessingResponse(
                    success=False,
                    error="Insufficient content to generate meaningful quiz questions",
                    processing_time=time.time() - start_time,
                    source_info=content_data.get('source_info', {})
                )
            
            print(f"Successfully read {len(text)} characters of content")
            
            # Step 2: Generate quiz questions
            print(f"Generating {request.num_questions} quiz questions...")
            quiz = self.quiz_maker_agent.generate_quiz(text, request)
            
            processing_time = time.time() - start_time
            print(f"Quiz generation completed in {processing_time:.2f} seconds")
            
            return ProcessingResponse(
                success=True,
                quiz=quiz,
                processing_time=processing_time,
                source_info=content_data.get('source_info', {})
            )
            
        except Exception as e:
            return ProcessingResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                processing_time=time.time() - start_time,
                source_info={}
            )
    
    def generate_from_url(self, url: str, num_questions: int = 10, 
                        difficulty: Optional[DifficultyLevel] = None,
                        question_types: Optional[list] = None) -> ProcessingResponse:
        """
        Convenience method to generate quiz from URL.
        
        Args:
            url: URL to read content from
            num_questions: Number of questions to generate
            difficulty: Preferred difficulty level
            question_types: Types of questions to generate
            
        Returns:
            Processing response with generated quiz
        """
        request = ProcessingRequest(
            source=url,
            source_type=SourceType.URL,
            num_questions=num_questions,
            difficulty_preference=difficulty,
            question_types=question_types
        )
        return self.generate_quiz(request)
    
    def generate_from_pdf(self, file_path: str, num_questions: int = 10,
                         difficulty: Optional[DifficultyLevel] = None,
                         question_types: Optional[list] = None) -> ProcessingResponse:
        """
        Convenience method to generate quiz from PDF file.
        
        Args:
            file_path: Path to PDF file
            num_questions: Number of questions to generate
            difficulty: Preferred difficulty level
            question_types: Types of questions to generate
            
        Returns:
            Processing response with generated quiz
        """
        request = ProcessingRequest(
            source=file_path,
            source_type=SourceType.PDF,
            num_questions=num_questions,
            difficulty_preference=difficulty,
            question_types=question_types
        )
        return self.generate_quiz(request)
    
    def generate_from_text(self, text: str, num_questions: int = 10,
                          difficulty: Optional[DifficultyLevel] = None,
                          question_types: Optional[list] = None) -> ProcessingResponse:
        """
        Convenience method to generate quiz from text content.
        
        Args:
            text: Text content to generate quiz from
            num_questions: Number of questions to generate
            difficulty: Preferred difficulty level
            question_types: Types of questions to generate
            
        Returns:
            Processing response with generated quiz
        """
        request = ProcessingRequest(
            source=text,
            source_type=SourceType.TEXT,
            num_questions=num_questions,
            difficulty_preference=difficulty,
            question_types=question_types
        )
        return self.generate_quiz(request)
    
    def generate_from_file(self, file_path: str, num_questions: int = 10,
                          difficulty: Optional[DifficultyLevel] = None,
                          question_types: Optional[list] = None) -> ProcessingResponse:
        """
        Convenience method to generate quiz from text file.
        
        Args:
            file_path: Path to text file
            num_questions: Number of questions to generate
            difficulty: Preferred difficulty level
            question_types: Types of questions to generate
            
        Returns:
            Processing response with generated quiz
        """
        request = ProcessingRequest(
            source=file_path,
            source_type=SourceType.FILE,
            num_questions=num_questions,
            difficulty_preference=difficulty,
            question_types=question_types
        )
        return self.generate_quiz(request)
    
    def auto_detect_and_generate(self, source: str, num_questions: int = 10,
                                difficulty: Optional[DifficultyLevel] = None,
                                question_types: Optional[list] = None) -> ProcessingResponse:
        """
        Automatically detect source type and generate quiz.
        
        Args:
            source: Source content (URL, file path, or text)
            num_questions: Number of questions to generate
            difficulty: Preferred difficulty level
            question_types: Types of questions to generate
            
        Returns:
            Processing response with generated quiz
        """
        source_type = self.reader_agent.detect_source_type(source)
        
        request = ProcessingRequest(
            source=source,
            source_type=source_type,
            num_questions=num_questions,
            difficulty_preference=difficulty,
            question_types=question_types
        )
        return self.generate_quiz(request)
