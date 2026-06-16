from pathlib import Path

path = Path("app/product/final_product_ui.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

binding_js = r'''
// Phase 40B: expose button functions globally
window.uploadDocument = uploadDocument;
window.refreshDocuments = refreshDocuments;
window.newChat = newChat;
window.reindexSelectedDocument = reindexSelectedDocument;
window.buildGraph = buildGraph;
window.openGraphViewer = openGraphViewer;
window.clearWorkspaceCache = clearWorkspaceCache;
window.deleteSelectedDocument = deleteSelectedDocument;
window.sendMessage = sendMessage;
window.handleKeyDown = handleKeyDown;
window.selectDocument = selectDocument;
window.openSource = openSource;
'''

if "Phase 40B: expose button functions globally" not in text:
    text = text.replace("renderDocuments();\n</script>", binding_js + "\nrenderDocuments();\n</script>")
    print("Added global button bindings.")
else:
    print("Bindings already present.")

path.write_text(text, encoding="utf-8")
print("Phase 40B complete.")
