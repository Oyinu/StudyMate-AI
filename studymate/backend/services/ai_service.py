import os
import json
print("DEBUG KEY:", os.getenv("GEMINI_API_KEY"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_questions(text: str, difficulty: str, num_mcq: int, num_theory: int) -> dict:
    """
    Generate quiz questions from extracted PDF text using Gemini API.
    """
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )

    if not text or len(text.strip()) < 100:
        raise ValueError(
            "Extracted PDF text is too short or empty. Cannot generate questions."
        )

    return _generate_with_gemini(text, difficulty, num_mcq, num_theory)


def _generate_with_gemini(text: str, difficulty: str, num_mcq: int, num_theory: int) -> dict:
    """Generate questions using Google Gemini API."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-3-flash-preview")

        # Truncate text to avoid token limits (keep first 8000 chars)
        truncated = text[:8000] if len(text) > 8000 else text

        prompt = f"""You are an expert academic question generator.

From the study material below, generate:
- {num_mcq} multiple choice questions (MCQs) with 4 options each
- {num_theory} theory/short-answer questions
- Difficulty level: {difficulty}

Rules:
- MCQs must have exactly 4 options labeled A, B, C, D
- The answer field must be just the letter: A, B, C, or D
- Theory questions must include a detailed model answer
- Questions MUST be directly based ONLY on the provided text below
- Do NOT generate questions from general knowledge — only from the text
- Do NOT include question numbers in the question text

Return ONLY valid JSON in exactly this format, no extra text before or after:
{{
  "mcq": [
    {{
      "question": "Question text here?",
      "options": ["A. Option one", "B. Option two", "C. Option three", "D. Option four"],
      "answer": "A"
    }}
  ],
  "theory": [
    {{
      "question": "Theory question here?",
      "model_answer": "Detailed model answer here."
    }}
  ]
}}

Study Material:
{truncated}"""

        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        questions = json.loads(raw)

        # Validate structure
        if "mcq" not in questions or "theory" not in questions:
            raise ValueError(f"Gemini returned unexpected JSON structure: {list(questions.keys())}")

        # Validate counts
        if len(questions["mcq"]) == 0 and num_mcq > 0:
            raise ValueError("Gemini returned 0 MCQ questions.")

        return questions

    except json.JSONDecodeError as e:
        print(f"JSON parse error from Gemini response: {e}")
        print(f"Raw response was: {raw[:500]}")
        return None

    except Exception as e:
        print(f"Gemini API error: {e}")
        return None
    except Exception as e:
       import traceback
       traceback.print_exc()
       return None