from pathlib import Path


REQUIRED_FILES = [
    "Dockerfile",
    ".dockerignore",
    "README.md",
    "requirements.txt",
    "app/main.py",
    "app/core/config.py",
    "app/deployment/hf_status.py"
]


def main():
    print("=" * 70)
    print("HUGGING FACE DEPLOYMENT READINESS CHECK")
    print("=" * 70)

    missing_files = []

    for file_path in REQUIRED_FILES:
        path = Path(file_path)

        if path.exists():
            print(f"OK      {file_path}")
        else:
            print(f"MISSING {file_path}")
            missing_files.append(file_path)

    if Path("README.md").exists():
        readme_text = Path("README.md").read_text(encoding="utf-8")

        print("\nREADME metadata check:")

        for item in ["sdk: docker", "app_port: 7860"]:
            if item in readme_text:
                print(f"OK      {item}")
            else:
                print(f"MISSING {item}")
                missing_files.append(f"README item: {item}")

    if Path("Dockerfile").exists():
        dockerfile_text = Path("Dockerfile").read_text(encoding="utf-8")

        print("\nDockerfile check:")

        for item in ["uvicorn", "app.main:app", "--port", "7860", "USER user"]:
            if item in dockerfile_text:
                print(f"OK      {item}")
            else:
                print(f"MISSING {item}")
                missing_files.append(f"Dockerfile item: {item}")

    print("\nResult:")

    if missing_files:
        print("NOT READY")
        print("Missing items:")
        for item in missing_files:
            print(f"- {item}")
    else:
        print("READY FOR HUGGING FACE SPACES")


if __name__ == "__main__":
    main()
