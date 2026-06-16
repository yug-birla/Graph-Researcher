from pathlib import Path

path = Path("app/core/config.py")
text = path.read_text(encoding="utf-8")

if "HF_API_MODE" not in text:
    old = '    HF_TIMEOUT_SECONDS: int = get_int_env("HF_TIMEOUT_SECONDS", 60)\n'

    new = '''    HF_TIMEOUT_SECONDS: int = get_int_env("HF_TIMEOUT_SECONDS", 60)

    # auto = try best route based on model name
    # chat = force router chat-completions API
    # inference = force HF inference model endpoint
    HF_API_MODE: str = os.getenv("HF_API_MODE", "auto")
'''

    if old in text:
        text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        print("HF_API_MODE added to config.py")
    else:
        print("Target line not found. config.py was not changed.")
else:
    print("HF_API_MODE already exists in config.py")
