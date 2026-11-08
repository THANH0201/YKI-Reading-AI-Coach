from ..cache.vocabulary_cache import (
    find_cached_vocabulary,
    cached_vocabulary_answer,
    save_analysis_from_answer,
)

from ..agent.tutor_agent import (
    build_tutor_agent,
)

class TutorService:
    @staticmethod
    def answer(
        question: str,
        article_content: str = "",
        article_id: int | None = None,
        subject: str | None = None,
    ):

        if not question.strip():
            return {"success": False, "message": "Question required."}

        cached = find_cached_vocabulary(question, article_id)

        if cached:
            word_form, analysis = cached

            return {
                "success": True,
                "answer": cached_vocabulary_answer(
                    word_form,
                    analysis,
                    article_content,
                ),
            }

        agent = build_tutor_agent(article_content, subject, article_id)

        result = agent.invoke({"messages": [{"role": "user", "content": question}]})

        answer = result["messages"][-1].content

        save_analysis_from_answer(question, answer, subject, article_id)

        return {"success": True, "answer": answer}
