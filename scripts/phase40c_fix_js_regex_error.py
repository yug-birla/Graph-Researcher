from pathlib import Path

path = Path("app/product/final_product_ui.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

# These are inside a Python triple-quoted HTML string.
# So JS regex \n must be written as \\n in the Python source,
# otherwise Python turns it into a real newline and breaks browser JS.

replacements = {
    r"[^|\n]*page": r"[^|\\n]*page",
    r"/\n{3,}/g": r"/\\n{3,}/g",
    r'"\n\n"': r'"\\n\\n"',
    r"split(/\n+/)": r"split(/\\n+/)",
    r"[ \t]+": r"[ \\t]+",
}

for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)

# Safety: if regex line is still risky, replace that exact line with a RegExp constructor.
bad_line = r'text = text.replace(/\s+\|\s*[^|\n]*page\s*\d+/gi, "");'
safe_line = r'text = text.replace(new RegExp("\\s+\\|\\s*[^|\\n]*page\\s*\\d+", "gi"), "");'

if bad_line in text:
    text = text.replace(bad_line, safe_line)

path.write_text(text, encoding="utf-8")
print("Fixed broken JavaScript regex escapes in final_product_ui.py")
