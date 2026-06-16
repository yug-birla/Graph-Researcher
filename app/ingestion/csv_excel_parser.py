from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from app.core.config import settings
from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class CsvExcelParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        extension = Path(source_file_name).suffix.lower()

        if extension == ".csv":
            sheets = {"csv": read_csv_safely(file_path)}
        elif extension in [".xlsx", ".xls"]:
            sheets = pd.read_excel(file_path, sheet_name=None)
        else:
            raise ValueError(f"Unsupported table file extension: {extension}")

        blocks = []
        block_counter = 1

        for sheet_name, dataframe in sheets.items():
            dataframe = clean_dataframe(dataframe)

            if dataframe.empty:
                continue

            for start_row in range(0, len(dataframe), settings.MAX_ROWS_PER_TABLE_BLOCK):
                end_row = min(start_row + settings.MAX_ROWS_PER_TABLE_BLOCK, len(dataframe))
                batch_df = dataframe.iloc[start_row:end_row]

                table_json = batch_df.to_dict(orient="records")
                markdown_table = dataframe_to_markdown(batch_df)

                blocks.append(
                    RichContentBlock(
                        block_id=f"{document_id}_table_block_{block_counter}",
                        document_id=document_id,
                        content_type="table",
                        content=markdown_table,
                        page_number=None,
                        section_title=f"Sheet: {sheet_name}",
                        source_file_name=source_file_name,
                        metadata={
                            "parser": "CsvExcelParser",
                            "original_format": extension,
                            "sheet_name": sheet_name,
                            "table_json": table_json,
                            "columns": list(batch_df.columns),
                            "row_start": start_row + 1,
                            "row_end": end_row,
                            "total_rows_in_sheet": len(dataframe),
                            "max_rows_per_table_block": settings.MAX_ROWS_PER_TABLE_BLOCK
                        }
                    )
                )
                block_counter += 1

        return blocks


def read_csv_safely(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="latin1")


def clean_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()
    dataframe = dataframe.dropna(how="all")
    dataframe = dataframe.dropna(axis=1, how="all")
    dataframe.columns = [
        str(column).strip() if str(column).strip() else f"column_{index + 1}"
        for index, column in enumerate(dataframe.columns)
    ]
    dataframe = dataframe.fillna("")

    for column in dataframe.columns:
        dataframe[column] = dataframe[column].astype(str)

    return dataframe


def dataframe_to_markdown(dataframe: pd.DataFrame) -> str:
    columns = [str(column) for column in dataframe.columns]
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")

    for _, row in dataframe.iterrows():
        values = [
            str(row[column]).replace("|", "\\|").replace("\n", " ").strip()
            for column in columns
        ]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)
