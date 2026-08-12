import json
from pathlib import Path


def load_json(path):

    with open(path, "r", encoding="utf8") as f:

        return json.load(f)


def ensure_folder(folder):

    Path(folder).mkdir(parents=True, exist_ok=True)