from typing import List
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class DocxParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        doc = Document(file_path)
        blocks = []
        block_counter = 1
        current_section_title = None

        for element in doc.element.body:
            if isinstance(element, CT_P):
                paragraph = Paragraph(element, doc)
                text = paragraph.text.strip()

                if not text:
                    continue

                style_name = paragraph.style.name if paragraph.style else ""

                if style_name.startswith("Heading"):
                    current_section_title = text

                blocks.append(
                    RichContentBlock(
                        block_id=f"{document_id}_docx_block_{block_counter}",
                        document_id=document_id,
                        content_type="text",
                        content=text,
                        page_number=None,
                        section_title=current_section_title,
                        source_file_name=source_file_name,
                        metadata={
                            "parser": "DocxParser",
                            "original_format": "docx",
                            "docx_element_type": "paragraph",
                            "style": style_name
                        }
                    )
                )
                block_counter += 1

            elif isinstance(element, CT_Tbl):
                table = Table(element, doc)
                table_data = extract_table_as_rows(table)
                markdown_table = rows_to_markdown(table_data)

                if not markdown_table:
                    continue

                blocks.append(
                    RichContentBlock(
                        block_id=f"{document_id}_docx_block_{block_counter}",
                        document_id=document_id,
                        content_type="table",
                        content=markdown_table,
                        page_number=None,
                        section_title=current_section_title,
                        source_file_name=source_file_name,
                        metadata={
                            "parser": "DocxParser",
                            "original_format": "docx",
                            "docx_element_type": "table",
                            "table_json": table_data
                        }
                    )
                )
                block_counter += 1

        return blocks


def extract_table_as_rows(table: Table):
    rows = []

    for row in table.rows:
        rows.append([cell.text.strip() for cell in row.cells])

    return rows


def rows_to_markdown(rows):
    if not rows:
        return ""

    header = rows[0]
    body = rows[1:]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for row in body:
        row = normalize_row(row, len(header))
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def normalize_row(row, expected_len):
    if len(row) < expected_len:
        row = row + [""] * (expected_len - len(row))
    if len(row) > expected_len:
        row = row[:expected_len]
    return row
