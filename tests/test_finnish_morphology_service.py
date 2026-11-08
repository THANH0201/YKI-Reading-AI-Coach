import pytest

from services.finnish_morphology_service import generate_paradigm


@pytest.mark.parametrize(
    ("lemma", "expected_forms", "expected_negative"),
    [
        (
            "avata",
            {
                "1sg": "avaan",
                "2sg": "avaat",
                "3sg": "avaa",
                "1pl": "avaamme",
                "2pl": "avaatte",
                "3pl": "avaavat"
            },
            {
                "1sg": "en avaa",
                "2sg": "et avaa",
                "3sg": "ei avaa",
                "1pl": "emme avaa",
                "2pl": "ette avaa",
                "3pl": "eivät avaa"
            }
        ),
        (
            "haluta",
            {
                "1sg": "haluan",
                "2sg": "haluat",
                "3sg": "haluaa",
                "1pl": "haluamme",
                "2pl": "haluatte",
                "3pl": "haluavat"
            },
            {
                "1sg": "en halua",
                "2sg": "et halua",
                "3sg": "ei halua",
                "1pl": "emme halua",
                "2pl": "ette halua",
                "3pl": "eivät halua"
            }
        )
    ]
)
def test_type_four_verb_present_forms(
    lemma,
    expected_forms,
    expected_negative
):
    forms = generate_paradigm(lemma, "verb")
    present_forms = {
        form["features"]["person"]: form["form"]
        for form in forms
        if form["features"].get("tense") == "present"
        and form["features"].get("voice") == "active"
        and form["features"].get("polarity") == "positive"
    }
    negative_forms = {
        form["features"]["person"]: form["form"]
        for form in forms
        if form["features"].get("tense") == "present"
        and form["features"].get("voice") == "active"
        and form["features"].get("polarity") == "negative"
    }

    assert present_forms == expected_forms
    assert negative_forms == expected_negative
