#!/usr/bin/env python3
"""
Enhanced Quiz Server with Web Search + AI
Integrates web data gathering with AI quiz generation
"""

import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our enhanced quiz generator
from enhanced_quiz_generator import EnhancedQuizGenerator

class EnhancedQuizHandler(BaseHTTPRequestHandler):
    """HTTP request handler for enhanced quiz generation."""
    
    def __init__(self, *args, **kwargs):
        self.quiz_generator = None
        super().__init__(*args, **kwargs)
    
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
        """Serve the interactive quiz HTML file."""
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
        """Handle enhanced quiz generation requests."""
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
            
            # Initialize quiz generator if not already done
            if not self.quiz_generator:
                try:
                    self.quiz_generator = EnhancedQuizGenerator(api_key)
                except Exception as e:
                    self.send_error_response(f"Failed to initialize AI model: {str(e)}")
                    return
            
            # Generate quiz using enhanced method
            print(f"🎯 Generating quiz for: {topic}")
            quiz = self.quiz_generator.generate_quiz_from_topic(topic, num_questions)
            
            # Add metadata
            quiz['source'] = f"Web search + AI analysis of {topic}"
            quiz['generated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            self.send_json_response(quiz)
                
        except Exception as e:
            print(f"❌ Error generating quiz: {e}")
            self.send_error_response(f"Failed to generate quiz: {str(e)}")
    
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

def start_enhanced_server(port=8080):
    """Start the enhanced HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, EnhancedQuizHandler)
    
    print(f"🚀 Enhanced Quiz Generator Server")
    print(f"🌐 Server running at: http://localhost:{port}")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("=" * 50)
    print("🎮 FEATURES:")
    print("✅ Web search data gathering")
    print("✅ AI-powered quiz generation")
    print("✅ Multiple-choice + True/False only")
    print("✅ Real-time topic research")
    print("✅ Multiple AI models fallback")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Enhanced server stopped. Thanks for testing!")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Quiz Generator Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run server on')
    args = parser.parse_args()
    
    start_enhanced_server(args.port)

if __name__ == '__main__':
    main()
