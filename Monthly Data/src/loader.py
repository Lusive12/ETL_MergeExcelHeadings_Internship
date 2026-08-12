import pandas as pd
from pathlib import Path


class ExcelLoader:

    def __init__(self, config):

        self.config = config

    def load(self, source_name):

        filename = self.config["sources"][source_name]

        path = Path("input") / filename

        df = pd.read_excel(path, dtype=str)

        return df