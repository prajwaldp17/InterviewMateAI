import streamlit as st
import pandas as pd
import csv
import io
from resume_interview import show_resume_interview

from ai_engine import get_ai_feedback
from feedback import (
    count_words,
    check_keywords,
    calculate_score,
    give_suggestions,
)
from history import init_db, save_interview, get_history


# -------------------------
# 1. Page setup
# -------------------------

st.set_page_config(
    page_title="InterviewMate AI",
    page_icon="🎯",
    layout="wide",
)

init_db()

# -------------------------
# Purple futuristic UI theme
# -------------------------

st.markdown("""
<style>

/* Main application background */
.stApp {
    background: linear-gradient(
        135deg,
        #100B20 0%,
        #17102B 45%,
        #100B20 100%
    );
    color: #F5F3FF;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Main headings */
h1, h2, h3 {
    color: #F5F3FF !important;
    letter-spacing: -0.5px;
}

/* Paragraphs and labels */
p, label, .stMarkdown {
    color: #DDD6FE;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1C1233 0%,
        #120D24 100%
    );
    border-right: 1px solid #39245E;
}

section[data-testid="stSidebar"] h1 {
    color: #C4B5FD !important;
}

/* Sidebar radio navigation */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #211637;
    border: 1px solid #39245E;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #352052;
    border-color: #8B5CF6;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #26183F,
        #1B1230
    );
    border: 1px solid #49316D;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
}

div[data-testid="stMetricLabel"] {
    color: #C4B5FD !important;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
    background: linear-gradient(
        100deg,
        #7C3AED,
        #A855F7
    );
    color: #FFFFFF !important;
    border: 1px solid #A78BFA;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {
    background: linear-gradient(
        100deg,
        #6D28D9,
        #9333EA
    );
    border-color: #DDD6FE;
    box-shadow: 0 0 18px rgba(168, 85, 247, 0.25);
}

/* Text input areas */
.stTextArea textarea,
.stTextInput input {
    background-color: #1B1230 !important;
    color: #F5F3FF !important;
    border: 1px solid #49316D !important;
    border-radius: 10px !important;
}

/* Dropdowns */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #211637;
    border-color: #49316D;
    border-radius: 10px;
    color: #FFFFFF;
}

/* Interview history expanders */
div[data-testid="stExpander"] {
    background-color: #1B1230;
    border: 1px solid #49316D;
    border-radius: 12px;
    overflow: hidden;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(
        90deg,
        #7C3AED,
        #C084FC
    );
}

/* Horizontal dividers */
hr {
    border-color: #39245E;
}

/* Info and success messages */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Charts and tables */
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    border: 1px solid #49316D;
    border-radius: 12px;
    overflow: hidden;
}

/* Links */
a {
    color: #C4B5FD !important;
}

/* Small footer-style captions */
.stCaption {
    color: #A78BFA !important;
}

/* Mobile-friendly spacing */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    div[data-testid="stMetric"] {
        padding: 12px;
    }
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# 2. Interview question bank
# -------------------------

question_bank = {
    "HR Interview": {
        "Tell me about yourself.": {
            "keywords": ["education", "skills", "experience", "goals"],
            "sample": (
                "I am a Computer Science graduate with knowledge "
                "of programming and problem-solving. I enjoy learning "
                "new skills and want to grow professionally."
            ),
        },
        "Why should we hire you?": {
            "keywords": ["skills", "learning", "teamwork", "contribute"],
            "sample": (
                "You should hire me because I am willing to learn, "
                "work with a team, and use my skills to contribute "
                "to the company's goals."
            ),
        },
    },
    "Python Interview": {
        "What is Python?": {
            "keywords": ["programming", "language", "readable", "code"],
            "sample": (
                "Python is a high-level programming language known "
                "for readable code. It is used in automation, data "
                "analysis, web development, and AI."
            ),
        },
        "What is a variable in Python?": {
            "keywords": ["store", "value", "name", "data"],
            "sample": (
                "A variable is a name that refers to a value. "
                "For example, age = 22 stores the value 22 under "
                "the variable name age."
            ),
        },
    },
    "Customer Support": {
        "How would you handle an angry customer?": {
            "keywords": ["listen", "empathy", "understand", "solution"],
            "sample": (
                "I would listen carefully, show empathy, understand "
                "the customer's issue, and work toward a suitable "
                "solution while communicating clearly."
            ),
        },
    },
}


# -------------------------
# 3. Sidebar navigation
# -------------------------

st.title("🎯 InterviewMate AI")
st.caption("Your personal AI-powered interview practice workspace")

with st.sidebar:
    st.title("🎯 InterviewMate AI")
    st.write("Your Interview Coach")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🎤 Practice Interview",
            "📄 Resume Interview",
            "📚 Interview History",
            "📈 Progress & Reports",
        ],
        label_visibility="visible",
        key="nav_page",
    )

    st.divider()
    st.caption("Practice. Learn. Improve.")


# Load saved interviews

interview_history = get_history()

scored_interviews = [
    record for record in interview_history
    if record[5] is not None
]

average_score = (
    sum(float(record[5]) for record in scored_interviews)
    / len(scored_interviews)
    if scored_interviews
    else None
)

# -------------------------
# 4. Dashboard page
# -------------------------

if page == "🏠 Dashboard":

    # Welcome banner
    st.markdown(
        """
        <div style="
            background: linear-gradient(120deg, #4C1D95, #7C3AED, #A855F7);
            padding: 30px;
            border-radius: 18px;
            margin-bottom: 25px;
            border: 1px solid #A78BFA;
        ">
            <h1 style="color: white; margin-bottom: 10px;">
                Welcome to InterviewMate AI 🎯
            </h1>
            <p style="color: #F3E8FF; font-size: 17px;">
                Your personal AI interview coach.
                Practice smarter, improve your answers,
                and track your interview preparation.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Dashboard statistics
    st.subheader("📊 Your Interview Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="📝 Total Reviews",
            value=len(interview_history)
        )

    with col2:
        st.metric(
            label="🎯 Scored Reviews",
            value=len(scored_interviews)
        )

    with col3:
        st.metric(
            label="⭐ Average Score",
            value=(
                f"{average_score:.1f}/10"
                if average_score is not None
                else "N/A"
            )
        )

    st.divider()

    # Quick actions
    st.subheader("🚀 Quick Actions")
    st.write("Choose what you want to work on today.")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        with st.container(border=True):
            st.markdown("### 🎤 Practice Interview")
            st.write(
                "Answer HR, Python, and customer support "
                "questions and receive feedback."
            )

            if st.button(
                "Start Practicing →",
                key="dashboard_practice",
                use_container_width=True
            ):
                st.session_state["nav_page"] = "🎤 Practice Interview"
                st.rerun()

    with action_col2:
        with st.container(border=True):
            st.markdown("### 📈 Progress & Reports")
            st.write(
                "Review your saved scores, track your progress, "
                "and download your interview report."
            )

            if st.button(
                "View My Progress →",
                key="dashboard_progress",
                use_container_width=True
            ):
                st.session_state["nav_page"] = "📈 Progress & Reports"
                st.rerun()

    st.divider()

    # Recent interview activity
    st.subheader("🕘 Recent Interview Activity")

    if interview_history:

        # Show the three most recent reviews
        recent_interviews = interview_history[:3]

        for record in recent_interviews:

            (
                interview_id,
                saved_category,
                saved_question,
                saved_answer,
                saved_feedback,
                saved_score,
                created_at
            ) = record

            with st.container(border=True):

                review_col1, review_col2 = st.columns([3, 1])

                with review_col1:
                    st.markdown(f"**{saved_question}**")
                    st.caption(
                        f"{saved_category} • {created_at}"
                    )

                with review_col2:
                    if saved_score is not None:
                        st.metric(
                            "Score",
                            f"{float(saved_score):.1f}/10"
                        )
                    else:
                        st.caption("Score unavailable")

                with st.expander("View answer and AI feedback"):

                    st.markdown("**Your answer**")
                    st.write(saved_answer)

                    st.markdown("**AI feedback**")
                    st.write(saved_feedback)

        if st.button(
            "View Full Interview History →",
            key="dashboard_history",
            use_container_width=True
        ):
            st.session_state["nav_page"] = "📚 Interview History"
            st.rerun()

    else:

        st.info(
            "You haven't saved any interview reviews yet. "
            "Start your first practice session to see your "
            "activity here."
        )

        if st.button(
            "Start Your First Interview →",
            key="dashboard_first_practice",
            use_container_width=True
        ):
            st.session_state["nav_page"] = "🎤 Practice Interview"
            st.rerun()

    # Footer
    st.divider()

    st.caption(
        "💜 InterviewMate AI | Practice. Learn. Improve."
    )

# -------------------------
# 5. Practice Interview page
# -------------------------

elif page == "🎤 Practice Interview":

    st.header("🎤 Practice Interview")

    st.write(
        "Choose a category, answer a question, and receive feedback."
    )

    category = st.selectbox(
        "Choose your interview type",
        list(question_bank.keys()),
        key="practice_category",
    )

    question = st.selectbox(
        "Choose a question",
        list(question_bank[category].keys()),
        key="practice_question",
    )

    st.subheader("Your interview question")
    st.info(question)

    answer = st.text_area(
        "Type your answer below",
        placeholder="Write your interview answer here...",
        height=180,
        key="practice_answer",
    )

    # Basic answer review

    st.divider()
    st.subheader("📊 Basic Interview Review")

    if st.button(
        "Review My Answer",
        use_container_width=True,
    ):

        if not answer.strip():

            st.warning("Please enter your answer first.")

        else:

            word_count = count_words(answer)

            keywords = question_bank[category][question]["keywords"]

            matched, missing = check_keywords(
                answer,
                keywords,
            )

            total_score, length_score, keyword_score = calculate_score(
                word_count,
                len(matched),
                len(keywords),
            )

            suggestions = give_suggestions(
                word_count,
                missing,
            )

            st.subheader("Your Results")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Score",
                f"{total_score}/10",
            )

            col2.metric(
                "Word Count",
                word_count,
            )

            col3.metric(
                "Keywords Matched",
                f"{len(matched)}/{len(keywords)}",
            )

            st.write(
                f"**Answer length score:** {length_score}/5"
            )

            st.write(
                f"**Keyword score:** {keyword_score}/5"
            )

            st.progress(
                max(
                    0.0,
                    min(1.0, float(total_score) / 10),
                )
            )

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
                st.write(f"- {suggestion}")

            st.subheader("📝 Sample Answer")

            st.write(
                question_bank[category][question]["sample"]
            )

            st.caption(
                "This score uses simple rules and keyword matching. "
                "It does not measure factual correctness, communication "
                "quality, or the full meaning of your answer."
            )

            # Save score temporarily for matching AI review

            st.session_state["latest_basic_review"] = {
                "category": category,
                "question": question,
                "answer": answer,
                "score": total_score,
            }

    # AI feedback section

    st.divider()
    st.subheader("🤖 AI-Powered Interview Feedback")

    with st.form("ai_feedback_form"):

        get_ai = st.form_submit_button(
            "Get Detailed AI Feedback",
            use_container_width=True,
        )

    if get_ai:

        if not answer.strip():

            st.warning("Please enter your answer first.")

        else:

            with st.spinner("AI is reviewing your answer..."):

                try:

                    ai_feedback = get_ai_feedback(
                        question,
                        answer,
                    )

                    st.markdown(ai_feedback)

                    # Match the score to the same answer

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

                    # Save AI review to SQLite database

                    save_interview(
                        category=category,
                        question=question,
                        answer=answer,
                        feedback=ai_feedback,
                        score=score_to_save,
                    )

                    st.success(
                        "Interview review saved to your history!"
                    )

                except Exception as error:

                    st.error(
                        "AI feedback failed. Check that Ollama is running "
                        "and the model is installed."
                    )

                    st.caption(str(error))


# -------------------------
# 6. Interview History page
# -------------------------

elif page == "📚 Interview History":

    st.header("📚 Interview History")

    interview_history = get_history()

    if not interview_history:

        st.info(
            "No interview history yet. "
            "Complete your first AI review to see it here."
        )

    else:

        st.write(
            f"Total saved interviews: {len(interview_history)}"
        )

        for record in interview_history:

            (
                interview_id,
                saved_category,
                saved_question,
                saved_answer,
                saved_feedback,
                saved_score,
                created_at,
            ) = record

            with st.expander(
                f"{saved_category} | {saved_question} | {created_at}"
            ):

                st.markdown("**Your answer**")
                st.write(saved_answer)

                st.markdown("**AI feedback**")
                st.write(saved_feedback)

                if saved_score is not None:

                    st.write(
                        f"**Basic review score:** {saved_score}/10"
                    )

                else:

                    st.caption(
                        "No basic score was saved for this review."
                    )

        # CSV download

        st.divider()
        st.subheader("📥 Download Interview History")

        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)

        csv_writer.writerow(
            [
                "Interview ID",
                "Category",
                "Question",
                "Your Answer",
                "AI Feedback",
                "Score",
                "Date",
            ]
        )

        for record in interview_history:
            csv_writer.writerow(record)

        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv_buffer.getvalue(),
            file_name="interviewmate_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.caption(
            "The report includes saved questions, answers, AI feedback, "
            "scores when available, and timestamps."
        )


# -------------------------
# 7. Progress & Reports page
# -------------------------

elif page == "📈 Progress & Reports":

    st.header("📈 Progress & Reports")

    interview_history = get_history()

    scored_interviews = [
        record for record in interview_history
        if record[5] is not None
    ]

    average_score = (
        sum(float(record[5]) for record in scored_interviews)
        / len(scored_interviews)
        if scored_interviews
        else None
    )

    # Summary metrics

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total AI Reviews",
        len(interview_history),
    )

    col2.metric(
        "Scored Reviews",
        len(scored_interviews),
    )

    col3.metric(
        "Average Score",
        (
            f"{average_score:.1f}/10"
            if average_score is not None
            else "Not available"
        ),
    )

    # Score chart

    st.divider()
    st.subheader("📈 Score Improvement Over Time")

    if scored_interviews:

        chart_data = []

        # Database results are newest first.
        # Reverse them to show oldest to newest.

        for attempt_number, record in enumerate(
            reversed(scored_interviews),
            start=1,
        ):

            chart_data.append(
                {
                    "Attempt": attempt_number,
                    "Score": float(record[5]),
                    "Question": record[2],
                    "Date": record[6],
                }
            )

        df = pd.DataFrame(chart_data)

        st.line_chart(
            df,
            x="Attempt",
            y="Score",
        )

        st.caption(
            "Each point represents a saved numeric score, "
            "ordered from oldest to newest."
        )

    else:

        st.info(
            "No scored interviews are available yet. On the Practice "
            "Interview page, use 'Review My Answer' first, then request "
            "AI feedback for the same answer."
        )

    # Category chart

    st.divider()
    st.subheader("📊 Practice by Interview Category")

    if interview_history:

        category_data = pd.DataFrame(
            [
                {"Category": record[1]}
                for record in interview_history
            ]
        )

        category_counts = (
            category_data["Category"]
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Attempts")
        )

        st.bar_chart(
            category_counts,
            x="Category",
            y="Attempts",
        )

    else:

        st.info(
            "Your category chart will appear after you save "
            "your first interview review."
        )

    # CSV export

    st.divider()
    st.subheader("📥 Export your report")

    if interview_history:

        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)

        csv_writer.writerow(
            [
                "Interview ID",
                "Category",
                "Question",
                "Your Answer",
                "AI Feedback",
                "Score",
                "Date",
            ]
        )

        for record in interview_history:
            csv_writer.writerow(record)

        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv_buffer.getvalue(),
            file_name="interviewmate_history.csv",
            mime="text/csv",
        )

    else:

        st.info(
            "Complete an AI review before exporting a report."
        )
        
elif page == "📄 Resume Interview":
    show_resume_interview()