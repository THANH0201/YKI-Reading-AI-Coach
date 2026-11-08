import json

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq

from ..prompts.tutor_prompt import SYSTEM_PROMPT

from ..tools.article_search_tool import (
    search_article,
)

from ..tools.translation_tool import (
    translate_finnish_to_english,
)

from ..tools.vocabulary_tool import (
    save_finnish_word_analysis,
)


def build_tools(
    article_content: str,
    subject: str | None = None,
    article_id: int | None = None,
):
    @tool
    def search_article_tool(
        query: str,
    ) -> str:
        """Search the current article for relevant sentences."""

        return json.dumps(
            search_article(
                article_content,
                query,
            ),
            ensure_ascii=False,
        )

    @tool
    def translate_tool(
        phrase: str,
    ) -> str:
        """Translate a Finnish word or phrase."""

        return json.dumps(
            translate_finnish_to_english(
                phrase,
            ),
            ensure_ascii=False,
        )

    @tool
    def save_word_tool(
        word_form: str,
        lemma: str,
        meaning: str,
        part_of_speech: str,
        noun_type: str | None = None,
        verb_type: int | None = None,
        suffixes: list[dict] | None = None,
        grammatical_features: dict | None = None,
        stem_changes: list[str] | None = None,
        word_forms: list[dict] | None = None,
    ) -> str:
        """Save Finnish vocabulary analysis."""

        result = save_finnish_word_analysis(
            word_form=word_form,
            lemma=lemma,
            meaning=meaning,
            part_of_speech=part_of_speech,
            noun_type=noun_type,
            verb_type=verb_type,
            suffixes=suffixes or [],
            grammatical_features=grammatical_features or {},
            stem_changes=stem_changes or [],
            word_forms=word_forms or [],
            subject=subject,
            article_id=article_id,
        )

        return json.dumps(
            result,
            ensure_ascii=False,
        )

    return [
        search_article_tool,
        translate_tool,
        save_word_tool,
    ]


def build_tutor_agent(
    article_content: str,
    subject: str | None = None,
    article_id: int | None = None,
):
    return create_agent(
        model=ChatGroq(
            model="qwen/qwen3.8-27b",
            temperature=0.3,
        ),
        tools=build_tools(
            article_content,
            subject,
            article_id,
        ),
        system_prompt=SYSTEM_PROMPT,
    )