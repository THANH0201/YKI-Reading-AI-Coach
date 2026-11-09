import sqlite3

import streamlit as st
from backend.functions.reading.models.exam_category import (
    ARTICLE_QUOTA_PER_CATEGORY,
    EXAM_CATEGORY_RULES,
)
from backend.functions.reading.services.article_ingestion_service import (
    ArticleIngestionService,
)
from backend.functions.reading.services.article_service import ArticleService
from backend.functions.reading.services.exam_service import ExamService
from backend.shared.timer import (
    create_deadline,
)

from backend.functions.writting.ai.writing_analyzer import analyze_writing
from views.exam_page import (
    render_exam,
    render_exam_results,
    render_exam_timer,
    render_tutor,
)

# Compact UI (safe)
st.markdown(
    """
<style>
.block-container {
    padding-top: 3rem;
    padding-bottom: 0.5rem;
}

h1, h2, h3 {
    margin-bottom: 0.3rem !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def _clear_exam_answers():
    for index in range(1, len(st.session_state.get("questions", [])) + 1):
        st.session_state.pop(f"q{index}", None)


def _clear_assessment():
    _clear_exam_answers()

    for key in (
        "article_id",
        "article_ids",
        "exam_articles",
        "content",
        "level",
        "subject",
        "questions",
        "exam_active",
        "exam_deadline",
        "exam_auto_submitted",
        "exam_result",
        "example_exam",
    ):
        st.session_state.pop(key, None)


def _render_article_form(show_start_button=True):

    article_error = st.session_state.pop("_article_error", None)

    if article_error:
        st.warning(article_error)

    content = st.text_area("Article Content", height=250, key="home_content")
    st.caption(
        "User-provided text is processed for this practice session only. "
        "It is not saved to the database or used in Example Exams. "
        "The text is sent to the configured AI provider for analysis."
    )

    if st.button("Analyze Reading", use_container_width=True):
        result = ArticleService.process_article(content)

        if not result["success"]:
            _clear_assessment()
            st.session_state["_article_error"] = result["message"]
            st.rerun()

        st.session_state["article_id"] = result["article_id"]
        st.session_state.pop("example_exam", None)
        st.session_state.pop("article_ids", None)
        st.session_state.pop("exam_articles", None)
        st.session_state["content"] = content
        st.session_state["level"] = result["level"]
        st.session_state["subject"] = result["subject"]

        _clear_exam_answers()

        st.session_state["questions"] = result["questions"]

        st.session_state["exam_active"] = False

        st.session_state.pop("exam_deadline", None)
        st.session_state.pop("exam_auto_submitted", None)
        st.session_state.pop("exam_result", None)

        st.rerun()

    if "level" in st.session_state:
        subject = st.session_state.get("subject", "")

        if show_start_button:
            info_col, btn_col = st.columns([5, 1])

            with info_col:
                st.caption(
                    f"📊 Level: {st.session_state['level']} | 📚 Subject: {subject}"
                )

            with btn_col:
                if st.button("🚀", help="Start Exam"):
                    st.session_state["exam_deadline"] = create_deadline()

                    st.session_state.pop("exam_auto_submitted", None)

                    st.session_state.pop("exam_result", None)

                    st.session_state["exam_active"] = True

                    st.rerun()

        else:
            st.caption(f"📊 Level: {st.session_state['level']} | 📚 Subject: {subject}")


def _load_example_exam():

    exam = ExamService.get_random_exam()

    if not exam:
        st.warning("No example exam is available.")
        return False

    article = exam["article"]
    articles = exam.get("articles") or [article]

    st.session_state["article_id"] = article.id
    st.session_state["example_exam"] = True
    st.session_state["article_ids"] = exam.get(
        "article_ids", [sample_article.id for sample_article in articles]
    )
    st.session_state["exam_articles"] = articles
    st.session_state["content"] = article.content
    st.session_state["level"] = article.detected_level
    st.session_state["subject"] = article.subject

    _clear_exam_answers()

    st.session_state["questions"] = exam["questions"]

    st.session_state["home_content"] = article.content

    st.session_state["exam_deadline"] = create_deadline()

    st.session_state.pop("exam_auto_submitted", None)

    st.session_state.pop("exam_result", None)

    st.session_state["exam_active"] = True

    return True


def _show_ingestion_result(result):
    st.success(f"Imported {len(result['imported'])} eligible article(s).")
    if result["imported"]:
        st.dataframe(result["imported"], use_container_width=True)
    for item in result["skipped"]:
        st.info(f"Skipped “{item['title']}”: {item['reason']}")
    for item in result["failed"]:
        st.error(f"Failed “{item['title']}”: {item['reason']}")


def _render_writing_practice():
    st.title("Writing Practice")
    st.caption(
        "Submit your Finnish text for an AI estimate of B1/B2 writing level, "
        "spelling and grammar corrections, and sentence-structure suggestions. "
        "This is practice feedback, not an official YKI score."
    )
    writing = st.text_area(
        "Your Finnish writing",
        height=250,
        key="writing_content",
        placeholder="Write or paste your Finnish text here...",
    )

    if st.button("Analyze Writing", key="analyze_writing"):
        st.session_state["writing_analysis_result"] = analyze_writing(writing)
        st.session_state["writing_analysis_text"] = writing

    result = st.session_state.get("writing_analysis_result")
    if not result or st.session_state.get("writing_analysis_text") != writing:
        return
    if not result["success"]:
        st.warning(result["message"])
        return

    analysis = result["analysis"]
    st.subheader(f"Estimated level: {analysis['estimated_level']}")
    st.write(analysis["assessment"])

    if analysis["strengths"]:
        st.markdown("**Strengths**")
        for strength in analysis["strengths"]:
            st.markdown(f"- {strength}")

    if analysis["corrections"]:
        st.markdown("**Spelling and grammar corrections**")
        for correction in analysis["corrections"]:
            st.markdown(
                f"- `{correction['original']}` → "
                f"`{correction['corrected']}` — "
                f"{correction['explanation']}"
            )
    else:
        st.info("No clear spelling or grammar errors were identified.")

    if analysis["sentence_suggestions"]:
        st.markdown("**Sentence structure and vocabulary suggestions**")
        for suggestion in analysis["sentence_suggestions"]:
            st.markdown(
                f"- `{suggestion['original']}` → "
                f"`{suggestion['suggestion']}` — "
                f"{suggestion['explanation']}"
            )

    st.markdown("**Suggested revision**")
    st.write(analysis["revised_text"])


def _render_skill_placeholder(skill_name: str, message: str):
    st.title(f"{skill_name} Practice")
    st.info(message)


def _render_article_ingestion():
    with st.expander("Build the sample-exam library from licensed feeds"):
        st.warning(
            "Only add an RSS/Atom feed when its license or written permission "
            "explicitly allows full-text storage, adaptation into questions, "
            "AI-provider processing, and display to learners. The app does "
            "not verify licensing claims or automatically crawl the example "
            "reference sites."
        )

        with st.form("licensed_feed_form"):
            publisher = st.text_input("Publisher")
            category_labels = {
                rules["label"]: category
                for category, rules in EXAM_CATEGORY_RULES.items()
            }
            selected_category_label = st.selectbox(
                "YKI article type", options=list(category_labels)
            )
            feed_url = st.text_input(
                "RSS/Atom feed URL", placeholder="https://publisher.example/rss.xml"
            )
            rights_basis = st.text_input(
                "License or written permission",
                placeholder="CC BY 4.0 or written permission",
            )
            permission_reference = st.text_input("License/permission evidence URL")
            approved_by = st.text_input("Reviewed/approved by", placeholder="Your name")
            rights_confirmed = st.checkbox(
                "I confirm this source permits storing and adapting the "
                "full text, sending it to the configured AI provider, and "
                "displaying the resulting practice exam."
            )
            add_and_crawl = st.form_submit_button(
                "Add licensed feed and import eligible articles",
                use_container_width=True,
            )

        if add_and_crawl:
            try:
                result = ArticleIngestionService.add_source_and_crawl(
                    publisher=publisher,
                    feed_url=feed_url,
                    rights_basis=rights_basis,
                    permission_reference=permission_reference,
                    approved_by=approved_by,
                    rights_confirmed=rights_confirmed,
                    exam_category=category_labels[selected_category_label],
                )
            except (ValueError, OSError) as error:
                st.error(f"Could not import the feed: {error}")
            except sqlite3.Error as error:
                st.error(f"The licensed-feed database is unavailable: {error}")
            else:
                _show_ingestion_result(result)

        try:
            sources = ArticleIngestionService.list_sources()
        except sqlite3.Error as error:
            st.error(f"The licensed-feed registry is unavailable: {error}")
            return
        if sources:
            st.caption("Registered licensed feeds")
            st.dataframe(
                [
                    {
                        "Publisher": source["publisher"],
                        "Article type": EXAM_CATEGORY_RULES[source["exam_category"]][
                            "label"
                        ],
                        "Feed": source["feed_url"],
                        "License": source["rights_basis"],
                        "Last checked": source["last_checked_at"] or "Never",
                    }
                    for source in sources
                ],
                use_container_width=True,
            )
            if st.button(
                "Fetch all registered feeds", key="crawl_all_registered_feeds"
            ):
                try:
                    feed_results = ArticleIngestionService.crawl_all_sources()
                except sqlite3.Error as error:
                    st.error(f"The licensed-feed database is unavailable: {error}")
                else:
                    for result in feed_results:
                        if "error" in result:
                            st.error(f"{result['publisher']}: {result['error']}")
                        else:
                            st.markdown(f"**{result['publisher']}**")
                            _show_ingestion_result(result)

            source_options = {
                f"{source['publisher']} — {source['feed_url']}": source["id"]
                for source in sources
            }
            selected_source = st.selectbox(
                "Run a registered feed again",
                options=list(source_options),
                key="registered_feed_to_crawl",
            )
            if st.button("Fetch and process new articles", key="crawl_registered_feed"):
                try:
                    result = ArticleIngestionService.crawl_source(
                        source_options[selected_source]
                    )
                except (ValueError, OSError) as error:
                    st.error(f"Could not import the feed: {error}")
                except sqlite3.Error as error:
                    st.error(f"The licensed-feed database is unavailable: {error}")
                else:
                    _show_ingestion_result(result)

        try:
            pool_counts = " · ".join(
                (
                    f"{rules['label']}: "
                    f"{ArticleIngestionService.remaining_article_capacity(category)} "
                    f"of {ARTICLE_QUOTA_PER_CATEGORY} slots remaining"
                )
                for category, rules in EXAM_CATEGORY_RULES.items()
            )
        except sqlite3.Error as error:
            st.error(f"The sample library is unavailable: {error}")
        else:
            st.caption("Pool counts: " + pool_counts)


def render_home():

    st.sidebar.title("YKI Reading AI Coach")

    st.session_state.setdefault("practice_section", "reading")

    if st.sidebar.button("📚 Example Reading Exam"):
        st.session_state["practice_section"] = "reading"
        if _load_example_exam():
            st.rerun()

    for section, label in (
        ("reading", "📖 Reading"),
        ("listening", "🎧 Listening"),
        ("speaking", "🗣 Speaking"),
        ("writing", "✍️ Writing"),
    ):
        if st.sidebar.button(
            label,
            key=f"practice_{section}",
            type=(
                "primary"
                if st.session_state["practice_section"] == section
                else "secondary"
            ),
        ):
            st.session_state["practice_section"] = section

    if (
        st.session_state.get("exam_active") or "exam_result" in st.session_state
    ) and st.sidebar.button("🏠 Home"):
        _clear_assessment()
        for key in (
            "home_content",
            "tutor_result",
            "tutor_question",
        ):
            st.session_state.pop(key, None)
        st.session_state["practice_section"] = "reading"
        st.rerun()

    active_section = st.session_state["practice_section"]
    if active_section == "listening":
        _render_skill_placeholder(
            "Listening",
            "Listening practice is not available yet. This section is a "
            "placeholder for future audio exercises.",
        )
        return
    if active_section == "speaking":
        _render_skill_placeholder(
            "Speaking",
            "Speaking practice is not available yet. This section is a "
            "placeholder for future speaking exercises.",
        )
        return
    if active_section == "writing":
        _render_writing_practice()
        return

    # Tutor luôn hiển thị đầy đủ phía trên
    render_tutor()

    exam_active = st.session_state.get("exam_active", False)

    if exam_active:
        with st.sidebar:
            render_exam_timer()

    if st.session_state.get("example_exam"):
        render_exam()
        render_exam_results()

    elif exam_active or "exam_result" in st.session_state:
        home_column, question_column = st.columns([1.5, 1])

        with home_column:
            if not st.session_state.get("example_exam"):
                _render_article_form(show_start_button=False)

            render_exam_results()

        with question_column:
            render_exam()

    else:
        _render_article_form()

    _render_article_ingestion()
