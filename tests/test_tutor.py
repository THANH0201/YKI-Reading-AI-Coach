from io import BytesIO
import json
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from groq import GroqError, RateLimitError
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from backend.ai_neural_networks.reading.services.tutor_service import (
    GROQ_MODEL,
    MAX_TOOL_CALLS,
    SYSTEM_PROMPT,
    TUTOR_MAX_COMPLETION_TOKENS,
    TUTOR_REQUEST_TIMEOUT_SECONDS,
    TutorService,
    _build_agent,
    _build_tools,
    _execute_tool,
)
from backend.repositories.vocabulary_repository import VocabularyRepository


class FakeAgent:
    def __init__(self, messages):
        self.messages = messages
        self.invocation = None

    def invoke(self, invocation):
        self.invocation = invocation
        return {"messages": self.messages}


def _assistant_message(content):
    return SimpleNamespace(content=content)


def test_tutor_validates_question_but_allows_missing_article():
    agent = FakeAgent([_assistant_message("General vocabulary answer.")])
    with patch(
        "services.tutor_service._build_agent",
        return_value=agent
    ) as build_agent:
        assert TutorService.answer("", "Article")["success"] is False
        result = TutorService.answer("koti")

    assert result == {
        "success": True,
        "answer": "General vocabulary answer."
    }
    build_agent.assert_called_once_with(
        "",
        subject=None,
        article_id=None
    )


def test_tutor_uses_langchain_agent_and_returns_answer():
    agent = FakeAgent([_assistant_message("  Clear answer.  ")])
    with patch(
        "services.tutor_service._build_agent",
        return_value=agent
    ) as build_agent:
        result = TutorService.answer("What is a noun?", "Article")

    assert result == {"success": True, "answer": "Clear answer."}
    build_agent.assert_called_once_with(
        "Article",
        subject=None,
        article_id=None
    )
    assert agent.invocation == {
        "messages": [{"role": "user", "content": "What is a noun?"}]
    }


def test_tutor_saves_lemma_and_inflection_from_grammar_answer(database):
    explanation = """
avataan — "is opened" / "will be opened"

Word-by-word:
- avaa = "open" (verb, 3rd person singular present)
- -taan = passive marker (3rd person singular passive)

Grammar:
- Lemma: avata (verb, type 1)
- Form: 3rd person singular passive, present tense
- Meaning: "is opened" / "one opens" / "it gets opened"
"""
    agent = FakeAgent([_assistant_message(explanation)])
    with patch(
        "services.tutor_service._build_agent",
        return_value=agent
    ):
        result = TutorService.answer("What does avataan mean?")

    assert result["success"] is True
    analysis = VocabularyRepository.get_word_analysis_for_form("avataan")
    assert analysis is not None
    assert analysis["word_form"] == "avataan"
    assert analysis["lemma"] == "avata"
    assert analysis["part_of_speech"] == "verb"
    assert analysis["verb_type"] == 1
    assert analysis["meaning"] == (
        "is opened / one opens / it gets opened"
    )
    assert analysis["grammatical_features"] == {
        "form": "3rd person singular passive, present tense",
        "number": "singular",
        "voice": "passive",
        "tense": "present",
        "person": "3rd person"
    }
    assert analysis["suffixes"] == [{
        "suffix": "-taan",
        "function": "passive marker"
    }]
    assert analysis["stem_changes"] == ["Form uses the stem avaa"]


def test_tutor_enables_word_analysis_for_single_word_queries():
    agent = FakeAgent([_assistant_message("Koulutus is a noun.")])
    with patch(
        "services.tutor_service._build_agent",
        return_value=agent
    ) as build_agent:
        result = TutorService.answer(
            "Koulutuksen merkitys tässä lauseessa?",
            "Article",
            article_id=17,
            subject="Education"
        )

    assert result == {
        "success": True,
        "answer": "Koulutus is a noun."
    }
    build_agent.assert_called_once_with(
        "Article",
        subject="Education",
        article_id=17
    )


def test_langchain_agent_uses_groq_tools_prompt_and_tool_limit():
    with (
        patch("services.tutor_service.ChatGroq") as chat_groq,
        patch("services.tutor_service.create_agent") as create_agent
    ):
        _build_agent("Current article.")

    chat_groq.assert_called_once_with(
        model=GROQ_MODEL,
        temperature=0.3,
        timeout=TUTOR_REQUEST_TIMEOUT_SECONDS,
        max_retries=0,
        max_tokens=TUTOR_MAX_COMPLETION_TOKENS
    )
    assert TUTOR_MAX_COMPLETION_TOKENS < 1000
    arguments = create_agent.call_args.kwargs
    assert arguments["model"] is chat_groq.return_value
    assert arguments["system_prompt"] == SYSTEM_PROMPT
    assert [tool.name for tool in arguments["tools"]] == [
        "search_article",
        "translate_finnish_to_english",
        "save_finnish_word_analysis"
    ]
    middleware = arguments["middleware"]
    assert len(middleware) == 1
    assert isinstance(middleware[0], ToolCallLimitMiddleware)
    assert middleware[0].run_limit == MAX_TOOL_CALLS


def test_langchain_agent_completes_model_tool_result_model_cycle():
    fake_model = GenericFakeChatModel(messages=iter([
        AIMessage(
            content="",
            tool_calls=[{
                "name": "search_article",
                "args": {"query": "Finland education"},
                "id": "search-call",
                "type": "tool_call"
            }]
        ),
        AIMessage(content="The article says Finland values education.")
    ]))

    with (
        patch(
            "services.tutor_service.ChatGroq",
            return_value=fake_model
        ),
        patch.object(
            GenericFakeChatModel,
            "bind_tools",
            lambda self, tools, **kwargs: self
        )
    ):
        result = _build_agent(
            "Finland values education. The weather is cold."
        ).invoke({
            "messages": [{
                "role": "user",
                "content": "What does it say about education?"
            }]
        })

    messages = result["messages"]
    assert isinstance(messages[1], AIMessage)
    assert messages[1].tool_calls[0]["name"] == "search_article"
    assert messages[2].content == json.dumps({
        "query": "Finland education",
        "matches": ["Finland values education."]
    })
    assert messages[-1].content == (
        "The article says Finland values education."
    )


def test_langchain_agent_middleware_limits_tool_execution_per_run():
    def search_call(call_number):
        return AIMessage(
            content="",
            tool_calls=[{
                "name": "search_article",
                "args": {"query": "Finland"},
                "id": f"search-{call_number}",
                "type": "tool_call"
            }]
        )

    fake_model = GenericFakeChatModel(messages=iter([
        search_call(1),
        search_call(2),
        search_call(3),
        search_call(4),
        AIMessage(content="The tool-call limit was enforced.")
    ]))

    with (
        patch(
            "services.tutor_service.ChatGroq",
            return_value=fake_model
        ),
        patch.object(
            GenericFakeChatModel,
            "bind_tools",
            lambda self, tools, **kwargs: self
        ),
        patch(
            "services.tutor_service._search_article",
            return_value={"matches": ["Finland."]}
        ) as search
    ):
        result = _build_agent("Finland.").invoke({
            "messages": [{"role": "user", "content": "Search Finland"}]
        })

    assert search.call_count == MAX_TOOL_CALLS
    assert result["messages"][-1].content == (
        "The tool-call limit was enforced."
    )


def test_langchain_article_tool_searches_current_article():
    tools = _build_tools(
        "Finland values education. The weather is cold."
    )
    search_tool = tools[0]

    result = json.loads(search_tool.invoke({"query": "Finland education"}))
    assert result == {
        "query": "Finland education",
        "matches": ["Finland values education."]
    }


def test_article_search_matches_common_finnish_inflections():
    search_tool = _build_tools(
        "Koulutuksen merkitys on suuri."
    )[0]

    result = json.loads(search_tool.invoke({"query": "koulutus"}))
    assert result["matches"] == ["Koulutuksen merkitys on suuri."]


def test_langchain_translation_tool_uses_mymemory_api_and_caches_result(database):
    api_response = BytesIO(
        json.dumps({
            "responseData": {
                "translatedText": "education"
            }
        }).encode("utf-8")
    )
    translation_tool = _build_tools(
        "Article must not be sent to API."
    )[1]

    with patch(
        "services.tutor_service.urlopen",
        return_value=api_response
    ) as translate:
        result = json.loads(
            translation_tool.invoke({"phrase": "koulutus"})
        )

    assert result == {
        "phrase": "koulutus",
        "translation": "education",
        "source": "MyMemory",
        "cached": False
    }
    request = translate.call_args.args[0]
    assert parse_qs(urlparse(request.full_url).query) == {
        "q": ["koulutus"],
        "langpair": ["fi|en"]
    }
    assert translate.call_args.kwargs["timeout"] == 8
    assert VocabularyRepository.get_translation("koulutus") == {
        "phrase": "koulutus",
        "translation": "education",
        "provider": "MyMemory"
    }


def test_translation_tool_uses_database_cache_without_calling_api(database):
    VocabularyRepository.save_translation(
        phrase="Koulutus",
        translation="education"
    )
    translation_tool = _build_tools("Article.")[1]

    with patch("services.tutor_service.urlopen") as translate:
        result = json.loads(
            translation_tool.invoke({"phrase": "  KOULUTUS  "})
        )

    translate.assert_not_called()
    assert result == {
        "phrase": "Koulutus",
        "translation": "education",
        "source": "MyMemory",
        "cached": True
    }


def test_translation_tool_rejects_oversized_phrase():
    translation_tool = _build_tools("Article")[1]

    with (
        patch("services.tutor_service.urlopen") as translate,
        pytest.raises(ValidationError)
    ):
        translation_tool.invoke({"phrase": "word " * 30})

    translate.assert_not_called()


def test_translation_tool_returns_api_failure_to_agent(database):
    translation_tool = _build_tools("Article")[1]
    with patch(
        "services.tutor_service.urlopen",
        side_effect=TimeoutError("timeout")
    ):
        result = json.loads(
            translation_tool.invoke({"phrase": "koulutus"})
        )

    assert result == {
        "error": (
            "The Finnish-English translation service is temporarily "
            "unavailable (TimeoutError)."
        )
    }


def test_single_word_analysis_tool_saves_grammar_and_article_subject(database):
    tools = _build_tools(
        "Article.",
        subject="Education",
        article_id=None
    )
    analysis_tool = tools[2]

    result = json.loads(analysis_tool.invoke({
        "word_form": "koulutuksen",
        "lemma": "koulutus",
        "meaning": "education; learning",
        "part_of_speech": "noun",
        "noun_type": "countable",
        "suffixes": [{"suffix": "n", "function": "genitive"}],
        "grammatical_features": {"case": "genitive"},
        "stem_changes": ["consonant gradation"],
        "word_forms": [
            {
                "grammatical_case": "partitive",
                "number": "singular",
                "form": "koulutusta"
            },
            {
                "grammatical_case": "partitive",
                "number": "plural",
                "form": "koulutuksia"
            }
        ]
    }))

    assert result["saved"] is True
    assert result["word_form"] == "koulutuksen"
    assert result["lemma"] == "koulutus"
    assert result["subject"] == "Education"
    assert VocabularyRepository.get_word_analysis(
        "KOULUTUS"
    )["suffixes"] == [
        {"suffix": "n", "function": "genitive"}
    ]
    assert {
        (form["grammatical_case"], form["number"], form["form"])
        for form in VocabularyRepository.get_word_analysis(
            "koulutus"
        )["forms"]
    } == {
        ("partitive", "singular", "koulutusta"),
        ("partitive", "plural", "koulutuksia")
    }


def test_vocabulary_analysis_is_saved_when_no_article_is_loaded(database):
    analysis_tool = _build_tools("")[1]

    result = json.loads(analysis_tool.invoke({
        "word_form": "kotona",
        "lemma": "koti",
        "meaning": "home; at home",
        "part_of_speech": "noun",
        "noun_type": "countable",
        "suffixes": [{"suffix": "na", "function": "essive"}],
        "grammatical_features": {
            "case": "essive",
            "number": "singular"
        },
        "word_forms": [
            {
                "grammatical_case": "partitive",
                "number": "singular",
                "form": "kotia"
            },
            {
                "grammatical_case": "partitive",
                "number": "plural",
                "form": "kotoja"
            }
        ]
    }))

    assert result["saved"] is True
    assert result["article_id"] is None
    assert VocabularyRepository.get_word_analysis("koti")["word_form"] == (
        "kotona"
    )


def test_single_word_analysis_tool_rejects_invalid_finnish_verb_type():
    tools = _build_tools("Article.")
    analysis_tool = tools[1]

    with pytest.raises(ValidationError):
        analysis_tool.invoke({
            "word_form": "puhun",
            "lemma": "puhua",
            "meaning": "to speak",
            "part_of_speech": "verb",
            "verb_type": 7
        })


def test_tutor_returns_cached_inflected_word_without_calling_ai(database):
    VocabularyRepository.save_word_analysis(
        word_form="kotona",
        lemma="koti",
        part_of_speech="noun",
        meaning="home; at home",
        noun_type="countable",
        word_forms=[
            {
                "grammatical_case": "illative",
                "number": "singular",
                "form": "kotiin"
            }
        ]
    )

    with patch("services.tutor_service._build_agent") as build_agent:
        result = TutorService.answer("What does kotiin mean?")

    build_agent.assert_not_called()
    assert result["success"] is True
    assert "kotiin — koti (noun)" in result["answer"]
    assert "home; at home" in result["answer"]
    assert (
        '"kotiin" là dạng illative singular của "koti", trả lời câu hỏi '
        '"mihin?" (đến đâu?) và chỉ hướng đến nhà.'
    ) in result["answer"]


def test_tutor_uses_cached_word_and_article_sentence_without_calling_ai(
        database
):
    VocabularyRepository.save_word_analysis(
        word_form="koti",
        lemma="koti",
        part_of_speech="noun",
        meaning="home",
        noun_type="countable",
        word_forms=[
            {
                "grammatical_case": "illative",
                "number": "singular",
                "form": "kotiin"
            }
        ]
    )

    with patch("services.tutor_service._build_agent") as build_agent:
        result = TutorService.answer(
            "Kotiin?",
            "Menen kotiin joka ilta."
        )

    build_agent.assert_not_called()
    assert result["success"] is True
    assert "In the current article" in result["answer"]
    assert "Menen kotiin joka ilta." in result["answer"]


def test_tutor_calls_ai_when_vocabulary_is_not_cached():
    agent = FakeAgent([_assistant_message("New explanation.")])
    with (
        patch(
            "services.tutor_service.VocabularyRepository."
            "get_word_analysis_for_form",
            return_value=None
        ),
        patch(
            "services.tutor_service._build_agent",
            return_value=agent
        ) as build_agent
    ):
        result = TutorService.answer("What does uusi sana mean?")

    assert result == {
        "success": True,
        "answer": "New explanation."
    }
    build_agent.assert_called_once()


def test_word_analysis_tool_is_available_without_an_article():
    assert [tool.name for tool in _build_tools("")] == [
        "translate_finnish_to_english",
        "save_finnish_word_analysis"
    ]
    assert "search_article" not in {
        tool.name for tool in _build_tools("")
    }


def test_tool_executor_rejects_unapproved_and_invalid_tools():
    assert _execute_tool("run_python", {}, "Article") == {
        "error": "This tool is not available."
    }
    assert _execute_tool("search_article", {"extra": "x"}, "Article") == {
        "error": "search_article requires only a query argument."
    }
    assert _execute_tool(
        "translate_finnish_to_english",
        {"phrase": ""},
        "Article"
    ) == {
        "error": "The phrase must be a non-empty string."
    }


def test_tutor_surfaces_agent_failure_and_invalid_responses():
    with (
        patch(
            "services.tutor_service._build_agent",
            side_effect=GroqError("offline")
        ),
        patch("services.tutor_service.logger.exception")
    ):
        result = TutorService.answer("Question", "Article")

    assert result["success"] is False
    assert "unavailable" in result["message"]

    with patch(
        "services.tutor_service._build_agent",
        return_value=FakeAgent([])
    ):
        result = TutorService.answer("Question", "Article")
    assert result["success"] is False
    assert "invalid response" in result["message"]

    with patch(
        "services.tutor_service._build_agent",
        return_value=FakeAgent([_assistant_message(" ")])
    ):
        result = TutorService.answer("Question", "Article")
    assert result["success"] is False
    assert "empty response" in result["message"]


def test_tutor_explains_provider_rate_limit():
    rate_limit_error = RateLimitError(
        "Output tokens per minute limit exceeded.",
        response=httpx.Response(
            429,
            request=httpx.Request("POST", "https://api.groq.com")
        ),
        body={"error": {"code": "rate_limit_exceeded"}}
    )
    with (
        patch(
            "services.tutor_service._build_agent",
            side_effect=rate_limit_error
        ),
        patch("services.tutor_service.logger.exception")
    ):
        result = TutorService.answer("What does koti mean?")

    assert result == {
        "success": False,
        "message": (
            "The AI Tutor has reached the provider's temporary request "
            "limit. Please wait a moment and try again."
        )
    }
