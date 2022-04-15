import json
import pathlib
from GenerateCSVs.elr import extract_loinc_lab
from GenerateCSVs.elr import elr_to_csv
import pytest


def test_extract_loinc_lab():
    covid_obs = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "observation.json")
    )
    non_covid_obs = {
        "resourceType": "Observation",
        "id": "some-id",
        "status": "final",
        "code": {
            "coding": [
                {
                    "code": "123456",
                    "display": "some sorta health thing",
                    "system": "http://blah.org",
                }
            ]
        },
    }
    assert extract_loinc_lab(non_covid_obs) == []
    assert extract_loinc_lab(covid_obs) == [
        "94500-6",
        "Positive",
        "2022-01-01T01:01:00",
    ]


@pytest.fixture()
def bundle():
    return json.load(open(pathlib.Path(__file__).parent / "assets" / "elr.json"))


def test_elr_to_csv(bundle):
    generated_rows = elr_to_csv(bundle)
    num_rows = 0
    for row in generated_rows:
        num_rows += 1
        assert row == [
            "",
            "John",
            "Shepard",
            "2153-11-07",
            "Male",
            "1234 Silversun Strip",
            "Zakera Ward",
            "Citadel",
            "99999",
            "",
            "",
            "White",
            "",
            "94500-6",
            "Positive",
            "2022-01-01T01:01:00",
        ]
    assert num_rows == 1
