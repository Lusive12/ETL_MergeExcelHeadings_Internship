from pathlib import Path
import pandas as pd

class Exporter:
    def __init__(self):
        # No config needed any more
        pass

    def export(self, dataframe, output_path: str):
        output_file = Path(output_path)
        # Ensure parent folder exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # If the file already exists, try to delete it first
        if output_file.exists():
            try:
                output_file.unlink()          # remove the old file
            except PermissionError:
                # If it’s still locked, raise a clear error
                raise PermissionError(
                    f"Unable to delete existing file {output_file}. "
                    "Make sure it is not open in another program."
                )

        # Write the new Excel file
        dataframe.to_excel(output_file, index=False)
        return output_file
