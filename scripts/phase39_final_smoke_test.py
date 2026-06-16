from pathlib import Path
import py_compile
import traceback

print("\n==============================")
print("PHASE 39 FINAL SMOKE TEST")
print("==============================\n")

files_to_compile = [
    "app/main.py",
    "app/deployment/hf_status.py",
    "app/product/final_product_ui.py",
    "app/product/document_storage_manager.py",
    "app/product/document_compare_service.py",
    "app/product/source_viewer.py",
    "app/product/admin_ui.py",
    "app/product/auth_service.py",
]

compile_failed = False

print("1. Checking Python compile...\n")

for file in files_to_compile:
    path = Path(file)

    if not path.exists():
        print(f"SKIP missing: {file}")
        continue

    try:
        py_compile.compile(str(path), doraise=True)
        print(f"OK: {file}")
    except Exception:
        compile_failed = True
        print(f"FAILED: {file}")
        traceback.print_exc()

print("\n2. Checking FastAPI app import and routes...\n")

required_routes = [
    ("/", "GET"),
    ("/app", "GET"),
    ("/ask", "POST"),
    ("/documents/upload", "POST"),
    ("/documents/{document_id}/graph/build", "POST"),
    ("/documents/{document_id}/graph/view", "GET"),
    ("/documents/{document_id}/sources/{source_id}/view", "GET"),
    ("/documents/{document_id}/storage", "GET"),
    ("/documents/{document_id}/delete", "DELETE"),
    ("/documents/compare", "POST"),
    ("/login", "GET"),
    ("/admin", "GET"),
]

try:
    from app.main import app

    existing = set()

    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()

        for method in methods:
            existing.add((path, method))

    missing = []

    for route in required_routes:
        if route in existing:
            print(f"OK route: {route[1]} {route[0]}")
        else:
            print(f"MISSING route: {route[1]} {route[0]}")
            missing.append(route)

    print("\n3. Summary\n")

    if compile_failed:
        print("RESULT: FAILED - compile errors exist.")
    elif missing:
        print("RESULT: PARTIAL - app imports, but some expected routes are missing.")
        print("Missing routes:")
        for method_path in missing:
            print(f"- {method_path[1]} {method_path[0]}")
    else:
        print("RESULT: PASS - core app files compile and required routes exist.")

except Exception:
    print("RESULT: FAILED - app.main could not be imported.")
    traceback.print_exc()


checklist = """# Final Testing Checklist - GraphResearcher

Use this checklist after deployment.

## Basic pages
- [ ] Open `/`
- [ ] Open `/app`
- [ ] Open `/login`
- [ ] Open `/admin`

## Single document flow
- [ ] Clear Workspace Cache
- [ ] Upload one PDF
- [ ] Confirm document appears in left sidebar
- [ ] Ask a simple question
- [ ] Ask a detailed question
- [ ] Check answer renders properly
- [ ] Check sources appear on right side
- [ ] Click Open source
- [ ] Click Build / Rebuild Graph
- [ ] Click View Graph

## Compare flow
- [ ] Upload second PDF
- [ ] Select first document
- [ ] Choose second document in Compare With
- [ ] Ask a comparison question
- [ ] Confirm side-by-side answer appears
- [ ] Confirm sources for both documents appear

## Delete flow
- [ ] Delete selected document
- [ ] Confirm it disappears from sidebar
- [ ] Open `/documents/<DOCUMENT_ID>/storage`
- [ ] Confirm backend storage is missing/deleted or delete attempted

## Final notes
- Files on Hugging Face `/tmp` are temporary.
- If old documents show after rebuild, clear workspace cache and re-upload.
- Do not expose API Docs or GraphRAG Console in normal user UI.
"""

Path("FINAL_TEST_CHECKLIST.md").write_text(checklist, encoding="utf-8")
print("\nCreated FINAL_TEST_CHECKLIST.md")
