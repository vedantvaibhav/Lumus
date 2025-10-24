"""
Vercel serverless function for quiz generation
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# Add the parent directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from enhanced_quiz_generator import EnhancedQuizGenerator
except ImportError:
    # Fallback if enhanced_quiz_generator is not available
    EnhancedQuizGenerator = None

class QuizHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for quiz generation."""
        if self.path == '/generate-quiz':
            self.handle_quiz_generation()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_index()
        else:
            self.send_error(404)
    
    def serve_index(self):
        """Serve the main quiz page."""
        try:
            # Read the interactive quiz HTML file
            html_path = os.path.join(os.path.dirname(__file__), '..', 'interactive_quiz.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error serving page: {str(e)}")
    
    def handle_quiz_generation(self):
        """Handle quiz generation requests."""
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            api_key = data.get('api_key')
            topic = data.get('topic')
            num_questions = int(data.get('num_questions', 10))
            
            # Validate input
            if not api_key:
                self.send_error_response("API key is required")
                return
            
            if not topic:
                self.send_error_response("Topic is required")
                return
            
            # Generate quiz using enhanced method
            if EnhancedQuizGenerator:
                generator = EnhancedQuizGenerator(api_key)
                quiz = generator.generate_quiz_from_topic(topic, num_questions)
            else:
                # Fallback to simple quiz generation
                quiz = self.create_fallback_quiz(topic)
            
            # Add metadata
            quiz['source'] = f"AI analysis of {topic}"
            
            self.send_json_response(quiz)
                
        except Exception as e:
            self.send_error_response(f"Failed to generate quiz: {str(e)}")
    
    def create_fallback_quiz(self, topic):
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
                }
            ]
        }
    
    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, message):
        """Send error response."""
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {'error': message}
        json_data = json.dumps(error_data)
        self.wfile.write(json_data.encode('utf-8'))

def handler(request):
    """Vercel serverless function handler."""
    handler = QuizHandler(request)
    return handler
