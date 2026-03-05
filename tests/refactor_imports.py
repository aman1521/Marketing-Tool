import os

base_dir = r"d:\Marketing tool\backend\services"

replacements = {
    "backend.services.forge": "backend.services.execution.forge",
    "backend.services.hawkeye": "backend.services.execution.hawkeye",
    "backend.services.memory": "backend.services.intelligence.operator_memory",
    "backend.services.pulse": "backend.services.intelligence.market_signals",
    "backend.services.creative_genome": "backend.services.intelligence.creative_genome",
    "backend.services.competitor": "backend.services.competitor_intelligence",
    "backend.services.genesis": "backend.services.safety_engine"
}

files_changed = 0

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            for old, new in replacements.items():
                content = content.replace(old, new)
                
            if content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated {filepath}")
                files_changed += 1

print(f"Repaired imports in {files_changed} files.")
