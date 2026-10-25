
import streamlit as st
from pypdf import PdfReader
from io import BytesIO
import ollama

from ai_engine import get_ai_feedback
from history import save_interview


def extract_resume_text(pdf_file):
    """Extract readable text from an uploaded PDF resume."""

    pdf_bytes = BytesIO(pdf_file.getvalue())
    reader = PdfReader(pdf_bytes)

    resume_text = ""

    for page in reader.pages:
        resume_text += page.extract_text() or ""
        resume_text += "\n"

    return resume_text.strip()


def generate_resume_questions(resume_text):
    """Generate interview questions based on the resume."""

    prompt = f"""
You are an interview coach for students and fresh graduates.

Read the resume text below and create 5 personalized interview
questions based on the candidate's actual skills, projects,
education, and experience.

Rules:
- Use simple English.
- Include questions about projects and skills when available.
- Do not invent skills or experience.
- Include a mix of HR and technical questions where appropriate.
- Return only a numbered list of 5 questions.

RESUME TEXT:
{resume_text[:10000]}
"""

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def show_resume_interview():
    """Display the resume-based interview feature."""

    st.header("📄 Resume-Based Interview")

    st.write(
        "Upload your resume to generate personalized interview "
        "questions and receive AI feedback on your answers."
    )

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=["pdf"],
        key="resume_pdf",
    )

    if uploaded_file is None:
        st.info("Upload a PDF resume to get started.")
        return

    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("Please upload a PDF smaller than 5 MB.")
        return

    # Step 1: Read the uploaded resume
    if st.button(
        "📑 Read My Resume",
        use_container_width=True,
    ):
        try:
            resume_text = extract_resume_text(uploaded_file)

            if not resume_text:
                st.error(
                    "No readable text was found. "
                    "This PDF may be scanned or image-based."
                )
                return

            st.session_state["resume_text"] = resume_text
            st.session_state.pop("resume_questions", None)
            st.session_state.pop("resume_selected_question", None)
            st.session_state.pop("resume_answer", None)

            st.success("Resume text extracted successfully!")

        except Exception as error:
            st.error(
                "Could not read this PDF. Please try another file."
            )
            st.caption(str(error))

    # Step 2: Display extracted resume text
    resume_text = st.session_state.get("resume_text", "")

    if resume_text:
        with st.expander("Preview extracted resume text"):
            st.text(resume_text[:5000])

        # Step 3: Generate personalized questions
        if st.button(
            "🤖 Generate My Interview Questions",
            use_container_width=True,
        ):
            try:
                with st.spinner(
                    "Ollama is preparing your questions..."
                ):
                    questions = generate_resume_questions(
                        resume_text
                    )

                st.session_state["resume_questions"] = questions

                # Reset the previous selection and answer
                st.session_state.pop(
                    "resume_selected_question",
                    None,
                )
                st.session_state.pop("resume_answer", None)

                st.success(
                    "Your personalized questions are ready!"
                )

            except Exception as error:
                st.error(
                    "Could not generate questions. Check that "
                    "Ollama is running and llama3.2:1b is installed."
                )
                st.caption(str(error))

    # Step 4: Display generated questions
    questions = st.session_state.get("resume_questions", "")

    if questions:
        st.divider()
        st.subheader("🎯 Your Personalized Questions")
        st.markdown(questions)

        # Extract numbered questions from the AI response
        question_list = [
            line.strip()
            for line in questions.splitlines()
            if line.strip()
            and line.strip()[0].isdigit()
            and "." in line.strip()
        ]

        if question_list:
            selected_question = st.selectbox(
                "Choose a question to answer",
                question_list,
                key="resume_selected_question",
            )

            answer = st.text_area(
                "Write your answer",
                key="resume_answer",
                height=180,
                placeholder="Write your interview answer here...",
            )

            # Step 5: Get feedback and save the interview
           
            if st.button(
                "💬 Get AI Feedback",
                use_container_width=True,
            ):
                if not answer.strip():
                    st.warning("Please write your answer first.")

                else:
                    # First, get AI feedback
                    try:
                        with st.spinner("Reviewing your answer..."):
                            feedback = get_ai_feedback(
                                selected_question,
                                answer,
                            )

                        st.success("AI feedback generated successfully!")
                        st.subheader("📝 AI Feedback")
                        st.markdown(feedback)

                    except Exception as error:
                        st.error("AI feedback failed.")
                        st.exception(error)

                        # Stop here if AI feedback failed
                        st.stop()

                    # Second, save the interview
                    try:
                        save_interview(
                            category="Resume-Based Interview",
                            question=selected_question,
                            answer=answer,
                            feedback=feedback,
                            score=None,
                        )

                        st.success(
                            "Resume interview saved successfully!"
                        )

                    except Exception as error:
                        st.error("Database save failed.")
                        st.exception(error)


        else:
            st.warning(
                "The AI response did not contain numbered questions "
                "in the expected format. Please generate the questions "
                "again."
            )
