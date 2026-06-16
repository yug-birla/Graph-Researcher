from typing import List

from app.core.config import settings
from app.schemas.rich_content_block import RichContentBlock
from app.schemas.content_chunk import ContentChunk


def chunk_blocks(
    blocks: List[RichContentBlock],
    chunk_size: int = settings.DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = settings.DEFAULT_CHUNK_OVERLAP
) -> List[ContentChunk]:

    chunks = []

    for block in blocks:
        if block.content_type == "text":
            chunks.extend(
                chunk_text_block(
                    block=block,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            )
        else:
            chunks.append(create_atomic_chunk(block))

    return chunks


def chunk_text_block(
    block: RichContentBlock,
    chunk_size: int,
    chunk_overlap: int
) -> List[ContentChunk]:

    text = block.content

    if not text:
        return []

    chunks = []
    start = 0
    chunk_index = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                ContentChunk(
                    chunk_id=f"{block.block_id}_chunk_{chunk_index + 1}",
                    document_id=block.document_id,
                    parent_block_id=block.block_id,
                    content_type=block.content_type,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    page_number=block.page_number,
                    section_title=block.section_title,
                    source_file_name=block.source_file_name,
                    start_char=start,
                    end_char=end,
                    metadata={
                        "chunking_strategy": "character_overlap",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "parent_parser": block.metadata.get("parser")
                    }
                )
            )
            chunk_index += 1

        if end == text_length:
            break

        start = end - chunk_overlap

    return chunks


def create_atomic_chunk(block: RichContentBlock) -> ContentChunk:
    return ContentChunk(
        chunk_id=f"{block.block_id}_chunk_1",
        document_id=block.document_id,
        parent_block_id=block.block_id,
        content_type=block.content_type,
        content=block.content,
        chunk_index=0,
        page_number=block.page_number,
        section_title=block.section_title,
        source_file_name=block.source_file_name,
        start_char=0,
        end_char=len(block.content),
        metadata={
            "chunking_strategy": "atomic_rich_content_block",
            "reason": "non-text content should not be split"
        }
    )
