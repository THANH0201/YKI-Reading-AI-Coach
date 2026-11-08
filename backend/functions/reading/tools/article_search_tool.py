import re


def terms_match(query_term: str, article_term: str) -> bool:
    if query_term == article_term:
        return True

    shorter_length = min(len(query_term), len(article_term))

    if shorter_length < 6:
        return False

    prefix_length = 0

    for q, a in zip(query_term, article_term):
        if q != a:
            break
        prefix_length += 1

    return prefix_length >= shorter_length - 2


def search_article(
    article_content: str,
    query: str,
) -> dict:

    query_terms = {
        term.casefold()
        for term in re.findall(r"[^\W_]+", query, flags=re.UNICODE)
        if len(term) > 2
    }

    if not query_terms:
        return {"query": query, "matches": []}

    sentences = re.split(r"(?<=[.!?])\s+|\r?\n+", article_content)

    ranked_matches = []

    for position, sentence in enumerate(sentences):
        clean_sentence = sentence.strip()

        if not clean_sentence:
            continue

        sentence_terms = {
            term.casefold()
            for term in re.findall(r"[^\W_]+", clean_sentence, flags=re.UNICODE)
        }

        overlap = sum(
            any(terms_match(term, candidate) for candidate in sentence_terms)
            for term in query_terms
        )

        if overlap:
            ranked_matches.append((overlap, position, clean_sentence))

    ranked_matches.sort(key=lambda x: (-x[0], x[1]))

    return {"query": query, "matches": [match[2] for match in ranked_matches[:3]]}
