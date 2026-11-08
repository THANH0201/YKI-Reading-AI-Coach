import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from backend.functions.reading.repositories.vocabulary_repository import (
    VocabularyRepository,
)


def translate_finnish_to_english(phrase: str):

    cached = VocabularyRepository.get_translation(phrase)

    if cached:
        return {
            "phrase": cached["phrase"],
            "translation": cached["translation"],
            "cached": True,
        }

    url = "https://api.mymemory.translated.net/get?" + urlencode(
        {"q": phrase, "langpair": "fi|en"}
    )

    try:
        request = Request(url, headers={"User-Agent": "YKI-Reading-AI-Coach"})

        with urlopen(request, timeout=8) as response:
            result = json.load(response)

    except (URLError, TimeoutError, json.JSONDecodeError):
        return {"error": "Translation service unavailable."}

    translated_text = result["responseData"]["translatedText"]

    VocabularyRepository.save_translation(phrase, translated_text, "MyMemory")

    return {"phrase": phrase, "translation": translated_text}
