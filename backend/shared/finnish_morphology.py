import re

_VOWELS = "aäoöuüy"
_CASES = (
    "nominative",
    "genitive",
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
)

_GRADATION = (
    ("kk", "k"),
    ("pp", "p"),
    ("tt", "t"),
    ("mp", "mm"),
    ("nt", "nn"),
    ("nk", "ng"),
    ("lt", "ll"),
    ("rt", "rr"),
)


def _harmonic_vowel(word: str) -> str:
    return "ä" if any(character in word for character in "äöy") else "a"


def _generate_noun(lemma: str) -> list[dict]:
    word = lemma.casefold()
    harmony = _harmonic_vowel(word)
    if not word or word[-1] not in _VOWELS:
        return []

    stem = word
    weak_stem = stem
    for strong, weak in _GRADATION:
        if stem.endswith(strong):
            weak_stem = stem[: -len(strong)] + weak
            break
    else:
        if stem.endswith("k") and len(stem) > 1:
            weak_stem = stem[:-1]

    if word.endswith("nen"):
        singular_genitive = word[:-3] + "sen"
        singular_partitive = word[:-3] + "sta"
        singular_inessive = word[:-3] + "sessa"
        singular_elative = word[:-3] + "sesta"
        singular_illative = word[:-3] + "seen"
        plural_stem = word[:-3] + "si"
        plural_genitive = word[:-3] + "sten"
        plural_partitive = word[:-3] + "sia"
        plural_inessive = word[:-3] + "sissa"
        plural_elative = word[:-3] + "sista"
        plural_illative = word[:-3] + "siin"
        plural_adessive = word[:-3] + "silla"
        plural_ablative = word[:-3] + "silta"
        plural_allative = word[:-3] + "sille"
        plural_essive = word[:-3] + "sina"
        plural_translative = word[:-3] + "siksi"
        plural_abessive = word[:-3] + "sitta"
        plural_comitative = word[:-3] + "sine"
        plural_instructive = word[:-3] + "sin"
        singular_adessive = word[:-3] + "sella"
        singular_ablative = word[:-3] + "selta"
        singular_allative = word[:-3] + "selle"
        singular_essive = word[:-3] + "sena"
        singular_translative = word[:-3] + "seksi"
        singular_abessive = word[:-3] + "setta"
        singular_comitative = word[:-3] + "sine"
        singular_instructive = word[:-3] + "sen"
    elif word.endswith("e"):
        singular_genitive = weak_stem + "en"
        singular_partitive = word + "tta"
        singular_inessive = word + "essa"
        singular_elative = word + "esta"
        singular_illative = word + "eseen"
        plural_stem = word + "i"
        plural_genitive = word + "iden"
        plural_partitive = word + "ita"
        plural_inessive = word + "issa"
        plural_elative = word + "ista"
        plural_illative = word + "isiin"
        singular_adessive = word + "ella"
        singular_ablative = word + "elta"
        singular_allative = word + "elle"
        singular_essive = word + "ena"
        singular_translative = word + "eksi"
        singular_abessive = word + "etta"
        singular_comitative = word + "ine"
        singular_instructive = word + "en"
        plural_adessive = word + "illa"
        plural_ablative = word + "ilta"
        plural_allative = word + "ille"
        plural_essive = word + "ina"
        plural_translative = word + "iksi"
        plural_abessive = word + "itta"
        plural_comitative = word + "ine"
        plural_instructive = word + "in"
    elif word.endswith("i"):
        known_old_i = {
            "koti": {
                "gen": "kodin",
                "part": "kotia",
                "iness": "kodissa",
                "elative": "kodista",
                "illative": "kotiin",
                "plural_stem": "koto",
                "plural_gen": "kotien",
                "plural_part": "kotoja",
            },
            "vesi": {
                "gen": "veden",
                "part": "vettä",
                "iness": "vedessä",
                "elative": "vedestä",
                "illative": "veteen",
                "plural_stem": "vesi",
                "plural_gen": "vesien",
                "plural_part": "vesiä",
            },
        }
        if word in known_old_i:
            pattern = known_old_i[word]
            singular_genitive = pattern["gen"]
            singular_partitive = pattern["part"]
            singular_inessive = pattern["iness"]
            singular_elative = pattern["elative"]
            singular_illative = pattern["illative"]
            plural_stem = pattern["plural_stem"]
            plural_genitive = pattern["plural_gen"]
            plural_partitive = pattern["plural_part"]
            plural_inessive = plural_stem + "issa"
            plural_elative = plural_stem + "ista"
            plural_illative = plural_stem + "iin"
            singular_adessive = singular_genitive[:-1] + "lla"
            singular_ablative = singular_genitive[:-1] + "lta"
            singular_allative = singular_genitive[:-1] + "lle"
            singular_essive = singular_genitive[:-1] + "na"
            singular_translative = singular_genitive[:-1] + "ksi"
            singular_abessive = singular_genitive[:-1] + "tta"
            singular_comitative = singular_genitive[:-1] + "ine"
            singular_instructive = singular_genitive
            plural_adessive = plural_stem + "illa"
            plural_ablative = plural_stem + "ilta"
            plural_allative = plural_stem + "ille"
            plural_essive = plural_stem + "ina"
            plural_translative = plural_stem + "iksi"
            plural_abessive = plural_stem + "itta"
            plural_comitative = plural_stem + "ine"
            plural_instructive = plural_stem + "in"
        else:
            # New i-stem nouns, e.g. taksi: taksin, taksia, takseja.
            singular_genitive = word + "n"
            singular_partitive = word + "a" if harmony == "a" else word + "ä"
            singular_inessive = word + "ssa" if harmony == "a" else word + "ssä"
            singular_elative = word + "sta" if harmony == "a" else word + "stä"
            singular_illative = word + "in"
            plural_stem = word[:-1] + "e"
            plural_genitive = plural_stem + "n"
            plural_partitive = plural_stem + "ja"
            plural_inessive = plural_stem + "issa"
            plural_elative = plural_stem + "ista"
            plural_illative = plural_stem + "iin"
            singular_adessive = word + ("lla" if harmony == "a" else "llä")
            singular_ablative = word + ("lta" if harmony == "a" else "ltä")
            singular_allative = word + ("lle")
            singular_essive = word + ("na" if harmony == "a" else "nä")
            singular_translative = word + ("ksi")
            singular_abessive = word + ("tta" if harmony == "a" else "ttä")
            singular_comitative = word + "ine"
            singular_instructive = singular_genitive
            plural_adessive = plural_stem + "illa"
            plural_ablative = plural_stem + "ilta"
            plural_allative = plural_stem + "ille"
            plural_essive = plural_stem + "ina"
            plural_translative = plural_stem + "iksi"
            plural_abessive = plural_stem + "itta"
            plural_comitative = plural_stem + "ine"
            plural_instructive = plural_stem + "in"
    else:
        singular_genitive = weak_stem + "n"
        singular_partitive = word + harmony
        singular_inessive = weak_stem + ("ssa" if harmony == "a" else "ssä")
        singular_elative = weak_stem + ("sta" if harmony == "a" else "stä")
        singular_illative = word + word[-1] + "n"
        plural_stem = weak_stem + "i"
        plural_genitive = word + "jen"
        plural_partitive = plural_stem + "ja"
        plural_inessive = plural_stem + ("ssa" if harmony == "a" else "ssä")
        plural_elative = plural_stem + ("sta" if harmony == "a" else "stä")
        plural_illative = plural_stem + "hin"
        singular_adessive = weak_stem + ("lla" if harmony == "a" else "llä")
        singular_ablative = weak_stem + ("lta" if harmony == "a" else "ltä")
        singular_allative = weak_stem + "lle"
        singular_essive = weak_stem + ("na" if harmony == "a" else "nä")
        singular_translative = weak_stem + "ksi"
        singular_abessive = weak_stem + ("tta" if harmony == "a" else "ttä")
        singular_comitative = weak_stem + "ine"
        singular_instructive = singular_genitive
        plural_adessive = plural_stem + "illa"
        plural_ablative = plural_stem + "ilta"
        plural_allative = plural_stem + "ille"
        plural_essive = plural_stem + "ina"
        plural_translative = plural_stem + "iksi"
        plural_abessive = plural_stem + "itta"
        plural_comitative = plural_stem + "ine"
        plural_instructive = plural_stem + "in"

    endings = {
        "genitive": (singular_genitive, plural_genitive),
        "partitive": (singular_partitive, plural_partitive),
        "inessive": (singular_inessive, plural_inessive),
        "elative": (singular_elative, plural_elative),
        "illative": (singular_illative, plural_illative),
        "adessive": (singular_adessive, plural_adessive),
        "ablative": (singular_ablative, plural_ablative),
        "allative": (singular_allative, plural_allative),
        "essive": (singular_essive, plural_essive),
        "translative": (singular_translative, plural_translative),
        "abessive": (singular_abessive, plural_abessive),
        "comitative": (singular_comitative, plural_comitative),
        "instructive": (singular_instructive, plural_instructive),
    }
    forms = [
        {
            "part_of_speech": "noun",
            "features": {"case": "nominative", "number": "singular"},
            "form": word,
        },
        {
            "part_of_speech": "noun",
            "features": {"case": "nominative", "number": "plural"},
            "form": plural_stem + "t",
        },
    ]
    for case in _CASES[1:]:
        singular, plural = endings[case]
        forms.extend(
            (
                {
                    "part_of_speech": "noun",
                    "features": {"case": case, "number": "singular"},
                    "form": singular,
                },
                {
                    "part_of_speech": "noun",
                    "features": {"case": case, "number": "plural"},
                    "form": plural,
                },
            )
        )
    return forms


def _verb_type(lemma: str) -> int | None:
    word = lemma.casefold()
    if word.endswith(("eta", "etä")):
        return 6
    if word.endswith(("ita", "itä")):
        return 5
    if re.search(r"[aeiouyäö]ta$", word) or re.search(r"[aeiouyäö]tä$", word):
        return 4
    if word.endswith(("da", "dä")):
        return 2
    if word.endswith(("la", "lä", "na", "nä", "ra", "rä", "sta", "stä")):
        return 3
    if word.endswith(("a", "ä")):
        return 1
    return None


def _append_form(
    forms: list[dict], lemma: str, features: dict[str, str], form: str
) -> None:
    if form:
        forms.append({"part_of_speech": "verb", "features": features, "form": form})


def _generate_verb(lemma: str, requested_type: int | None) -> list[dict]:
    word = lemma.casefold()
    detected_type = _verb_type(word)
    if detected_type is None or (
        requested_type is not None and requested_type != detected_type
    ):
        return []

    harmony = _harmonic_vowel(word)
    a = harmony
    if detected_type == 1:
        present_stem = word[:-1]
        weak_stem = present_stem
        for strong, weak in _GRADATION:
            if weak_stem.endswith(strong):
                weak_stem = weak_stem[: -len(strong)] + weak
                break
        if present_stem.endswith("k") and len(present_stem) > 1:
            weak_stem = present_stem[:-1]
    elif detected_type == 2:
        present_stem = word[:-2]
        weak_stem = present_stem
    elif detected_type == 3:
        infinitive_ending = next(
            (
                ending
                for ending in ("la", "lä", "na", "nä", "ra", "rä", "sta", "stä")
                if word.endswith(ending)
            ),
            None,
        )
        if infinitive_ending is None:
            return []
        ending_size = len(infinitive_ending)
        present_stem = (
            word[:-ending_size]
            + {
                "la": "le",
                "lä": "le",
                "na": "ne",
                "nä": "ne",
                "ra": "re",
                "rä": "re",
                "sta": "se",
                "stä": "se",
            }[infinitive_ending]
        )
        weak_stem = present_stem
    elif detected_type == 4:
        present_stem = word[:-2] + ("a" if word.endswith("ta") else "ä")
        weak_stem = present_stem
    elif detected_type == 5:
        present_stem = word[:-2] + "tse"
        weak_stem = present_stem
    else:
        present_stem = word[:-2] + "ne"
        weak_stem = present_stem

    harmony_endings = {
        "1sg": "n",
        "2sg": "t",
        "1pl": "mme",
        "2pl": "tte",
        "3pl": "vat" if a == "a" else "vät",
    }
    if detected_type == 1:
        person_forms = {
            "1sg": present_stem + "n",
            "2sg": present_stem + "t",
            "3sg": (
                present_stem + present_stem[-1]
                if present_stem[-1] in _VOWELS
                else present_stem
            ),
            "1pl": present_stem + "mme",
            "2pl": present_stem + "tte",
            "3pl": weak_stem + harmony_endings["3pl"],
        }
        negative_stem = present_stem
    elif detected_type == 2:
        person_forms = {
            "1sg": present_stem + "n",
            "2sg": present_stem + "t",
            "3sg": present_stem,
            "1pl": present_stem + "mme",
            "2pl": present_stem + "tte",
            "3pl": present_stem + harmony_endings["3pl"],
        }
        negative_stem = present_stem
    elif detected_type == 3:
        stem = present_stem[:-1]
        person_forms = {
            "1sg": stem + "en",
            "2sg": stem + "et",
            "3sg": present_stem + "e",
            "1pl": present_stem + "mme",
            "2pl": present_stem + "tte",
            "3pl": present_stem + harmony_endings["3pl"],
        }
        negative_stem = present_stem
    elif detected_type == 4:
        stem = word[:-2]
        if stem.endswith(("a", "ä")):
            endings = {
                "1sg": "an" if a == "a" else "än",
                "2sg": "at" if a == "a" else "ät",
                "3sg": a,
                "1pl": "amme" if a == "a" else "ämme",
                "2pl": "atte" if a == "a" else "ätte",
                "3pl": "avat" if a == "a" else "ävät",
            }
            person_forms = {person: stem + ending for person, ending in endings.items()}
        else:
            person_forms = {
                "1sg": present_stem + "n",
                "2sg": present_stem + "t",
                "3sg": present_stem + a,
                "1pl": present_stem + "mme",
                "2pl": present_stem + "tte",
                "3pl": present_stem + harmony_endings["3pl"],
            }
        negative_stem = present_stem
    elif detected_type == 5:
        stem = present_stem[:-1]
        person_forms = {
            "1sg": stem + "en",
            "2sg": stem + "et",
            "3sg": present_stem + "e",
            "1pl": stem + "emme",
            "2pl": stem + "ette",
            "3pl": present_stem + harmony_endings["3pl"],
        }
        negative_stem = present_stem
    else:
        stem = present_stem[:-2]
        person_forms = {
            "1sg": stem + "n",
            "2sg": stem + "t",
            "3sg": present_stem + "e",
            "1pl": stem + "nemme",
            "2pl": stem + "nette",
            "3pl": present_stem + harmony_endings["3pl"],
        }
        negative_stem = present_stem

    forms: list[dict] = []
    for person, form in person_forms.items():
        _append_form(
            forms,
            word,
            {
                "mood": "indicative",
                "tense": "present",
                "voice": "active",
                "polarity": "positive",
                "person": person,
            },
            form,
        )
        negative_person = {
            "1sg": "en",
            "2sg": "et",
            "3sg": "ei",
            "1pl": "emme",
            "2pl": "ette",
            "3pl": "eivät",
        }[person]
        _append_form(
            forms,
            word,
            {
                "mood": "indicative",
                "tense": "present",
                "voice": "active",
                "polarity": "negative",
                "person": person,
            },
            f"{negative_person} {negative_stem}",
        )

    if detected_type == 1:
        passive_present = word[:-1] + ("taan" if a == "a" else "tään")
        passive_negative = word[:-1] + ("ta" if a == "a" else "tä")
    elif detected_type == 2:
        passive_present = word[:-2] + ("daan" if a == "a" else "dään")
        passive_negative = word
    elif detected_type == 3:
        passive_present = word[:-1] + ("aan" if a == "a" else "ään")
        passive_negative = word
    else:
        passive_present = word[:-2] + ("taan" if a == "a" else "tään")
        passive_negative = word
    _append_form(
        forms,
        word,
        {
            "mood": "indicative",
            "tense": "present",
            "voice": "passive",
            "polarity": "positive",
        },
        passive_present,
    )
    _append_form(
        forms,
        word,
        {
            "mood": "indicative",
            "tense": "present",
            "voice": "passive",
            "polarity": "negative",
        },
        f"ei {passive_negative}",
    )

    irregular_past_stems = {
        "syödä": "söi",
        "juoda": "joi",
        "saada": "sai",
        "voida": "voi",
        "käydä": "kävi",
        "uida": "ui",
        "tehdä": "teki",
        "tulla": "tuli",
        "mennä": "meni",
        "olla": "oli",
        "nousta": "nousi",
    }
    if word in irregular_past_stems:
        past_stem = irregular_past_stems[word]
    elif detected_type == 4:
        past_stem = word[:-2] + "si"
    elif detected_type == 5:
        past_stem = present_stem[:-1] + "i"
    elif detected_type == 6:
        past_stem = present_stem[:-2] + "ni"
    else:
        past_stem = present_stem + "i"

    past_endings = {
        "1sg": "n",
        "2sg": "t",
        "3sg": "",
        "1pl": "mme",
        "2pl": "tte",
        "3pl": "vat" if a == "a" else "vät",
    }
    for person, ending in past_endings.items():
        if person == "3sg" and detected_type in {1, 2}:
            form = past_stem
        else:
            form = past_stem + ending
        _append_form(
            forms,
            word,
            {
                "mood": "indicative",
                "tense": "past",
                "voice": "active",
                "polarity": "positive",
                "person": person,
            },
            form,
        )
    if detected_type == 1:
        past_passive = word[:-1] + ("ttiin" if a == "a" else "ttiin")
    elif detected_type == 2 or detected_type == 3:
        past_passive = word[:-2] + "tiin"
    else:
        past_passive = word[:-2] + "ttiin"
    _append_form(
        forms,
        word,
        {
            "mood": "indicative",
            "tense": "past",
            "voice": "passive",
            "polarity": "positive",
        },
        past_passive,
    )
    return forms


def _generate_adjective(lemma: str) -> list[dict]:
    forms = _generate_noun(lemma)
    for form in forms:
        form["part_of_speech"] = "adjective"
    word = lemma.casefold()
    if word.endswith(("a", "ä")) and len(word) > 2:
        comparative = word[:-1] + ("ampi" if word.endswith("a") else "ämpi")
        superlative = word[:-1] + ("in" if word.endswith("a") else "in")
        for degree, degree_stem in (
            ("comparative", comparative),
            ("superlative", superlative),
        ):
            forms.append(
                {
                    "part_of_speech": "adjective",
                    "features": {
                        "degree": degree,
                        "case": "nominative",
                        "number": "singular",
                    },
                    "form": degree_stem,
                }
            )
    return forms


def generate_paradigm(
    lemma: str, part_of_speech: str, verb_type: int | None = None
) -> list[dict]:
    """Generate forms with transparent rules; unknown patterns return none."""
    normalized_lemma = lemma.strip().casefold()
    normalized_pos = part_of_speech.strip().casefold()
    if not normalized_lemma:
        return []

    if normalized_pos in {"verb", "verbi"}:
        return _generate_verb(normalized_lemma, verb_type)
    if normalized_pos in {"noun", "substantiivi", "n"}:
        return _generate_noun(normalized_lemma)
    if normalized_pos in {"adjective", "adjektiivi", "adj"}:
        return _generate_adjective(normalized_lemma)
    return []


def infer_verb_type(lemma: str) -> int | None:
    """Return the rule-based verb type when the infinitive ending is known."""
    return _verb_type(lemma)
