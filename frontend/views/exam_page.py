import streamlit as st
from backend.shared.timer import (
    format_remaining,
    remaining_seconds,
)
from backend.functions.reading.services.score_service import ScoreService
from backend.functions.reading.services.tutor_service import TutorService

# Compact UI
st.markdown(
    """
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 0.5rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

h1, h2, h3 {
    margin-bottom: 0.25rem !important;
}

hr {
    margin: 0.3rem 0 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def _submit_exam(auto_submitted=False):
    if "exam_result" in st.session_state:
        return

    questions = st.session_state.get("questions", [])

    if not questions:
        return

    user_answers = {
        f"q{index}": st.session_state.get(f"q{index}", "")
        for index in range(1, len(questions) + 1)
    }

    st.session_state["exam_result"] = ScoreService.grade_exam(
        article_id=st.session_state.get("article_id"),
        article_ids=st.session_state.get("article_ids"),
        article_level=st.session_state.get("level"),
        questions=questions,
        user_answers=user_answers,
    )

    st.session_state["exam_auto_submitted"] = auto_submitted
    st.session_state["exam_active"] = False


@st.fragment(run_every="1s")
def render_exam_timer():
    if "exam_result" in st.session_state:
        st.metric("⏱ Time Remaining", "Submitted")
        return

    deadline = st.session_state.get("exam_deadline")

    if deadline is None:
        st.metric("⏱ Time Remaining", "--:--")
        return

    seconds_left = remaining_seconds(deadline)

    st.metric(
        "⏱ Time Remaining",
        format_remaining(seconds_left),
    )

    if seconds_left == 0:
        _submit_exam(auto_submitted=True)
        st.rerun(scope="app")


def render_exam():
    questions = st.session_state.get("questions", [])
    exam_submitted = "exam_result" in st.session_state

    if not questions:
        st.subheader("Questions")
        st.warning("No questions available.")
        return

    articles = st.session_state.get("exam_articles", [])
    example_exam = st.session_state.get("example_exam", False)

    def render_question(index, question):
        st.markdown(f"**Question {index}.** {question.question}")

        if question.question_type == "multiple_choice":
            options = [
                question.option_a,
                question.option_b,
                question.option_c,
                question.option_d,
            ]
            st.radio(
                "Select one answer",
                options,
                index=None,
                key=f"q{index}",
                disabled=exam_submitted,
            )
        elif question.question_type == "true_false":
            st.radio(
                "Select one answer",
                ["True", "False"],
                index=None,
                key=f"q{index}",
                disabled=exam_submitted,
            )
        elif question.question_type == "open":
            st.text_input(
                "Your Answer",
                key=f"q{index}",
                disabled=exam_submitted,
            )
        else:
            st.warning(f"Question {index} has an unsupported question type.")

    deadline = st.session_state.get("exam_deadline")

    if deadline is not None and remaining_seconds(deadline) == 0:
        _submit_exam(auto_submitted=True)
        st.rerun(scope="app")

    if example_exam and articles:
        st.subheader("Example Exam")
        rendered_question_indexes = set()

        for article in articles:
            st.subheader(f"{article.exam_category or 'Reading'}: {article.title}")
            st.caption(
                f"{article.detected_level} · {article.subject} · "
                f"{article.word_count} words"
            )
            if article.source.startswith("Original AI-generated Finnish practice text"):
                st.caption(
                    "Original synthetic practice material; "
                    "not an article from a news publisher."
                )
            st.write(article.content)
            st.markdown("**Questions**")

            article_questions = [
                (index, question)
                for index, question in enumerate(questions, start=1)
                if question.article_id == article.id
            ]
            for index, question in article_questions:
                render_question(index, question)
                rendered_question_indexes.add(index)
                if index < len(questions):
                    st.markdown(
                        "<hr style='margin:5px 0'>",
                        unsafe_allow_html=True,
                    )

        remaining_questions = [
            (index, question)
            for index, question in enumerate(questions, start=1)
            if index not in rendered_question_indexes
        ]
        if remaining_questions:
            st.subheader("Other Questions")
            for index, question in remaining_questions:
                render_question(index, question)

    else:
        st.subheader("Questions")

    if articles and not example_exam:
        st.subheader("Reading texts")
        for article in articles:
            with st.expander(f"{article.exam_category or 'Reading'}: {article.title}"):
                st.caption(
                    f"{article.detected_level} · {article.subject} · "
                    f"{article.word_count} words"
                )
                if article.source.startswith(
                    "Original AI-generated Finnish practice text"
                ):
                    st.caption(
                        "Original synthetic practice material; "
                        "not an article from a news publisher."
                    )
                st.write(article.content)

    if not example_exam:
        for index, question in enumerate(questions, start=1):
            render_question(index, question)
            if index < len(questions):
                st.markdown(
                    "<hr style='margin:5px 0'>",
                    unsafe_allow_html=True,
                )

    if not exam_submitted and st.button(
        "Submit Exam",
        use_container_width=True,
    ):
        _submit_exam()
        st.rerun()


def render_exam_results():
    if "exam_result" not in st.session_state:
        return

    result = st.session_state["exam_result"]

    st.subheader("Exam Result")

    if st.session_state.get("exam_auto_submitted"):
        st.warning("Time is up. Your answers were submitted automatically.")

    st.success(f"Score: {result['score']}%")

    st.info("Chat with the AI Tutor to gain a deeper understanding of this article.")

    st.info(f"Correct Answers: {result['correct_answers']}/{result['total_questions']}")

    st.subheader("Question Review")

    for index, detail in enumerate(
        result["details"],
        start=1,
    ):
        if detail["is_correct"]:
            st.write(f"✅ Q{index}: Correct")

        else:
            st.error(
                f"""
Q{index}: Incorrect

Your Answer:
{detail["user_answer"]}

Correct Answer:
{detail["correct_answer"]}
"""
            )

    # feedback = result["feedback"]

    # st.subheader("🤖 AI Coach Feedback")

    # st.info(
    #     feedback.overall_feedback
    # )

    # if feedback.strengths:

    #     st.markdown("**✅ Strengths**")

    #     for item in feedback.strengths:
    #         st.write(f"• {item['question']}")

    # if feedback.weaknesses:

    #     st.markdown("**⚠ Areas To Improve**")

    #     for item in feedback.weaknesses:
    #         st.write(f"• {item['question']}")

    # if feedback.recommendations:

    #     st.markdown("**📚 Study Recommendations**")

    #     for item in feedback.recommendations:
    #         st.write(f"• {item}")

    # st.success(
    #     f"🎯 Next Goal: {feedback.next_goal}"
    # )


# "Finnish-English vocabulary translations use MyMemory; only the "
# "requested word or phrase is sent to that external service."


def render_tutor():

    st.subheader("🤖 AI Tutor")

    st.caption(
        "Ask Finnish vocabulary questions with or without an article. "
        "With an article loaded, explanations can use its context."
    )

    def send_tutor_question():
        tutor_question = st.session_state.get("tutor_question", "")

        if tutor_question:
            st.session_state["_pending_tutor_question"] = tutor_question
            st.session_state["tutor_question"] = ""

    if st.session_state.get("example_exam"):
        st.text_input(
            "Ask about vocabulary, grammar, or article content.",
            label_visibility="collapsed",
            placeholder="Ask about Finnish vocabulary or article content.",
            key="tutor_question",
        )
        st.button(
            ":material/send:",
            key="send_tutor_question",
            use_container_width=True,
            on_click=send_tutor_question,
        )
    else:
        col1, col2 = st.columns([10, 1])

        with col1:
            st.text_input(
                "Ask about vocabulary, grammar, or article content.",
                label_visibility="collapsed",
                placeholder="Ask about Finnish vocabulary or article content.",
                key="tutor_question",
            )

        with col2:
            st.button(
                ":material/send:",
                key="send_tutor_question",
                use_container_width=True,
                on_click=send_tutor_question,
            )

    pending_question = st.session_state.pop("_pending_tutor_question", None)
    if pending_question:
        with st.spinner("AI Tutor is preparing your answer..."):
            st.session_state["tutor_result"] = TutorService.answer(
                pending_question,
                st.session_state.get("content", ""),
                article_id=st.session_state.get("article_id"),
                subject=st.session_state.get("subject"),
            )

    result = st.session_state.get("tutor_result")
    if result:
        if result["success"]:
            st.info(result["answer"])
        else:
            st.warning(result["message"])
