
import streamlit as st

from ai_engine import get_ai_feedback
from feedback import (
    count_words,
    check_keywords,
    calculate_score,
    give_suggestions
)
from history import init_db, save_interview, get_history

# -------------------------
# 1. Page setup
# -------------------------

st.set_page_config(
    page_title="InterviewMate AI",
    page_icon="🎯"
)

init_db()

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
# 3. Select interview question
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
# 4. Rule-based answer review
# -------------------------

st.divider()
st.subheader("📊 Basic Interview Review")

if st.button("Review My Answer"):
    if not answer.strip():
        st.warning("Please enter your answer first.")
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

        st.subheader("Your Results")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Score", f"{total_score}/10")
        col2.metric("Word Count", word_count)
        col3.metric(
            "Keywords Matched",
            f"{len(matched)}/{len(keywords)}"
        )

        st.write(f"**Answer length score:** {length_score}/5")
        st.write(f"**Keyword score:** {keyword_score}/5")

        st.progress(max(0.0, min(1.0, total_score / 10)))

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

        # Save the rule-based score for progress tracking.
        st.session_state["latest_basic_review"] = {
            "category": category,
            "question": question,
            "answer": answer,
            "score": total_score
        }

# -------------------------
# 5. AI-powered feedback
# -------------------------

st.divider()
st.subheader("🤖 AI-Powered Interview Feedback")

with st.form("ai_feedback_form"):
    get_ai = st.form_submit_button("Get Detailed AI Feedback")

if get_ai:
    if not answer.strip():
        st.warning("Please enter your answer first.")
    else:
        with st.spinner("AI is reviewing your answer..."):
            try:
                ai_feedback = get_ai_feedback(question, answer)

                st.markdown(ai_feedback)

                # Use the latest basic score only when it belongs
                # to the same category, question, and answer.
                latest_review = st.session_state.get(
                    "latest_basic_review"
                )

                score_to_save = None

                if (
                    latest_review
                    and latest_review["category"] == category
                    and latest_review["question"] == question
                    and latest_review["answer"] == answer
                ):
                    score_to_save = latest_review["score"]

                save_interview(
                    category=category,
                    question=question,
                    answer=answer,
                    feedback=ai_feedback,
                    score=score_to_save
                )

                st.success("Interview review saved to your history!")

            except Exception as error:
                st.error(
                    "AI feedback failed. Check that Ollama is running "
                    "and the model is installed."
                )
                st.caption(str(error))

# -------------------------
# 6. Interview history
# -------------------------

st.divider()
st.header("📚 Interview History")

interview_history = get_history()

if not interview_history:
    st.info(
        "No interview history yet. "
        "Complete your first AI review to see it here."
    )
else:
    st.write(f"Total saved interviews: {len(interview_history)}")

    for record in interview_history:
        (
            interview_id,
            saved_category,
            saved_question,
            saved_answer,
            saved_feedback,
            saved_score,
            created_at
        ) = record

        with st.expander(
            f"{saved_category} | {saved_question} | {created_at}"
        ):
            st.markdown("**Your answer**")
            st.write(saved_answer)

            st.markdown("**AI feedback**")
            st.write(saved_feedback)

            if saved_score is not None:
                st.write(f"**Basic review score:** {saved_score}/10")

# -------------------------
# 7. Progress tracking
# -------------------------

st.divider()
st.header("📈 Your Progress")

total_interviews = len(interview_history)

scored_interviews = [
    record
    for record in interview_history
    if record[5] is not None
]

average_score = (
    sum(record[5] for record in scored_interviews)
    / len(scored_interviews)
    if scored_interviews
    else None
)

col1, col2, col3 = st.columns(3)

col1.metric("Total AI Reviews", total_interviews)
col2.metric("Reviews With Scores", len(scored_interviews))

if average_score is not None:
    col3.metric("Average Basic Score", f"{average_score:.1f}/10")
else:
    col3.metric("Average Basic Score", "Not available")

st.caption(
    "Progress scores come from your rule-based review out of 10. "
    "AI feedback is stored separately and is not automatically scored."
)
