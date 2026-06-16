from pathlib import Path


SUPPORTED_FILE_TYPES = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".pdf": "pdf",
    ".docx": "docx",
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".html": "html",
    ".htm": "html",
    ".tex": "latex",
}


def detect_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    return SUPPORTED_FILE_TYPES.get(extension, "unsupported")
