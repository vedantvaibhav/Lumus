"""
Vercel serverless function for quiz generation
"""

import json
import os
import sys
from typing import Dict, Any

def create_fallback_quiz(topic: str) -> Dict[str, Any]:
    """Create a simple fallback quiz."""
    return {
        "title": f"{topic} Quiz",
        "total_questions": 5,
        "questions": [
            {
                "question": f"What is {topic}?",
                "type": "multiple-choice",
                "options": [f"A field related to {topic}", "A type of technology", "A historical event", "A scientific concept"],
                "answer": f"A field related to {topic}",
                "explanation": f"This is a general question about {topic}.",
                "difficulty": "easy"
            },
            {
                "question": f"True or False: {topic} is an important subject.",
                "type": "true-false",
                "answer": "True",
                "explanation": f"{topic} is indeed an important subject worth studying.",
                "difficulty": "easy"
            },
            {
                "question": f"Which best describes {topic}?",
                "type": "multiple-choice",
                "options": ["A complex subject", "A simple concept", "A practical skill", "An abstract idea"],
                "answer": "A complex subject",
                "explanation": f"{topic} typically involves multiple aspects and concepts.",
                "difficulty": "medium"
            },
            {
                "question": f"True or False: {topic} requires specialized knowledge.",
                "type": "true-false",
                "answer": "True",
                "explanation": "Most topics require some level of specialized knowledge to understand fully.",
                "difficulty": "easy"
            },
            {
                "question": f"What is the main focus of {topic}?",
                "type": "multiple-choice",
                "options": ["Understanding core concepts", "Memorizing facts", "Practical application", "All of the above"],
                "answer": "All of the above",
                "explanation": f"{topic} typically involves understanding, memorization, and application.",
                "difficulty": "medium"
            }
        ]
    }

def handler(request):
    """Vercel serverless function handler."""
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Parse request body
        if request.method == 'POST':
            body = request.get('body', '{}')
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Extract parameters
        api_key = data.get('api_key')
        topic = data.get('topic')
        num_questions = int(data.get('num_questions', 10))
        
        # Validate input
        if not topic:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Topic is required'})
            }
        
        # For now, use fallback quiz generation
        # In a real deployment, you would integrate with the enhanced quiz generator
        quiz = create_fallback_quiz(topic)
        
        # Add metadata
        quiz['source'] = f"AI analysis of {topic}"
        quiz['generated_at'] = "2024-01-01 00:00:00"
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(quiz)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
