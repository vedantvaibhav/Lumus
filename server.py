#!/usr/bin/env python3
"""
Simple HTTP server for Self-Quiz Generator Agent
Serves the HTML UI and handles quiz generation requests
"""

import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.orchestrator import QuizGenerator
from src.core.models import SourceType, DifficultyLevel, QuestionType, ProcessingRequest


class QuizHandler(BaseHTTPRequestHandler):
    """HTTP request handler for quiz generation."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_html()
        elif self.path.startswith('/images/'):
            self.serve_static_file()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/generate-quiz':
            self.handle_quiz_generation()
        else:
            self.send_error(404)
    
    def serve_static_file(self):
        """Serve static files from the images directory."""
        try:
            # Remove leading slash and serve from current directory
            file_path = self.path[1:]  # Remove leading '/'
            
            # Security check - only allow files in images directory
            if not file_path.startswith('images/'):
                self.send_error(403, "Access denied")
                return
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return
            
            # Determine content type based on file extension
            if file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_path.endswith('.gif'):
                content_type = 'image/gif'
            elif file_path.endswith('.svg'):
                content_type = 'image/svg+xml'
            else:
                content_type = 'application/octet-stream'
            
            # Read and serve the file
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            print(f"Error serving static file {self.path}: {e}")
            self.send_error(500, "Internal server error")
    
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
            difficulty = data.get('difficulty', 'any')
            question_types = data.get('question_types', ['multiple-choice', 'short'])
            
            # Validate input
            if not api_key:
                self.send_error_response("Google API key is required")
                return
            
            if not topic:
                self.send_error_response("Topic is required")
                return
            
            # Create quiz generator
            generator = QuizGenerator(api_key)
            
            # Prepare request
            difficulty_level = None
            if difficulty != 'any':
                difficulty_level = DifficultyLevel(difficulty)
            
            question_type_objects = []
            for qtype in question_types:
                if qtype == 'multiple-choice':
                    question_type_objects.append(QuestionType.MULTIPLE_CHOICE)
                elif qtype == 'short':
                    question_type_objects.append(QuestionType.SHORT_ANSWER)
                elif qtype == 'true-false':
                    question_type_objects.append(QuestionType.TRUE_FALSE)
            
            request = ProcessingRequest(
                source=topic,
                source_type=SourceType.TEXT,
                num_questions=num_questions,
                difficulty_preference=difficulty_level,
                question_types=question_type_objects if question_type_objects else None
            )
            
            # Generate quiz
            response = generator.generate_quiz(request)
            
            if response.success:
                quiz = response.quiz
                
                # Convert quiz to JSON-serializable format
                quiz_data = {
                    'title': quiz.title,
                    'source': quiz.source,
                    'total_questions': quiz.total_questions,
                    'difficulty_distribution': quiz.difficulty_distribution,
                    'topics': quiz.topics,
                    'questions': []
                }
                
                for question in quiz.questions:
                    question_data = {
                        'question': question.question,
                        'answer': question.answer,
                        'type': question.type.value,
                        'difficulty': question.difficulty.value,
                        'explanation': question.explanation,
                        'topic': question.topic
                    }
                    
                    if question.options:
                        question_data['options'] = question.options
                    
                    quiz_data['questions'].append(question_data)
                
                self.send_json_response(quiz_data)
            else:
                self.send_error_response(f"Failed to generate quiz: {response.error}")
                
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}")
    
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


def start_server(port=8080):
    """Start the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, QuizHandler)
    
    print(f"🚀 Self-Quiz Generator Agent Server")
    print(f"🌐 Server running at: http://localhost:{port}")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thanks for using Self-Quiz Generator Agent!")
        httpd.shutdown()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-Quiz Generator Agent Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run server on')
    args = parser.parse_args()
    
    start_server(args.port)


if __name__ == '__main__':
    main()
