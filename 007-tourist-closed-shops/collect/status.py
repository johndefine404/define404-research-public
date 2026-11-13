#!/usr/bin/env python3
# 남은 배치 목록: MANIFEST 대비 raw 파일이 없거나 줄 수가 모자란 배치
import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
todo = []
for m in json.loads((R / "collect/batches/MANIFEST.json").read_text()):
    p = R / m["output"]
    n = sum(1 for l in open(p) if l.strip()) if p.exists() else 0
    if n < m["n"]:
        todo.append(m["batch"])
print(len(todo), " ".join(todo))
