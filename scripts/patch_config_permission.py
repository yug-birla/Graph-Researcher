from pathlib import Path
import re

path = Path("app/core/config.py")
text = path.read_text(encoding="utf-8")

pattern = r'''    def ensure_directories\(self\) -> None:
(?:        .+\n)+?'''

new_block = '''    def ensure_directories(self) -> None:
        directories = [
            self.UPLOAD_DIR,
            self.PROCESSED_DIR,
            self.QDRANT_LOCAL_PATH,
            self.EVALUATION_DIR
        ]

        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

        except PermissionError:
            fallback_base = Path("/tmp/graphrag")
            fallback_dirs = [
                fallback_base / "uploads",
                fallback_base / "processed",
                fallback_base / "qdrant",
                fallback_base / "evaluation"
            ]

            for directory in fallback_dirs:
                directory.mkdir(parents=True, exist_ok=True)
'''

match = re.search(pattern, text)

if not match:
    print("Could not auto-patch ensure_directories. Please send config.py if this happens.")
else:
    text = text[:match.start()] + new_block + text[match.end():]
    path.write_text(text, encoding="utf-8")
    print("config.py permission fallback patched successfully.")
