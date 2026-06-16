from typing import List
import pymupdf

from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class PdfParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        blocks = []
        pdf_document = pymupdf.open(file_path)

        for page_index in range(len(pdf_document)):
            page = pdf_document[page_index]
            text = page.get_text("text").strip()

            if not text:
                continue

            blocks.append(
                RichContentBlock(
                    block_id=f"{document_id}_page_{page_index + 1}",
                    document_id=document_id,
                    content_type="text",
                    content=text,
                    page_number=page_index + 1,
                    section_title=None,
                    source_file_name=source_file_name,
                    metadata={
                        "parser": "PdfParser",
                        "original_format": "pdf",
                        "page_index_zero_based": page_index
                    }
                )
            )

        pdf_document.close()
        return blocks
