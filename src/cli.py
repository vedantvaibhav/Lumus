"""
Command-line interface for the Self-Quiz Generator Agent.
"""

import os
import sys
import click
from typing import Optional, List
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.orchestrator import QuizGenerator
from src.core.models import SourceType, DifficultyLevel, QuestionType
from src.utils.formatters import QuizFormatter


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Self-Quiz Generator Agent - Generate quizzes from any document or webpage."""
    load_dotenv()


@cli.command()
@click.argument('source')
@click.option('--output', '-o', help='Output file path (without extension)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'csv', 'html', 'anki', 'all']), 
              default='json', help='Output format')
@click.option('--questions', '-q', default=10, help='Number of questions to generate')
@click.option('--difficulty', '-d', 
              type=click.Choice(['easy', 'medium', 'hard']), 
              help='Preferred difficulty level')
@click.option('--types', '-t', 
              type=click.Choice(['multiple-choice', 'short', 'true-false']), 
              multiple=True, help='Question types to generate')
@click.option('--source-type', '-s',
              type=click.Choice(['url', 'pdf', 'text', 'file', 'auto']),
              default='auto', help='Source type (auto-detect if not specified)')
@click.option('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generate(source: str, output: Optional[str], output_format: str, 
             questions: int, difficulty: Optional[str], types: List[str],
             source_type: str, api_key: Optional[str], verbose: bool):
    """Generate a quiz from the specified source."""
    
    # Check API key
    if not api_key and not os.getenv('OPENAI_API_KEY'):
        click.echo("Error: OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key option.", err=True)
        sys.exit(1)
    
    # Initialize components
    generator = QuizGenerator(api_key)
    formatter = QuizFormatter()
    
    # Determine source type
    if source_type == 'auto':
        detected_type = generator.reader_agent.detect_source_type(source)
    else:
        detected_type = SourceType(source_type)
    
    if verbose:
        click.echo(f"Detected source type: {detected_type.value}")
    
    # Prepare request parameters
    difficulty_level = DifficultyLevel(difficulty) if difficulty else None
    question_types = [QuestionType(t) for t in types] if types else None
    
    try:
        # Generate quiz
        click.echo(f"Generating quiz from {detected_type.value} source...")
        from src.core.models import ProcessingRequest
        request = ProcessingRequest(
            source=source,
            source_type=detected_type,
            num_questions=questions,
            difficulty_preference=difficulty_level,
            question_types=question_types
        )
        response = generator.generate_quiz(request)
        
        if not response.success:
            click.echo(f"Error: {response.error}", err=True)
            sys.exit(1)
        
        quiz = response.quiz
        
        if verbose:
            formatter.print_quiz_summary(quiz)
        
        # Export quiz
        if output_format == 'all':
            formats = ['json', 'csv', 'html', 'anki']
        else:
            formats = [output_format]
        
        exported_files = []
        for fmt in formats:
            if output:
                file_path = f"{output}.{fmt}" if fmt != 'anki' else f"{output}_anki.csv"
            else:
                file_path = None
            
            if fmt == 'json':
                exported_file = formatter.export_to_json(quiz, file_path)
            elif fmt == 'csv':
                exported_file = formatter.export_to_csv(quiz, file_path)
            elif fmt == 'html':
                exported_file = formatter.export_to_html(quiz, file_path)
            elif fmt == 'anki':
                exported_file = formatter.export_to_anki(quiz, file_path)
            
            exported_files.append(exported_file)
            click.echo(f"Exported to {exported_file}")
        
        click.echo(f"\nQuiz generation completed successfully!")
        click.echo(f"Generated {quiz.total_questions} questions in {response.processing_time:.2f} seconds")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.option('--questions', '-q', default=10, help='Number of questions to generate')
@click.option('--output', '-o', help='Output file path (without extension)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'csv', 'html', 'anki']), 
              default='json', help='Output format')
def url(url: str, questions: int, output: Optional[str], output_format: str):
    """Generate a quiz from a webpage URL."""
    ctx = click.get_current_context()
    ctx.invoke(generate, source=url, questions=questions, 
               output=output, output_format=output_format, source_type='url')


@cli.command()
@click.argument('file_path')
@click.option('--questions', '-q', default=10, help='Number of questions to generate')
@click.option('--output', '-o', help='Output file path (without extension)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'csv', 'html', 'anki']), 
              default='json', help='Output format')
def pdf(file_path: str, questions: int, output: Optional[str], output_format: str):
    """Generate a quiz from a PDF file."""
    ctx = click.get_current_context()
    ctx.invoke(generate, source=file_path, questions=questions, 
               output=output, output_format=output_format, source_type='pdf')


@cli.command()
@click.argument('file_path')
@click.option('--questions', '-q', default=10, help='Number of questions to generate')
@click.option('--output', '-o', help='Output file path (without extension)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'csv', 'html', 'anki']), 
              default='json', help='Output format')
def file(file_path: str, questions: int, output: Optional[str], output_format: str):
    """Generate a quiz from a text file."""
    ctx = click.get_current_context()
    ctx.invoke(generate, source=file_path, questions=questions, 
               output=output, output_format=output_format, source_type='file')


@cli.command()
def examples():
    """Show usage examples."""
    click.echo("""
Self-Quiz Generator Agent - Usage Examples
==========================================

1. Generate quiz from a webpage:
   quiz-generator url "https://en.wikipedia.org/wiki/Photosynthesis"

2. Generate quiz from a PDF:
   quiz-generator pdf "document.pdf" --questions 15

3. Generate quiz from a text file:
   quiz-generator file "notes.txt" --format html

4. Generate quiz with specific difficulty:
   quiz-generator generate "https://example.com/article" --difficulty hard

5. Generate quiz with specific question types:
   quiz-generator generate "content.pdf" --types multiple-choice --types short

6. Generate quiz in multiple formats:
   quiz-generator generate "source.txt" --format all --output my_quiz

7. Generate quiz with custom output file:
   quiz-generator generate "url" --output "biology_quiz" --format json

8. Verbose output:
   quiz-generator generate "source.pdf" --verbose

Environment Variables:
- OPENAI_API_KEY: Your OpenAI API key (required)

For more information, visit: https://github.com/your-repo/quiz-generator
""")


if __name__ == '__main__':
    cli()
