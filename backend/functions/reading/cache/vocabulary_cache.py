import logging
import re

from ..repositories.vocabulary_repository import (
    VocabularyRepository,
)

from ..tools.article_search_tool import (
    search_article,
)

from ..tools.vocabulary_tool import (
    save_finnish_word_analysis,
)

logger = logging.getLogger(__name__)


def cached_vocabulary_answer(
    word_form: str, analysis: dict, article_content: str
) -> str:
    answer = (
        f"{word_form} — {analysis['lemma']} "
        f"({analysis['part_of_speech']}): {analysis['meaning']}"
    )
    if analysis["noun_type"]:
        answer += f" Noun type: {analysis['noun_type']}."
    if analysis["verb_type"]:
        answer += f" Finnish verb type: {analysis['verb_type']}."

    normalized_form = word_form.casefold()
    inflected_form = next(
        (
            form
            for form in analysis["forms"]
            if form["form"].casefold() == normalized_form
        ),
        None,
    )
    if inflected_form is None and (analysis["word_form"].casefold() == normalized_form):
        grammatical_features = analysis["grammatical_features"]
        grammatical_case = grammatical_features.get("case")
        number = grammatical_features.get("number")
        if grammatical_case and number:
            inflected_form = {
                "grammatical_case": grammatical_case,
                "number": number,
                "form": word_form,
            }

    if inflected_form:
        grammatical_case = inflected_form["grammatical_case"]
        number = inflected_form["number"]
        if grammatical_case == "illative":
            destination = (
                "và chỉ hướng đến nhà."
                if analysis["lemma"].casefold() == "koti"
                else "và chỉ hướng đến/đi vào một nơi hoặc đối tượng."
            )
            answer += (
                f' Ngữ pháp: "{word_form}" là dạng illative '
                f'{number} của "{analysis["lemma"]}", trả lời câu hỏi '
                f'"mihin?" (đến đâu?) {destination}'
            )
        else:
            answer += (
                f' Ngữ pháp: "{word_form}" là dạng {grammatical_case} '
                f'{number} của "{analysis["lemma"]}".'
            )

    features = analysis["grammatical_features"]
    if features:
        feature_text = ", ".join(f"{name}: {value}" for name, value in features.items())
        answer += f" Saved grammatical features: {feature_text}."

    if analysis["suffixes"]:
        suffix_text = ", ".join(
            f"{suffix['suffix']} ({suffix['function']})"
            for suffix in analysis["suffixes"]
        )
        answer += f" Saved suffix analysis: {suffix_text}."

    if article_content.strip():
        matches = search_article(article_content, f"{word_form} {analysis['lemma']}")[
            "matches"
        ]
        if matches:
            answer += " In the current article, the matching context is: " + " ".join(
                matches
            )
        else:
            answer += (
                " This word was not found in the current article; "
                "the meaning above is its saved general meaning."
            )

    return answer


def save_analysis_from_answer(
    question: str, answer: str, subject: str | None, article_id: int | None
) -> bool | None:
    lemma_match = re.search(
        r"(?im)^\s*(?:[-*•]\s*)?Lemma\s*:\s*([^\s(]+)\s*\(([^)]*)\)", answer
    )
    meaning_match = re.search(r"(?im)^\s*(?:[-*•]\s*)?Meaning\s*:\s*(.+?)\s*$", answer)
    form_match = re.search(r"(?im)^\s*(?:[-*•]\s*)?Form\s*:\s*(.+?)\s*$", answer)
    if not lemma_match or not meaning_match or not form_match:
        return None

    lemma = lemma_match.group(1).strip("`\"' ")
    analysis_description = lemma_match.group(2).casefold()
    part_of_speech = analysis_description.split(",", maxsplit=1)[0].strip()
    if not part_of_speech:
        return None

    word_match = re.search(r"(?m)^\s*([^\W_]+)\s*[—–-]\s*", answer)
    if word_match:
        word_form = word_match.group(1)
    else:
        question_terms = re.findall(
            r"[^\W_]+(?:[-'][^\W_]+)*", question, flags=re.UNICODE
        )
        answer_terms = {
            term.casefold() for term in re.findall(r"[^\W_]+", answer, flags=re.UNICODE)
        }
        word_form = next(
            (term for term in question_terms if term.casefold() in answer_terms), ""
        )
    if not word_form or not re.fullmatch(
        r"[^\W_]+(?:[-'][^\W_]+)*", word_form, flags=re.UNICODE
    ):
        return None

    verb_type_match = re.search(r"\bverb\s*,\s*type\s+([1-6])\b", analysis_description)
    verb_type = int(verb_type_match.group(1)) if verb_type_match else None
    if part_of_speech == "verb" and verb_type is None:
        return None

    form_description = form_match.group(1).strip()
    normalized_form = form_description.casefold()
    grammatical_features = {"form": form_description}
    for feature in ("singular", "plural", "passive", "active", "present", "past"):
        if re.search(rf"\b{feature}\b", normalized_form):
            grammatical_features[
                "tense"
                if feature in {"present", "past"}
                else "voice"
                if feature in {"passive", "active"}
                else "number"
            ] = feature
    person_match = re.search(r"\b([1-6](?:st|nd|rd|th)\s+person)\b", normalized_form)
    if person_match:
        grammatical_features["person"] = person_match.group(1)

    suffixes = []
    for match in re.finditer(
        r"(?im)^\s*(?:[-*•]\s*)?(-[^\s=]+)\s*=\s*([^\r\n]+)", answer
    ):
        suffix_description = match.group(2).strip()
        suffix_function = re.sub(r"\s*\([^)]*\)\s*$", "", suffix_description).strip()
        if suffix_function:
            suffixes.append({"suffix": match.group(1), "function": suffix_function})

    stem_changes = []
    base_form_match = re.search(
        r"(?im)^\s*(?:[-*•]\s*)?([^\W_]+)\s*=\s*.+\b(?:verb|stem)\b", answer
    )
    if base_form_match and base_form_match.group(1).casefold() != lemma.casefold():
        stem_changes.append(f"Form uses the stem {base_form_match.group(1)}")

    result = save_finnish_word_analysis(
        word_form=word_form,
        lemma=lemma,
        part_of_speech=part_of_speech,
        meaning=re.sub(r"[\"“”]", "", meaning_match.group(1)).strip(),
        noun_type=None,
        verb_type=verb_type,
        suffixes=suffixes,
        grammatical_features=grammatical_features,
        stem_changes=stem_changes,
        word_forms=[],
        subject=subject,
        article_id=article_id,
    )
    if "error" in result:
        logger.error(
            "Could not cache the Tutor's parsed vocabulary analysis: %s",
            result["error"],
        )
        return False
    return True


def find_cached_vocabulary(
    question: str, article_id: int | None
) -> tuple[str, dict] | None:
    words = re.findall(r"[^\W_]+(?:[-'][^\W_]+)*", question, flags=re.UNICODE)
    for word in words:
        if len(word) < 2:
            continue
        analysis = VocabularyRepository.get_word_analysis_for_form(
            word, article_id=article_id
        )
        if analysis is not None and analysis.get("meaning"):
            return word, analysis
    return None
