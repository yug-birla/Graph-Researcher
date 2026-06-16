from typing import List
from bs4 import BeautifulSoup

from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class HtmlParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        blocks = []
        block_counter = 1
        current_section_title = None

        for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote", "pre", "code", "table"]):
            tag_name = element.name.lower()

            if tag_name in ["h1", "h2", "h3", "h4"]:
                text = clean_text(element.get_text(" ", strip=True))
                current_section_title = text
                content_type = "text"

            elif tag_name == "table":
                rows = []
                for tr in element.find_all("tr"):
                    cells = [
                        clean_text(cell.get_text(" ", strip=True))
                        for cell in tr.find_all(["th", "td"])
                    ]
                    if cells:
                        rows.append(cells)

                text = rows_to_markdown(rows)
                content_type = "table"

            elif tag_name in ["pre", "code"]:
                text = element.get_text("\n", strip=True)
                content_type = "code"

            else:
                text = clean_text(element.get_text(" ", strip=True))
                content_type = "text"

            if not text:
                continue

            blocks.append(
                RichContentBlock(
                    block_id=f"{document_id}_html_block_{block_counter}",
                    document_id=document_id,
                    content_type=content_type,
                    content=text,
                    page_number=None,
                    section_title=current_section_title,
                    source_file_name=source_file_name,
                    metadata={
                        "parser": "HtmlParser",
                        "original_format": "html",
                        "html_tag": tag_name
                    }
                )
            )
            block_counter += 1

        return blocks


def clean_text(text: str) -> str:
    return " ".join(text.split())


def rows_to_markdown(rows):
    if not rows:
        return ""

    header = rows[0]
    body = rows[1:]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for row in body:
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        if len(row) > len(header):
            row = row[:len(header)]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)
