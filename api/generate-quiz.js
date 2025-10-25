const https = require('https');

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const { api_key, topic, num_questions = 10 } = req.body;

    if (!api_key) {
      res.status(400).json({ error: 'API key is required' });
      return;
    }

    if (!topic) {
      res.status(400).json({ error: 'Topic is required' });
      return;
    }

    // Call Google Gemini API directly
    const quiz = await generateQuizWithGemini(api_key, topic, num_questions);
    
    res.status(200).json(quiz);
  } catch (error) {
    console.error('Error generating quiz:', error);
    res.status(500).json({ error: `Failed to generate quiz: ${error.message}` });
  }
}

async function generateQuizWithGemini(apiKey, topic, numQuestions) {
  const prompt = `You are an expert educational quiz generator. Create a high-quality quiz about "${topic}" with exactly ${numQuestions} questions.

STRICT REQUIREMENTS:
1. Generate exactly ${numQuestions} questions
2. Use ONLY multiple-choice (4 options) and true/false questions
3. Mix question types: 60% multiple-choice, 40% true/false
4. Include easy, medium, and hard questions
5. Each question must have a clear explanation
6. Questions MUST test understanding, not just memorization
7. Focus on IMPORTANT concepts

Format as JSON:
{
  "title": "Quiz Title",
  "total_questions": ${numQuestions},
  "questions": [
    {
      "question": "Question text?",
      "type": "multiple-choice",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "answer": "A) Option 1",
      "explanation": "Why this answer is correct",
      "difficulty": "easy|medium|hard"
    },
    {
      "question": "True or False statement?",
      "type": "true-false",
      "answer": "True|False",
      "explanation": "Why this answer is correct",
      "difficulty": "easy|medium|hard"
    }
  ]
}

Make sure all questions are relevant to the topic and educational.`;

  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [{
        parts: [{
          text: prompt
        }]
      }],
      generationConfig: {
        temperature: 0.4,
        maxOutputTokens: 6000,
      }
    })
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  
  if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
    throw new Error('Invalid response from API');
  }

  const quizText = data.candidates[0].content.parts[0].text;
  
  // Clean up the response (remove markdown formatting if present)
  let cleanText = quizText.trim();
  if (cleanText.startsWith('```json')) {
    cleanText = cleanText.substring(7);
  }
  if (cleanText.endsWith('```')) {
    cleanText = cleanText.substring(0, cleanText.length - 3);
  }

  const quiz = JSON.parse(cleanText);
  
  // Add metadata
  quiz.source = `AI analysis of ${topic}`;
  quiz.generated_at = new Date().toISOString();
  
  return quiz;
}
