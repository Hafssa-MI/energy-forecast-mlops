"""Change l'environnement actif dans params.yaml : python scripts/use_env.py staging"""
import re
import sys
from pathlib import Path

env = sys.argv[1] if len(sys.argv) > 1 else ""
if env not in ("dev", "staging", "prod"):
    sys.exit("Usage : python scripts/use_env.py [dev|staging|prod]")
p = Path("params.yaml")
text = re.sub(r"^active_env:.*$", f"active_env: {env}", p.read_text(encoding="utf-8"), flags=re.M)
p.write_text(text, encoding="utf-8")
print(f"Environnement actif : {env}")
