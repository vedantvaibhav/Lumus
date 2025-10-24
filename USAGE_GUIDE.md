# Self-Quiz Generator Agent - Complete Usage Guide

## 🚀 Quick Start

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
# OR create a .env file with: OPENAI_API_KEY=your-api-key-here
```

### 2. Basic Usage

#### Command Line Interface
```bash
# Generate quiz from a webpage
python main.py url "https://en.wikipedia.org/wiki/Photosynthesis"

# Generate quiz from PDF
python main.py pdf "document.pdf" --questions 15

# Generate quiz from text file
python main.py file "notes.txt" --format html

# Generate quiz with specific difficulty
python main.py generate "https://example.com/article" --difficulty hard

# Generate quiz in multiple formats
python main.py generate "source.txt" --format all --output my_quiz
```

#### Python API
```python
from src.core.orchestrator import QuizGenerator
from src.core.models import DifficultyLevel, QuestionType

# Initialize generator
generator = QuizGenerator()

# Generate from URL
response = generator.generate_from_url(
    url="https://example.com/article",
    num_questions=10,
    difficulty=DifficultyLevel.MEDIUM
)

# Generate from PDF
response = generator.generate_from_pdf("document.pdf", num_questions=15)

# Generate from text
response = generator.generate_from_text("Your text content here...")

if response.success:
    quiz = response.quiz
    print(f"Generated {quiz.total_questions} questions")
    for question in quiz.questions:
        print(f"Q: {question.question}")
        print(f"A: {question.answer}")
```

## 📋 Features

### Supported Sources
- **Web Pages**: Any URL (Wikipedia, articles, blogs, etc.)
- **PDF Files**: Academic papers, textbooks, documents
- **Text Files**: Notes, articles, any plain text
- **Direct Text**: Paste content directly

### Question Types
- **Multiple Choice**: 4 options with one correct answer
- **Short Answer**: Open-ended questions
- **True/False**: Simple true/false statements

### Difficulty Levels
- **Easy**: Basic facts and definitions
- **Medium**: Application and understanding
- **Hard**: Analysis, synthesis, and critical thinking

### Export Formats
- **JSON**: Structured data format
- **CSV**: Spreadsheet-compatible format
- **HTML**: Interactive web page
- **Anki**: Flashcard format for spaced repetition

## 🎯 Advanced Usage

### Custom Question Types
```bash
python main.py generate "source.pdf" --types multiple-choice --types short
```

### Specific Difficulty
```bash
python main.py generate "source.txt" --difficulty hard --questions 20
```

### Multiple Export Formats
```bash
python main.py generate "source.pdf" --format all --output biology_quiz
```

### Verbose Output
```bash
python main.py generate "source.txt" --verbose
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
OPENAI_MODEL=gpt-4o-mini  # Default model
REQUEST_TIMEOUT=30         # Request timeout in seconds
```

### API Key Setup
1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set environment variable: `export OPENAI_API_KEY="sk-..."`
3. Or create `.env` file with your key

## 📊 Output Examples

### JSON Format
```json
{
  "title": "Photosynthesis Quiz",
  "source": "https://en.wikipedia.org/wiki/Photosynthesis",
  "total_questions": 10,
  "difficulty_distribution": {
    "easy": 3,
    "medium": 5,
    "hard": 2
  },
  "topics": ["Chloroplasts", "Light Reactions", "Calvin Cycle"],
  "questions": [
    {
      "question": "What is the main pigment in photosynthesis?",
      "answer": "Chlorophyll",
      "type": "multiple-choice",
      "difficulty": "easy",
      "options": ["Chlorophyll", "Carotene", "Xanthophyll", "Anthocyanin"],
      "explanation": "Chlorophyll is the primary pigment that captures light energy.",
      "topic": "Photosynthesis Basics"
    }
  ]
}
```

### HTML Output
- Interactive web page with styled questions
- Color-coded difficulty levels
- Explanations and topics
- Responsive design

### CSV Format
- Spreadsheet-compatible
- All question data in columns
- Easy to import into other tools

### Anki Format
- Front/Back card format
- Tags for organization
- Ready for spaced repetition

## 🎮 Demo

Run the demo to see all features in action:
```bash
python demo.py
```

The demo will:
1. Generate a quiz from sample text
2. Show URL-based generation
3. Demonstrate multiple export formats
4. Display quiz summaries and statistics

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: OpenAI API key is required
   ```
   Solution: Set `OPENAI_API_KEY` environment variable

2. **Network Issues**
   ```
   Failed to read URL: Connection timeout
   ```
   Solution: Check internet connection and URL validity

3. **PDF Reading Error**
   ```
   Failed to read PDF: File not found
   ```
   Solution: Ensure PDF file exists and is readable

4. **Insufficient Content**
   ```
   Insufficient content to generate meaningful quiz questions
   ```
   Solution: Use longer text content or different source

### Performance Tips

1. **Large Documents**: For very large PDFs, consider splitting into sections
2. **API Limits**: Be mindful of OpenAI API rate limits and costs
3. **Question Count**: More questions = longer processing time
4. **Model Choice**: `gpt-4o-mini` is cost-effective for most use cases

## 🔮 Extensions & Customization

### Custom Question Types
Extend the system by adding new question types in `src/core/models.py`:
```python
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple-choice"
    SHORT_ANSWER = "short"
    TRUE_FALSE = "true-false"
    FILL_IN_BLANK = "fill-blank"  # New type
```

### Custom Export Formats
Add new formatters in `src/utils/formatters.py`:
```python
def export_to_markdown(self, quiz: Quiz, file_path: str) -> str:
    # Custom markdown export
    pass
```

### Integration Examples
- **Learning Management Systems**: Export quizzes to LMS platforms
- **Study Apps**: Integrate with flashcard applications
- **Educational Tools**: Build custom learning interfaces

## 📈 Future Enhancements

1. **Adaptive Difficulty**: Adjust difficulty based on user performance
2. **Topic Clustering**: Group questions by subject areas
3. **Spaced Repetition**: Track user performance over time
4. **Voice Interface**: Audio quiz generation and playback
5. **Multi-language**: Support for different languages
6. **Browser Extension**: Generate quizzes from any webpage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Learning! 🎓**

For more information, visit the project repository or run `python main.py --help` for command-line options.
