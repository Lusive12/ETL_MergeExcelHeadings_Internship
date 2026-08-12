import pandas as pd
from src.loader import ExcelLoader
from src.validator import Validator
from src.transformer import Transformer
from src.exporter import Exporter
from src.logger import setup_logger
from src.utils import load_json, ensure_folder


config = load_json("config/config.json")
mapping = load_json("config/mapping.json")

logger = setup_logger("logs")

ensure_folder("output")

loader = ExcelLoader(config)

validator = Validator(config, mapping)

exporter = Exporter()

logger.info("Starting ETL Process")

dataframes = {}

for source_name in config["sources"]:
    logger.info(f"Loading {source_name}")
    
    validator.validate_file(source_name)
    df = loader.load(source_name)
    validator.validate_columns(source_name, df)
    
    df = Transformer.normalize(df)
    dataframes[source_name] = df

logger.info("Merging dataframes")
primary_key = config["primary_key"]
merged_df = None

for source_name, df in dataframes.items():
    if merged_df is None:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on=primary_key, how="outer")

logger.info("Selecting output columns and exporting")
output_columns = config["output_columns"]
final_df = merged_df[output_columns]

exporter.export(final_df, "output/Output_Report.xlsx")

logger.info("ETL completed successfully.")