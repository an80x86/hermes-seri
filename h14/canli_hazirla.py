"""Canli cekim icin temiz Hermes tabani: ~/hermes-seri/h14_taban (olc.py'deki b_kimlik duzeniyle ayni).
b2taban kopyasi, takvim MCP'si cikarilmis, SOUL'a yalnizca "bu oturumdaki kullanici Ayse" satiri eklenmis."""
import json, pathlib, shutil

KOK = pathlib.Path(__file__).resolve().parent
EV = pathlib.Path.home() / "hermes-seri"
S = json.loads((KOK / "istekler.json").read_text(encoding="utf-8"))
d = EV / "h14_taban"
if d.exists():
    shutil.rmtree(d)
shutil.copytree(EV / "b2taban", d, ignore=shutil.ignore_patterns(
    "state.db*", "usage*", "sessions", "memories", "logs", "*.lock"))
for alt in ("memories", "sessions", "usage"):
    (d / alt).mkdir(exist_ok=True)
y = d / "config.yaml"
y.write_text(y.read_text().replace("mcp_servers:\n  takvim:\n    url: http://takvim:8000/mcp\n", ""))
(d / "SOUL.md").write_text((d / "SOUL.md").read_text() + S["kimlik_satiri"], encoding="utf-8")
print(d, "mcp_servers" in y.read_text())
