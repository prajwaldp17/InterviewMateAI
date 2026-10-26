import streamlit as st
import speech_recognition as sr
import io
import json
import streamlit.components.v1 as components

from ai_engine import get_ai_feedback
from history import save_interview


# Interview questions
VOICE_QUESTIONS = [
    "Tell me about yourself.",
    "Why should we hire you?",
    "What are your strengths and weaknesses?",
    "Explain a project you have worked on.",
    "Where do you see yourself in five years?",
    "Why do you want to become a Data Analyst?",
]


def speak_question(question):
    """Read the interview question aloud in the browser."""

    question_json = json.dumps(question)

    html_code = f"""
    <div style="font-family: Arial; padding: 5px;">
        <button
            onclick="speakQuestion()"
            style="
                background-color: #7c3aed;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 15px;
            ">
            🔊 Listen to Question
        </button>

        <script>
            function speakQuestion() {{
                const question = {question_json};

                window.speechSynthesis.cancel();

                const speech = new SpeechSynthesisUtterance(question);
                speech.lang = "en-IN";
                speech.rate = 0.9;

                window.speechSynthesis.speak(speech);
            }}
        </script>
    </div>
    """

    components.html(html_code, height=60)


def convert_speech_to_text(audio_file):
    """Convert recorded microphone audio into text."""

    recognizer = sr.Recognizer()

    audio_bytes = audio_file.getvalue()

    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio_data = recognizer.record(source)

    text = recognizer.recognize_google(
        audio_data,
        language="en-IN",
    )

    return text


def show_voice_interview():

    st.header("🎤 Voice Interview")

    st.write(
        "Practice speaking your interview answers. "
        "Listen to each question, record your answer, "
        "and receive AI feedback."
    )

    st.info(
        "Allow microphone access when your browser asks. "
        "Speech recognition requires an internet connection."
    )

    # Select an interview question
    selected_question = st.selectbox(
        "Choose an interview question",
        VOICE_QUESTIONS,
        key="voice_question",
    )

    st.subheader("Your Interview Question")

    st.markdown(f"### {selected_question}")

    # Read question aloud
    speak_question(selected_question)

    st.divider()

    # Record answer
    st.subheader("🎙️ Record Your Answer")

    audio_file = st.audio_input(
        "Click to record your answer",
        key="voice_recording",
    )

    # Convert recorded voice into text
    if st.button(
        "📝 Convert Speech to Text",
        use_container_width=True,
    ):

        if audio_file is None:
            st.warning("Please record your answer first.")

        else:
            try:
                with st.spinner("Converting your speech into text..."):

                    transcript = convert_speech_to_text(audio_file)

                st.session_state["voice_transcript"] = transcript
                st.session_state["voice_transcript_question"] = (
                    selected_question
                )

                st.success("Your speech was converted successfully!")

            except sr.UnknownValueError:
                st.error(
                    "Sorry, your speech could not be understood. "
                    "Please record your answer again."
                )

            except sr.RequestError as error:
                st.error(
                    "Speech recognition is unavailable. "
                    "Check your internet connection and try again."
                )

                st.caption(str(error))

            except Exception as error:
                st.error("Something went wrong while processing the audio.")
                st.caption(str(error))

    # Show editable transcript
    transcript_question = st.session_state.get(
        "voice_transcript_question"
    )

    if (
        transcript_question == selected_question
        and "voice_transcript" in st.session_state
    ):

        st.subheader("📝 Your Answer")

        answer = st.text_area(
            "Review or correct your answer before submitting",
            key="voice_transcript",
            height=150,
        )

        # Get feedback and save to history
        if st.button(
            "🤖 Get AI Feedback & Save",
            use_container_width=True,
        ):

            if not answer.strip():
                st.warning("Your answer is empty. Please record an answer.")

            else:
                try:
                    with st.spinner("AI is reviewing your answer..."):

                        feedback = get_ai_feedback(
                            selected_question,
                            answer,
                        )

                    st.subheader("📊 AI Interview Feedback")
                    st.markdown(feedback)

                    save_interview(
                        category="Voice Interview",
                        question=selected_question,
                        answer=answer,
                        feedback=feedback,
                        score=None,
                    )

                    st.success(
                        "Your voice interview has been saved to history!"
                    )

                except Exception as error:
                    st.error(
                        "Could not complete the feedback or save operation."
                    )

                    st.exception(error)
       
       
                    
show_voice_interview()