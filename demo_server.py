#!/usr/bin/env python3
"""
Demo server for Self-Quiz Generator Agent
Works without API calls for testing the UI
"""

import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


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


class DemoQuizHandler(BaseHTTPRequestHandler):
    """HTTP request handler for demo quiz generation."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_html()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/generate-quiz':
            self.handle_demo_quiz_generation()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the HTML file."""
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "HTML file not found")
    
    def handle_demo_quiz_generation(self):
        """Handle demo quiz generation requests."""
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            api_key = data.get('api_key')
            topic = data.get('topic')
            num_questions = int(data.get('num_questions', 10))
            difficulty = data.get('difficulty', 'any')
            question_types = data.get('question_types', ['multiple-choice', 'short'])
            
            # Validate input
            if not topic:
                self.send_error_response("Topic is required")
                return
            
            # Simulate processing time
            time.sleep(2)
            
            # Create demo quiz
            quiz = create_demo_quiz()
            
            # Adjust quiz based on parameters
            quiz['title'] = f"{topic.title()} Quiz (Demo)"
            quiz['source'] = topic
            
            # Filter questions based on difficulty if specified
            if difficulty != 'any':
                quiz['questions'] = [q for q in quiz['questions'] if q['difficulty'] == difficulty]
                quiz['total_questions'] = len(quiz['questions'])
            
            # Filter questions based on type if specified
            if question_types:
                quiz['questions'] = [q for q in quiz['questions'] if q['type'] in question_types]
                quiz['total_questions'] = len(quiz['questions'])
            
            # Limit to requested number of questions
            quiz['questions'] = quiz['questions'][:num_questions]
            quiz['total_questions'] = len(quiz['questions'])
            
            self.send_json_response(quiz)
                
        except Exception as e:
            self.send_error_response(f"Demo error: {str(e)}")
    
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
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass


def start_demo_server(port=8080):
    """Start the demo HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DemoQuizHandler)
    
    print(f"🎓 Self-Quiz Generator Agent - Demo Server")
    print(f"🌐 Demo server running at: http://localhost:{port}")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("=" * 50)
    print("🎮 DEMO MODE: Works without API calls!")
    print("📝 Try generating quizzes with sample content")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Demo server stopped. Thanks for testing!")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-Quiz Generator Agent Demo Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run server on')
    args = parser.parse_args()
    
    start_demo_server(args.port)


if __name__ == '__main__':
    main()
