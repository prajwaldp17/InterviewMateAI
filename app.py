
import streamlit as st
from ai_engine import get_ai_feedback

# -------------------------
# 1. Page setup
# -------------------------

from feedback import (
    count_words,
    check_keywords,
    calculate_score,
    give_suggestions
)

st.set_page_config(
    page_title="InterviewMate AI",
    page_icon="🎯"
)

st.title("🎯 InterviewMate AI")
st.write("Practice interviews and improve your answers.")

# -------------------------
# 2. Interview question bank
# -------------------------

question_bank = {
    "HR Interview": {
        "Tell me about yourself.": {
            "keywords": [
                "education", "skills", "experience", "goals"
            ],
            "sample": (
                "I am a Computer Science graduate with knowledge "
                "of programming and problem-solving. I enjoy learning "
                "new skills and want to grow professionally."
            )
        },
        "Why should we hire you?": {
            "keywords": [
                "skills", "learning", "teamwork", "contribute"
            ],
            "sample": (
                "You should hire me because I am willing to learn, "
                "work with a team, and use my skills to contribute "
                "to the company's goals."
            )
        }
    },
    "Python Interview": {
        "What is Python?": {
            "keywords": [
                "programming", "language", "readable", "code"
            ],
            "sample": (
                "Python is a high-level programming language known "
                "for readable code. It is used in automation, data "
                "analysis, web development, and AI."
            )
        },
        "What is a variable in Python?": {
            "keywords": [
                "store", "value", "name", "data"
            ],
            "sample": (
                "A variable is a name that refers to a value. "
                "For example, age = 22 stores the value 22 under "
                "the variable name age."
            )
        }
    },
    "Customer Support": {
        "How would you handle an angry customer?": {
            "keywords": [
                "listen", "empathy", "understand", "solution"
            ],
            "sample": (
                "I would listen carefully, show empathy, understand "
                "the customer's issue, and work toward a suitable "
                "solution while communicating clearly."
            )
        }
    }
}


# -------------------------
# 7. User interface
# -------------------------

category = st.selectbox(
    "Choose your interview type",
    list(question_bank.keys())
)

question = st.selectbox(
    "Choose a question",
    list(question_bank[category].keys())
)

st.subheader("Your interview question")
st.write(question)

answer = st.text_area(
    "Type your answer below",
    placeholder="Write your interview answer here..."
)

# -------------------------
# 8. Review the answer
# -------------------------

st.divider()

st.subheader("🤖 AI-Powered Interview Feedback")

with st.form("ai_feedback_form"):
    get_ai = st.form_submit_button(
        "Get Detailed AI Feedback"
    )

if get_ai:
    if not answer.strip():
        st.warning("Please enter your answer first.")
    else:
        with st.spinner("AI is reviewing your answer..."):
            try:
                ai_feedback = get_ai_feedback(
                    question,
                    answer
                )
                st.markdown(ai_feedback)

            except Exception as error:
                st.error(
                    "AI feedback failed. Check that Ollama "
                    "is running and the model is installed."
                )
                st.caption(str(error))


if st.button("Review My Answer"):

    if not answer.strip():
        st.warning("Please enter an answer first.")

    else:
        word_count = count_words(answer)

        keywords = question_bank[category][question]["keywords"]

        matched, missing = check_keywords(answer, keywords)

        total_score, length_score, keyword_score = calculate_score(
            word_count,
            len(matched),
            len(keywords)
        )

        suggestions = give_suggestions(word_count, missing)

        st.subheader("📊 Your Feedback")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Score", f"{total_score}/10")
        col2.metric("Word Count", word_count)
        col3.metric("Keywords Matched", f"{len(matched)}/{len(keywords)}")

        st.write(f"**Answer length score:** {length_score}/5")
        st.write(f"**Keyword score:** {keyword_score}/5")

        st.progress(total_score / 10)

        st.subheader("✅ Concepts Found")

        if matched:
            st.write(", ".join(matched))
        else:
            st.write("No expected keywords found.")

        st.subheader("📌 Concepts to Improve")

        if missing:
            st.write(", ".join(missing))
        else:
            st.write("All expected keywords were found.")

        st.subheader("💡 Suggestions")

        for suggestion in suggestions:
            st.write("- " + suggestion)

        st.subheader("📝 Sample Answer")

        st.write(question_bank[category][question]["sample"])

        st.caption(
            "This score uses simple rules and keyword matching. "
            "It does not measure factual correctness, communication "
            "quality, or the full meaning of your answer."
        )
