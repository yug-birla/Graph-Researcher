import shutil
from pathlib import Path
from typing import List

from PIL import Image

from app.core.config import settings
from app.ingestion.base_parser import BaseParser
from app.schemas.rich_content_block import RichContentBlock


class ImageParser(BaseParser):

    def parse(
        self,
        file_path: str,
        document_id: str,
        source_file_name: str
    ) -> List[RichContentBlock]:

        source_path = Path(file_path)

        image_assets_dir = settings.PROCESSED_DIR / document_id / "assets" / "images"
        image_assets_dir.mkdir(parents=True, exist_ok=True)

        safe_image_name = Path(source_file_name).name
        stored_image_path = image_assets_dir / safe_image_name

        shutil.copy2(source_path, stored_image_path)

        image_metadata = extract_image_metadata(stored_image_path)

        return [
            RichContentBlock(
                block_id=f"{document_id}_image_block_1",
                document_id=document_id,
                content_type="image",
                content=f"Image file uploaded: {source_file_name}. Caption not generated yet.",
                page_number=None,
                section_title=None,
                source_file_name=source_file_name,
                metadata={
                    "parser": "ImageParser",
                    "original_format": image_metadata["image_format"],
                    "image_path": str(stored_image_path),
                    "image_file_name": safe_image_name,
                    "width": image_metadata["width"],
                    "height": image_metadata["height"],
                    "mode": image_metadata["mode"],
                    "file_size_bytes": image_metadata["file_size_bytes"],
                    "caption_status": "not_generated"
                }
            )
        ]


def extract_image_metadata(image_path: Path) -> dict:
    with Image.open(image_path) as image:
        width, height = image.size
        image_format = image.format
        mode = image.mode

    return {
        "width": width,
        "height": height,
        "image_format": image_format,
        "mode": mode,
        "file_size_bytes": image_path.stat().st_size
    }
