import json
import pathlib
from GenerateCSVs.vxu import vxu_to_csv
import pytest


@pytest.fixture()
def bundle():
    return json.load(open(pathlib.Path(__file__).parent / "assets" / "vxu.json"))


def test_vxu_to_csv(bundle):
    generated_rows = vxu_to_csv(bundle)
    assert generated_rows == [
        [
            "",
            "JOHN",
            "DOE",
            "1970-01-01",
            "male",
            "123 TEST CT",
            "TEST",
            "VA",
            "23222",
            "",
            "",
            "2106-3",
            "",
            "197",
            "INFLUENZA, HIGH-DOSE SEASONAL, QUADRIVALENT, PRESERVATIVE FREE",
            "2018-11-12",
        ],
        [
            "",
            "JOHN",
            "DOE",
            "1970-01-01",
            "male",
            "123 TEST CT",
            "TEST",
            "VA",
            "23222",
            "",
            "",
            "2106-3",
            "",
            "208",
            "COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose (Pfizer-BioNTech)",
            "2021-10-04",
        ],
    ]
