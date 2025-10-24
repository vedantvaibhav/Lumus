"""
Quiz formatter for exporting quizzes to various formats.
Supports JSON, CSV, HTML, and Anki-compatible formats.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.models import Quiz, QuizQuestion


class QuizFormatter:
    """Formatter for exporting quizzes to different formats."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_to_json(self, quiz: Quiz, file_path: Optional[str] = None) -> str:
        """
        Export quiz to JSON format.
        
        Args:
            quiz: Quiz object to export
            file_path: Optional file path (if None, generates filename)
            
        Returns:
            Path to the exported file
        """
        if file_path is None:
            safe_title = "".join(c for c in quiz.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_path = f"quiz_{safe_title}_{self.timestamp}.json"
        
        quiz_data = {
            "title": quiz.title,
            "source": quiz.source,
            "total_questions": quiz.total_questions,
            "difficulty_distribution": quiz.difficulty_distribution,
            "topics": quiz.topics,
            "generated_at": datetime.now().isoformat(),
            "questions": []
        }
        
        for question in quiz.questions:
            question_data = {
                "question": question.question,
                "answer": question.answer,
                "type": question.type.value,
                "difficulty": question.difficulty.value,
                "explanation": question.explanation,
                "topic": question.topic
            }
            
            if question.options:
                question_data["options"] = question.options
            
            quiz_data["questions"].append(question_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def export_to_csv(self, quiz: Quiz, file_path: Optional[str] = None) -> str:
        """
        Export quiz to CSV format.
        
        Args:
            quiz: Quiz object to export
            file_path: Optional file path (if None, generates filename)
            
        Returns:
            Path to the exported file
        """
        if file_path is None:
            safe_title = "".join(c for c in quiz.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_path = f"quiz_{safe_title}_{self.timestamp}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Question Number', 'Question', 'Answer', 'Type', 'Difficulty',
                'Options', 'Explanation', 'Topic'
            ])
            
            # Write questions
            for i, question in enumerate(quiz.questions, 1):
                options_str = " | ".join(question.options) if question.options else ""
                
                writer.writerow([
                    i,
                    question.question,
                    question.answer,
                    question.type.value,
                    question.difficulty.value,
                    options_str,
                    question.explanation or "",
                    question.topic or ""
                ])
        
        return file_path
    
    def export_to_html(self, quiz: Quiz, file_path: Optional[str] = None) -> str:
        """
        Export quiz to HTML format with interactive elements.
        
        Args:
            quiz: Quiz object to export
            file_path: Optional file path (if None, generates filename)
            
        Returns:
            Path to the exported file
        """
        if file_path is None:
            safe_title = "".join(c for c in quiz.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_path = f"quiz_{safe_title}_{self.timestamp}.html"
        
        html_content = self._generate_html_content(quiz)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def export_to_anki(self, quiz: Quiz, file_path: Optional[str] = None) -> str:
        """
        Export quiz to Anki-compatible format (CSV with Anki fields).
        
        Args:
            quiz: Quiz object to export
            file_path: Optional file path (if None, generates filename)
            
        Returns:
            Path to the exported file
        """
        if file_path is None:
            safe_title = "".join(c for c in quiz.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_path = f"anki_{safe_title}_{self.timestamp}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write Anki header
            writer.writerow(['Front', 'Back', 'Tags'])
            
            # Write questions as Anki cards
            for question in quiz.questions:
                front = question.question
                
                # Format back side based on question type
                if question.type.value == "multiple-choice" and question.options:
                    back = f"Answer: {question.answer}\n\nOptions:\n"
                    for i, option in enumerate(question.options, 1):
                        back += f"{i}. {option}\n"
                else:
                    back = f"Answer: {question.answer}"
                
                if question.explanation:
                    back += f"\n\nExplanation: {question.explanation}"
                
                tags = f"quiz {question.difficulty.value}"
                if question.topic:
                    tags += f" {question.topic.replace(' ', '_')}"
                
                writer.writerow([front, back, tags])
        
        return file_path
    
    def _generate_html_content(self, quiz: Quiz) -> str:
        """Generate HTML content for the quiz."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{quiz.title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .quiz-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .quiz-header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
        }}
        .quiz-title {{
            color: #333;
            margin: 0;
            font-size: 2em;
        }}
        .quiz-meta {{
            color: #666;
            margin-top: 10px;
        }}
        .question {{
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fafafa;
        }}
        .question-number {{
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }}
        .question-text {{
            font-size: 1.1em;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        .options {{
            margin: 15px 0;
        }}
        .option {{
            margin: 8px 0;
            padding: 8px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #007bff;
        }}
        .answer {{
            background: #d4edda;
            border-left-color: #28a745;
            font-weight: bold;
        }}
        .explanation {{
            margin-top: 15px;
            padding: 10px;
            background: #e7f3ff;
            border-radius: 4px;
            font-style: italic;
        }}
        .difficulty {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .difficulty.easy {{ background: #d4edda; color: #155724; }}
        .difficulty.medium {{ background: #fff3cd; color: #856404; }}
        .difficulty.hard {{ background: #f8d7da; color: #721c24; }}
        .topic {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="quiz-container">
        <div class="quiz-header">
            <h1 class="quiz-title">{quiz.title}</h1>
            <div class="quiz-meta">
                <p>Source: {quiz.source}</p>
                <p>Total Questions: {quiz.total_questions}</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
"""
        
        for i, question in enumerate(quiz.questions, 1):
            html += f"""
        <div class="question">
            <div class="question-number">
                Question {i}
                <span class="difficulty {question.difficulty.value}">{question.difficulty.value.upper()}</span>
            </div>
            <div class="question-text">{question.question}</div>
"""
            
            if question.options:
                html += '<div class="options">'
                for j, option in enumerate(question.options):
                    is_correct = option == question.answer
                    option_class = "option answer" if is_correct else "option"
                    html += f'<div class="{option_class}">{chr(65+j)}. {option}</div>'
                html += '</div>'
            else:
                html += f'<div class="option answer">Answer: {question.answer}</div>'
            
            if question.explanation:
                html += f'<div class="explanation">Explanation: {question.explanation}</div>'
            
            if question.topic:
                html += f'<div class="topic">Topic: {question.topic}</div>'
            
            html += '</div>'
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def print_quiz_summary(self, quiz: Quiz) -> None:
        """Print a summary of the quiz to console."""
        print(f"\n{'='*60}")
        print(f"QUIZ SUMMARY: {quiz.title}")
        print(f"{'='*60}")
        print(f"Source: {quiz.source}")
        print(f"Total Questions: {quiz.total_questions}")
        print(f"Topics: {', '.join(quiz.topics)}")
        print(f"Difficulty Distribution:")
        for difficulty, count in quiz.difficulty_distribution.items():
            print(f"  - {difficulty.capitalize()}: {count} questions")
        print(f"{'='*60}\n")
        
        for i, question in enumerate(quiz.questions, 1):
            print(f"Question {i} ({question.difficulty.value.upper()}):")
            print(f"Q: {question.question}")
            
            if question.options:
                print("Options:")
                for j, option in enumerate(question.options):
                    marker = "✓" if option == question.answer else " "
                    print(f"  {marker} {chr(65+j)}. {option}")
            else:
                print(f"A: {question.answer}")
            
            if question.explanation:
                print(f"Explanation: {question.explanation}")
            
            if question.topic:
                print(f"Topic: {question.topic}")
            
            print("-" * 40)
