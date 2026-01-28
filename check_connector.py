
path = r"d:\mirakle_platform-1\templates\connector_dashboard.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if '<div class="programs-grid" id="connectorProgramsGrid">' in content:
    print("Found HTML element")
else:
    print("Did NOT find HTML element")
