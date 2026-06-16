from typing import List
from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class TxtParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if not text.strip():
            return []

        return [
            RichContentBlock(
                block_id=f"{document_id}_txt_block_1",
                document_id=document_id,
                content_type="text",
                content=text,
                page_number=None,
                section_title=None,
                source_file_name=source_file_name,
                metadata={
                    "parser": "TxtParser",
                    "original_format": "txt"
                }
            )
        ]
