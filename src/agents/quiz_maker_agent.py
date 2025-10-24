"""
Quiz Maker Agent for generating structured quiz questions from text content.
Uses Google's Gemini API to create educational quiz questions.
"""

import json
import os
import random
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from ..core.models import (
    Quiz, QuizQuestion, QuestionType, DifficultyLevel, 
    ProcessingRequest, SourceType
)


class QuizMakerAgent:
    """Agent responsible for generating quiz questions from text content."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Quiz Maker Agent with Google Gemini client."""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')  # Better quality model
    
    def generate_quiz(self, text: str, request: ProcessingRequest) -> Quiz:
        """
        Generate a quiz from the provided text content.
        
        Args:
            text: The cleaned text content
            request: Processing request with parameters
            
        Returns:
            Generated Quiz object
        """
        try:
            # Truncate text if too long (to stay within token limits)
            max_chars = 25000  # Increased limit for better context
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            # Generate questions based on request parameters
            questions = self._generate_questions(text, request)
            
            # Create quiz metadata
            quiz_title = self._generate_quiz_title(text, request)
            topics = self._extract_topics(text, questions)
            difficulty_distribution = self._calculate_difficulty_distribution(questions)
            
            return Quiz(
                title=quiz_title,
                source=request.source,
                questions=questions,
                total_questions=len(questions),
                difficulty_distribution=difficulty_distribution,
                topics=topics
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    def _generate_questions(self, text: str, request: ProcessingRequest) -> List[QuizQuestion]:
        """Generate quiz questions from text."""
        questions = []
        
        # Determine question types to generate
        question_types = request.question_types or [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]
        
        # Generate questions in batches to avoid token limits
        batch_size = min(5, request.num_questions)
        remaining_questions = request.num_questions
        
        while remaining_questions > 0 and len(questions) < request.num_questions:
            current_batch_size = min(batch_size, remaining_questions)
            
            batch_questions = self._generate_question_batch(
                text, current_batch_size, question_types, request
            )
            
            questions.extend(batch_questions)
            remaining_questions -= len(batch_questions)
        
        return questions[:request.num_questions]
    
    def _generate_question_batch(self, text: str, batch_size: int, 
                               question_types: List[QuestionType], 
                               request: ProcessingRequest) -> List[QuizQuestion]:
        """Generate a batch of questions."""
        
        # Create the system prompt
        system_prompt = self._create_system_prompt(question_types, request)
        
        # Create the user prompt
        user_prompt = f"""
Generate {batch_size} quiz questions from the following text:

{text}

Focus on the most important concepts and key information. Make sure questions are:
- Clear and unambiguous
- Educational and meaningful
- Appropriate for the difficulty level
- Cover different aspects of the content

Return the questions in the following JSON format:
{{
    "questions": [
        {{
            "question": "Question text here",
            "answer": "Correct answer here",
            "type": "multiple-choice" or "short" or "true-false",
            "difficulty": "easy" or "medium" or "hard",
            "options": ["Option A", "Option B", "Option C", "Option D"] (only for multiple-choice),
            "explanation": "Brief explanation of why this answer is correct",
            "topic": "Main topic or concept this question covers"
        }}
    ]
}}
"""
        
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,  # Lower temperature for more consistent quality
                    max_output_tokens=4000,  # Increased token limit
                )
            )
            
            content = response.text
            
            # Parse JSON response
            try:
                result = json.loads(content)
                questions_data = result.get('questions', [])
                
                # Convert to QuizQuestion objects
                questions = []
                for q_data in questions_data:
                    try:
                        question = QuizQuestion(
                            question=q_data['question'],
                            answer=q_data['answer'],
                            type=QuestionType(q_data['type']),
                            difficulty=DifficultyLevel(q_data['difficulty']),
                            options=q_data.get('options'),
                            explanation=q_data.get('explanation'),
                            topic=q_data.get('topic')
                        )
                        questions.append(question)
                    except Exception as e:
                        print(f"Error parsing question: {e}")
                        continue
                
                return questions
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                return []
                
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    def _create_system_prompt(self, question_types: List[QuestionType], 
                            request: ProcessingRequest) -> str:
        """Create the system prompt for quiz generation."""
        
        prompt = """You are an expert educational quiz generator with advanced pedagogical knowledge. Your task is to create high-quality quiz questions that test understanding, critical thinking, and knowledge retention.

STRICT QUALITY GUIDELINES:
1. Questions MUST be clear, unambiguous, and educationally valuable
2. Focus on IMPORTANT concepts, key facts, and critical information that students should know
3. AVOID trivial details, obscure facts, or overly specific information
4. Create questions that test UNDERSTANDING and APPLICATION, not just memorization
5. Ensure answers are accurate, well-explained, and educational
6. Make questions challenging but fair - they should make students think
7. Include questions that test different cognitive levels (knowledge, comprehension, application, analysis)
8. Each question should have clear learning objectives

Question Types:
- multiple-choice: Provide 4 options (A, B, C, D) with ONE clearly correct answer and 3 plausible distractors
- short: Open-ended questions requiring brief but thoughtful answers
- true-false: Simple true/false statements that test understanding of key concepts

Difficulty Levels:
- easy: Basic facts, definitions, and fundamental concepts
- medium: Application of concepts, understanding relationships, problem-solving
- hard: Analysis, synthesis, critical thinking, and complex reasoning

QUALITY STANDARDS:
- Each question should teach something valuable
- Explanations should be educational and help students learn
- Avoid questions that are too easy or too obscure
- Ensure questions are relevant to the topic and content provided
- Make questions engaging and thought-provoking"""
        
        if request.difficulty_preference:
            prompt += f"\n\nPreferred difficulty level: {request.difficulty_preference.value}"
        
        if request.topics:
            prompt += f"\n\nFocus on these topics: {', '.join(request.topics)}"
        
        return prompt
    
    def _generate_quiz_title(self, text: str, request: ProcessingRequest) -> str:
        """Generate an appropriate title for the quiz."""
        try:
            prompt = f"""
Based on the following text content, generate a concise and descriptive title for a quiz:

{text[:500]}...

The title should be:
- Clear and descriptive
- 5-10 words maximum
- Professional and educational
- Related to the main topic

Return only the title, no additional text.
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=50,
                )
            )
            
            title = response.text.strip()
            return title.replace('"', '').replace("'", "")
            
        except Exception:
            # Fallback title
            source_type = request.source_type.value
            return f"Quiz on {source_type} Content"
    
    def _extract_topics(self, text: str, questions: List[QuizQuestion]) -> List[str]:
        """Extract main topics from the text and questions."""
        topics = set()
        
        # Extract topics from questions
        for question in questions:
            if question.topic:
                topics.add(question.topic)
        
        # If no topics from questions, try to extract from text
        if not topics:
            try:
                prompt = f"""
Extract the main topics or subject areas from this text. Return 3-5 key topics:

{text[:1000]}...

Return topics as a simple list, one per line.
"""
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=200,
                    )
                )
                
                topics_text = response.text
                topics = set(line.strip() for line in topics_text.split('\n') if line.strip())
                
            except Exception:
                topics = {"General Knowledge"}
        
        return list(topics)[:5]  # Limit to 5 topics
    
    def _calculate_difficulty_distribution(self, questions: List[QuizQuestion]) -> Dict[str, int]:
        """Calculate the distribution of difficulty levels."""
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        
        for question in questions:
            distribution[question.difficulty.value] += 1
        
        return distribution
