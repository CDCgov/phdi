import json
import pathlib


def read_json_from_assets(filename: str):
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))
