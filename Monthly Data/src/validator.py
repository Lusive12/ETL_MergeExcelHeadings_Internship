from pathlib import Path


class Validator:

    def __init__(self, config, mapping):

        self.config = config
        self.mapping = mapping

    def validate_file(self, source_name):

        filename = self.config["sources"][source_name]

        path = Path("input") / filename

        if not path.exists():

            raise FileNotFoundError(f"{filename} not found.")

    def validate_columns(self, source_name, dataframe):

        required = [col for col, src in self.mapping.items() if src == source_name]
        
        primary_key = self.config["primary_key"]
        if primary_key not in required:
            required.append(primary_key)

        missing = [

            c for c in required

            if c not in dataframe.columns

        ]

        if missing:

            raise Exception(

                f"{source_name} missing columns : {missing}"

            )