from typing import Optional

from app.ingestion.base_parser import BaseParser
from app.ingestion.txt_parser import TxtParser
from app.ingestion.markdown_parser import MarkdownParser
from app.ingestion.pdf_parser import PdfParser
from app.ingestion.docx_parser import DocxParser
from app.ingestion.csv_excel_parser import CsvExcelParser
from app.ingestion.html_parser import HtmlParser
from app.ingestion.latex_parser import LatexParser
from app.ingestion.image_parser import ImageParser


class ParserRegistry:

    def __init__(self):
        self.parsers = {}

    def register(self, file_type: str, parser: BaseParser):
        self.parsers[file_type] = parser

    def get_parser(self, file_type: str) -> Optional[BaseParser]:
        return self.parsers.get(file_type)


parser_registry = ParserRegistry()

parser_registry.register("txt", TxtParser())
parser_registry.register("markdown", MarkdownParser())
parser_registry.register("pdf", PdfParser())
parser_registry.register("docx", DocxParser())

table_parser = CsvExcelParser()
parser_registry.register("csv", table_parser)
parser_registry.register("excel", table_parser)

parser_registry.register("html", HtmlParser())
parser_registry.register("latex", LatexParser())
parser_registry.register("image", ImageParser())
