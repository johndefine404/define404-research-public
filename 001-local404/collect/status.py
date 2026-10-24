"""수집 상태 점검. 배치마다 결과 파일이 완전한지(줄 수 = 문항 수, qid 일치, 빈 답 0) 보고 todo.json에 남은 배치를 쓴다.
사용: python3 collect/status.py"""
import json
from pathlib import Path
HERE = Path(__file__).parent
man = json.loads((HERE / "batches/MANIFEST.json").read_text(encoding="utf-8"))
done, todo, partial = [], [], []
for m in man:
    if m["system"] == "W-mem": continue
    f = HERE / "raw" / m["system"] / f'{m["batch"]}.jsonl'
    want = {x["qid"] for x in json.loads((HERE / "batches" / f'{m["batch"]}.json').read_text(encoding="utf-8"))}
    try:
        L = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
        ok = {x["qid"] for x in L} == want and all(x.get("answer", "").strip() for x in L)
    except Exception:
        ok = False; L = []
    (done if ok else (partial if L else todo)).append(m["batch"])
wq = sum(1 for f in (HERE / "raw/W-mem").glob("*.jsonl") for l in f.read_text(encoding="utf-8").splitlines() if l.strip())
(HERE / "todo.json").write_text(json.dumps(partial + todo, indent=0))
print(f"Claude 배치: 완료 {len(done)} / 불완전 {len(partial)} / 없음 {len(todo)} (전체 {len(done)+len(partial)+len(todo)})")
print(f"W-mem 답: {wq} / 4000")
