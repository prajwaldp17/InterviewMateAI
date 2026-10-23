
import ollama


def get_ai_feedback(question, answer):
    prompt = f"""
You are a friendly job interview coach.

Interview question:
{question}

Candidate's answer:
{answer}

Review the answer using these sections:

1. What the candidate did well
2. What is missing or unclear
3. How to improve the answer
4. An improved example answer

Use simple English and give practical advice.
Do not invent qualifications or work experience.
"""

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
