#!/usr/bin/env python3
"""
Demo mode for Self-Quiz Generator Agent
Works without API calls for testing the UI
"""

import json
import time
from datetime import datetime

def create_demo_quiz():
    """Create a demo quiz for testing."""
    return {
        "title": "Photosynthesis Quiz (Demo)",
        "source": "Demo Content",
        "total_questions": 5,
        "difficulty_distribution": {
            "easy": 2,
            "medium": 2,
            "hard": 1
        },
        "topics": ["Photosynthesis", "Plant Biology", "Energy Conversion"],
        "questions": [
            {
                "question": "What is the main pigment involved in photosynthesis?",
                "answer": "Chlorophyll",
                "type": "multiple-choice",
                "difficulty": "easy",
                "options": ["Chlorophyll", "Carotene", "Xanthophyll", "Anthocyanin"],
                "explanation": "Chlorophyll is the primary pigment that captures light energy for photosynthesis.",
                "topic": "Photosynthesis Basics"
            },
            {
                "question": "In which organelle does photosynthesis occur?",
                "answer": "Chloroplast",
                "type": "multiple-choice",
                "difficulty": "easy",
                "options": ["Mitochondria", "Chloroplast", "Nucleus", "Ribosome"],
                "explanation": "Chloroplasts contain the thylakoids where photosynthesis takes place.",
                "topic": "Cell Biology"
            },
            {
                "question": "What are the two main stages of photosynthesis?",
                "answer": "Light-dependent reactions and Calvin cycle",
                "type": "short",
                "difficulty": "medium",
                "explanation": "The light-dependent reactions capture energy, while the Calvin cycle uses it to make glucose.",
                "topic": "Photosynthesis Process"
            },
            {
                "question": "What is the overall equation for photosynthesis?",
                "answer": "6CO2 + 6H2O + light energy → C6H12O6 + 6O2",
                "type": "short",
                "difficulty": "medium",
                "explanation": "This equation shows how carbon dioxide and water are converted to glucose and oxygen using light energy.",
                "topic": "Photosynthesis Chemistry"
            },
            {
                "question": "True or False: Photosynthesis only occurs in green plants.",
                "answer": "False",
                "type": "true-false",
                "difficulty": "hard",
                "explanation": "Photosynthesis also occurs in algae, cyanobacteria, and some other photosynthetic organisms.",
                "topic": "Photosynthesis Diversity"
            }
        ]
    }

def main():
    """Run demo mode."""
    print("🎓 Self-Quiz Generator Agent - Demo Mode")
    print("=" * 50)
    print("This demo works without API calls!")
    print()
    
    # Create demo quiz
    quiz = create_demo_quiz()
    
    print(f"📊 Quiz: {quiz['title']}")
    print(f"📝 Questions: {quiz['total_questions']}")
    print(f"🏷️ Topics: {', '.join(quiz['topics'])}")
    print()
    
    # Display questions
    for i, question in enumerate(quiz['questions'], 1):
        print(f"Question {i} ({question['difficulty'].upper()}):")
        print(f"Q: {question['question']}")
        
        if question.get('options'):
            print("Options:")
            for j, option in enumerate(question['options']):
                marker = "✓" if option == question['answer'] else " "
                print(f"  {marker} {chr(65+j)}. {option}")
        else:
            print(f"A: {question['answer']}")
        
        if question['explanation']:
            print(f"Explanation: {question['explanation']}")
        
        print("-" * 40)
    
    # Save demo quiz
    with open('demo_quiz.json', 'w') as f:
        json.dump(quiz, f, indent=2)
    
    print(f"\n💾 Demo quiz saved to: demo_quiz.json")
    print("🎉 Demo completed successfully!")

if __name__ == "__main__":
    main()
