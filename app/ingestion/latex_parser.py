import re
from typing import List

from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class LatexParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            latex = f.read()

        latex = remove_comments(latex)

        blocks = []
        block_counter = 1

        formula_patterns = [
            ("equation", r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}"),
            ("align", r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}"),
            ("display_math", r"\\\[(.*?)\\\]")
        ]

        for env_name, pattern in formula_patterns:
            for match in re.finditer(pattern, latex, flags=re.DOTALL):
                formula = " ".join(match.group(1).split()).strip()
                if not formula:
                    continue

                blocks.append(
                    RichContentBlock(
                        block_id=f"{document_id}_latex_block_{block_counter}",
                        document_id=document_id,
                        content_type="formula",
                        content=formula,
                        page_number=None,
                        section_title=None,
                        source_file_name=source_file_name,
                        metadata={
                            "parser": "LatexParser",
                            "original_format": "tex",
                            "latex_environment": env_name
                        }
                    )
                )
                block_counter += 1

                latex = latex.replace(match.group(0), " ")

        text = clean_latex_text(latex)

        if text:
            blocks.append(
                RichContentBlock(
                    block_id=f"{document_id}_latex_block_{block_counter}",
                    document_id=document_id,
                    content_type="text",
                    content=text,
                    page_number=None,
                    section_title=None,
                    source_file_name=source_file_name,
                    metadata={
                        "parser": "LatexParser",
                        "original_format": "tex"
                    }
                )
            )

        return blocks


def remove_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lines.append(re.sub(r"(?<!\\)%.*", "", line))
    return "\n".join(lines)


def clean_latex_text(text: str) -> str:
    text = re.sub(r"\\documentclass(\[.*?\])?\{.*?\}", " ", text)
    text = re.sub(r"\\usepackage(\[.*?\])?\{.*?\}", " ", text)
    text = re.sub(r"\\begin\{document\}", " ", text)
    text = re.sub(r"\\end\{document\}", " ", text)
    text = re.sub(r"\\(section|subsection|subsubsection)\*?\{(.*?)\}", r"\2\n\n", text)
    text = re.sub(r"\\textbf\{(.*?)\}", r"\1", text)
    text = re.sub(r"\\textit\{(.*?)\}", r"\1", text)
    text = re.sub(r"\\cite\{.*?\}", "[citation]", text)
    text = re.sub(r"\\label\{.*?\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(\[.*?\])?(\{.*?\})?", " ", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()
