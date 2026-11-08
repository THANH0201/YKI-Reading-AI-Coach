import logging
import sqlite3

from backend.functions.reading.repositories.vocabulary_repository import (
    VocabularyRepository,
)

from backend.shared.finnish_morphology import (
    generate_paradigm,
    infer_verb_type,
)

logger = logging.getLogger(__name__)

def save_finnish_word_analysis(
    word_form: str,
    lemma: str,
    part_of_speech: str,
    meaning: str,
    noun_type: str | None,
    verb_type: int | None,
    suffixes: list[dict[str, str]],
    grammatical_features: dict[str, str],
    stem_changes: list[str],
    word_forms: list[dict[str, str]],
    subject: str | None,
    article_id: int | None,
) -> dict:
    if not lemma.strip() or not part_of_speech.strip() or not meaning.strip():
        return {"error": "The lemma, part of speech, and meaning must not be empty."}

    if noun_type not in (None, "countable", "uncountable", "both"):
        return {"error": ("noun_type must be countable, uncountable, both, or null.")}

    if verb_type is not None and not 1 <= verb_type <= 6:
        return {"error": "verb_type must be an integer from 1 to 6 or null."}

    normalized_part_of_speech = part_of_speech.strip().casefold()
    if normalized_part_of_speech in {"verb", "verbi"}:
        inferred_type = infer_verb_type(lemma)
        if inferred_type is not None:
            verb_type = inferred_type
    paradigm_forms = generate_paradigm(lemma, part_of_speech, verb_type)

    if any(
        not isinstance(suffix, dict)
        or set(suffix) != {"suffix", "function"}
        or not isinstance(suffix.get("suffix"), str)
        or not isinstance(suffix.get("function"), str)
        or not suffix["suffix"].strip()
        or not suffix["function"].strip()
        for suffix in suffixes
    ):
        return {
            "error": ("Each suffix must contain non-empty suffix and function values.")
        }

    valid_cases = {
        "nominative",
        "genitive",
        "accusative",
        "partitive",
        "inessive",
        "elative",
        "illative",
        "adessive",
        "ablative",
        "allative",
        "essive",
        "translative",
        "abessive",
        "comitative",
        "instructive",
    }
    if any(
        not isinstance(form, dict)
        or set(form) != {"grammatical_case", "number", "form"}
        or form.get("grammatical_case") not in valid_cases
        or form.get("number") not in {"singular", "plural"}
        or not isinstance(form.get("form"), str)
        or not form["form"].strip()
        for form in word_forms
    ):
        return {
            "error": (
                "Each word form must include a supported grammatical_case, "
                "singular/plural number, and non-empty form."
            )
        }

    try:
        analysis = VocabularyRepository.save_word_analysis(
            word_form=word_form,
            lemma=lemma,
            part_of_speech=part_of_speech,
            meaning=meaning,
            noun_type=noun_type,
            verb_type=verb_type,
            suffixes=suffixes,
            grammatical_features=grammatical_features,
            stem_changes=stem_changes,
            word_forms=word_forms,
            subject=subject,
            article_id=article_id,
            paradigm_forms=paradigm_forms,
        )
    except sqlite3.Error:
        logger.exception("Could not save Finnish word analysis")
        return {"error": "The vocabulary analysis could not be saved."}

    return {"saved": True, **analysis}
