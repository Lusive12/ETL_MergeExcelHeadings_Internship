import pandas as pd


class Transformer:

    @staticmethod
    def normalize(df):

        df.columns = [

            str(c).strip()

            for c in df.columns

        ]

        for c in df.columns:

            df[c] = (

                df[c]

                .astype(str)

                .str.strip()

                .replace({

                    "nan": None,

                    "None": None,

                    "NULL": None,

                    "N/A": None,

                    "-": None

                })

            )

        return df