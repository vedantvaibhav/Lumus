import os
import json
import sys
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_quiz_generator import EnhancedQuizGenerator
except ImportError:
    EnhancedQuizGenerator = None

def handler(request):
    """Vercel serverless function handler."""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # Handle POST requests
    if request.method == 'POST':
        try:
            # Parse request body
            data = json.loads(request.body)
            
            # Extract parameters
            api_key = data.get('api_key')
            topic = data.get('topic')
            num_questions = int(data.get('num_questions', 10))
            
            # Validate input
            if not api_key:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'API key is required'})
                }
            
            if not topic:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Topic is required'})
                }
            
            # Initialize quiz generator
            if not EnhancedQuizGenerator:
                return {
                    'statusCode': 500,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Quiz generator not available'})
                }
                
            quiz_generator = EnhancedQuizGenerator(api_key)
            
            # Generate quiz
            quiz = quiz_generator.generate_quiz_from_topic(topic, num_questions)
            
            # Add metadata
            quiz['source'] = f"Web search + AI analysis of {topic}"
            quiz['generated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'statusCode': 200,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(quiz)
            }
                
        except Exception as e:
            print(f"❌ Error generating quiz: {e}")
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Failed to generate quiz: {str(e)}'})
            }
    
    return {
        'statusCode': 405,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'})
    }