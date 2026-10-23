
from ai_engine import get_ai_feedback

question = "Tell me about yourself."

answer = (
    "I am a B.Tech Computer Science graduate. "
    "I am learning Python and looking for an opportunity "
    "to improve my technical skills."
)

feedback = get_ai_feedback(question, answer)

print("\n--- AI INTERVIEW FEEDBACK ---\n")
print(feedback)
