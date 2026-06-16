from pathlib import Path

files_to_fix = [
    Path("app/main.py"),
]

for path in files_to_fix:
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")
    print(f"Fixed hidden BOM characters in {path}")
