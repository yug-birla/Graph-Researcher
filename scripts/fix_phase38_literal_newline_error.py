from pathlib import Path

path = Path("app/deployment/hf_status.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

fixed_lines = []

for line in text.splitlines():
    stripped = line.strip()

    # Remove broken literal backslash-n lines accidentally written as Python code
    if stripped in {r"\n", r"\n\n", r"\n\n\n"}:
        continue

    # Fix if the broken literal got attached before a comment/import
    if stripped.startswith(r"\n\n#"):
        line = line.replace(r"\n\n", "", 1)

    if stripped.startswith(r"\n\nfrom "):
        line = line.replace(r"\n\n", "", 1)

    fixed_lines.append(line)

fixed = "\n".join(fixed_lines) + "\n"

# Extra targeted safety for Phase 38 export block
fixed = fixed.replace(r"\n\n# =====================================================", "\n\n# =====================================================")
fixed = fixed.replace(r"\n\nfrom app.product.final_product_ui", "\n\nfrom app.product.final_product_ui")

path.write_text(fixed, encoding="utf-8")

print("Fixed literal newline syntax error in hf_status.py")
