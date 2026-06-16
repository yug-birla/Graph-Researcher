from abc import ABC, abstractmethod
from typing import List
from app.schemas.rich_content_block import RichContentBlock


class BaseParser(ABC):

    @abstractmethod
    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:
        pass
