# Final Testing Checklist - GraphResearcher

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
