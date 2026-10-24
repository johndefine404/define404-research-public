"""H-mem_ja_001(200답 전부 한글) 재수집용 배치 생성. 원본 batches/H-mem_ja_001.json 의 qid 순서를 그대로 20개씩 10배치로 자른다.
출력: batches_retry/H-mem_ja_r001..r010.json. 원본 파일은 건드리지 않는다. 여러 번 돌려도 같은 결과."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
src = json.loads((D / "batches" / "H-mem_ja_001.json").read_text(encoding="utf-8"))
assert len(src) == 200 and all(x["qid"].endswith("-ja") for x in src)
N = 20
(D / "batches_retry").mkdir(exist_ok=True)
for i in range(0, len(src), N):
    p = D / "batches_retry" / f"H-mem_ja_r{i // N + 1:03d}.json"
    p.write_text(json.dumps(src[i:i + N], ensure_ascii=False), encoding="utf-8", newline="\n")
print(len(src) // N, "batches")
