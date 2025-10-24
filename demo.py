#!/usr/bin/env python3
"""
Demo script for the Self-Quiz Generator Agent.
Shows various usage examples and capabilities.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.orchestrator import QuizGenerator
from src.core.models import SourceType, DifficultyLevel, QuestionType
from src.utils.formatters import QuizFormatter


def demo_text_quiz():
    """Demo: Generate quiz from text content."""
    print("=" * 60)
    print("DEMO: Text-based Quiz Generation")
    print("=" * 60)
    
    sample_text = """
    Photosynthesis is the process by which plants convert light energy into chemical energy.
    This process occurs in the chloroplasts of plant cells, specifically in structures called thylakoids.
    The main pigment involved in photosynthesis is chlorophyll, which absorbs light primarily in the blue and red wavelengths.
    
    The process can be divided into two main stages: the light-dependent reactions and the Calvin cycle.
    In the light-dependent reactions, light energy is captured and used to produce ATP and NADPH.
    The Calvin cycle uses these energy carriers to convert carbon dioxide into glucose.
    
    The overall equation for photosynthesis is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2
    This process is crucial for life on Earth as it produces oxygen and forms the base of most food chains.
    """
    
    generator = QuizGenerator()
    formatter = QuizFormatter()
    
    print("Generating quiz from sample text about photosynthesis...")
    start_time = time.time()
    
    response = generator.generate_from_text(
        text=sample_text,
        num_questions=5,
        difficulty=DifficultyLevel.MEDIUM,
        question_types=[QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]
    )
    
    if response.success:
        quiz = response.quiz
        print(f"✓ Quiz generated successfully in {response.processing_time:.2f} seconds")
        
        # Print summary
        formatter.print_quiz_summary(quiz)
        
        # Export to different formats
        json_file = formatter.export_to_json(quiz, "demo_photosynthesis.json")
        html_file = formatter.export_to_html(quiz, "demo_photosynthesis.html")
        
        print(f"✓ Exported to: {json_file}")
        print(f"✓ Exported to: {html_file}")
        
    else:
        print(f"✗ Error: {response.error}")


def demo_url_quiz():
    """Demo: Generate quiz from URL (if internet available)."""
    print("\n" + "=" * 60)
    print("DEMO: URL-based Quiz Generation")
    print("=" * 60)
    
    # Use a simple, reliable URL for demo
    demo_url = "https://en.wikipedia.org/wiki/Photosynthesis"
    
    generator = QuizGenerator()
    formatter = QuizFormatter()
    
    print(f"Generating quiz from URL: {demo_url}")
    print("Note: This requires internet connection and may take a moment...")
    
    try:
        start_time = time.time()
        response = generator.generate_from_url(
            url=demo_url,
            num_questions=8,
            difficulty=DifficultyLevel.MEDIUM
        )
        
        if response.success:
            quiz = response.quiz
            print(f"✓ Quiz generated successfully in {response.processing_time:.2f} seconds")
            
            # Print first few questions
            print(f"\nSample questions from '{quiz.title}':")
            for i, question in enumerate(quiz.questions[:3], 1):
                print(f"\n{i}. {question.question}")
                if question.options:
                    for j, option in enumerate(question.options):
                        marker = "✓" if option == question.answer else " "
                        print(f"   {marker} {chr(65+j)}. {option}")
                else:
                    print(f"   Answer: {question.answer}")
            
            # Export
            csv_file = formatter.export_to_csv(quiz, "demo_wikipedia.csv")
            print(f"\n✓ Exported to: {csv_file}")
            
        else:
            print(f"✗ Error: {response.error}")
            
    except Exception as e:
        print(f"✗ Error generating quiz from URL: {str(e)}")
        print("This might be due to network issues or API limits.")


def demo_multiple_formats():
    """Demo: Export quiz in multiple formats."""
    print("\n" + "=" * 60)
    print("DEMO: Multiple Export Formats")
    print("=" * 60)
    
    sample_text = """
    Machine Learning is a subset of artificial intelligence that focuses on algorithms
    that can learn and make decisions from data without being explicitly programmed.
    
    There are three main types of machine learning:
    1. Supervised Learning: Uses labeled training data to learn a mapping from inputs to outputs
    2. Unsupervised Learning: Finds hidden patterns in data without labeled examples
    3. Reinforcement Learning: Learns through interaction with an environment using rewards and penalties
    
    Common algorithms include linear regression, decision trees, neural networks, and support vector machines.
    The field has applications in image recognition, natural language processing, recommendation systems, and more.
    """
    
    generator = QuizGenerator()
    formatter = QuizFormatter()
    
    print("Generating quiz about Machine Learning...")
    response = generator.generate_from_text(
        text=sample_text,
        num_questions=6,
        question_types=[QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]
    )
    
    if response.success:
        quiz = response.quiz
        
        # Export to all formats
        formats = {
            'JSON': formatter.export_to_json(quiz, "demo_ml.json"),
            'CSV': formatter.export_to_csv(quiz, "demo_ml.csv"),
            'HTML': formatter.export_to_html(quiz, "demo_ml.html"),
            'Anki': formatter.export_to_anki(quiz, "demo_ml_anki.csv")
        }
        
        print(f"✓ Generated quiz: '{quiz.title}'")
        print(f"✓ Questions: {quiz.total_questions}")
        print(f"✓ Topics: {', '.join(quiz.topics)}")
        
        print("\nExported files:")
        for format_name, file_path in formats.items():
            print(f"  {format_name}: {file_path}")
        
        print(f"\nDifficulty distribution:")
        for difficulty, count in quiz.difficulty_distribution.items():
            print(f"  {difficulty.capitalize()}: {count} questions")
            
    else:
        print(f"✗ Error: {response.error}")


def main():
    """Run all demo functions."""
    print("Self-Quiz Generator Agent - Demo")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("   Please set your OpenAI API key to run the demo:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("\n   You can get an API key from: https://platform.openai.com/api-keys")
        return
    
    try:
        # Run demos
        demo_text_quiz()
        demo_url_quiz()
        demo_multiple_formats()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Try the command-line interface: python main.py --help")
        print("2. Generate quizzes from your own content")
        print("3. Explore different output formats")
        print("4. Customize question types and difficulty levels")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {str(e)}")
        print("Please check your API key and internet connection.")


if __name__ == '__main__':
    main()
