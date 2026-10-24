"""L-mem 수집: 같은 공개 모델(Meta Llama 3.1 8B Instruct)을 이 맥에서 직접 실행(Ollama, llama3.1:8b-instruct-q8_0).
Workers AI 무료 한도로 W-mem을 끝낼 수 없어 바꾼 경로. 4,000문항 전부를 이 경로로 다시 받는다(조건 일관성).
도구 없음, 최대 300토큰, seed 20261021, 그 밖의 설정은 Ollama 기본값. 이미 받은 qid는 건너뛴다."""
import json, urllib.request, datetime
from pathlib import Path
HERE = Path(__file__).parent; OUT = HERE / "raw/L-mem"
MODEL = "llama3.1:8b-instruct-q8_0"
done = {json.loads(l)["qid"] for f in OUT.glob("*.jsonl") for l in f.read_text(encoding="utf-8").splitlines() if l.strip()}
for bf in sorted((HERE / "batches").glob("W-mem_*.json")):
    out = OUT / (bf.stem.replace("W-mem", "L-mem") + ".jsonl")
    for it in json.loads(bf.read_text(encoding="utf-8")):
        if it["qid"] in done: continue
        body = {"model": MODEL, "stream": False, "options": {"num_predict": 300, "seed": 20261021},
                "messages": [{"role": "user", "content": it["q"]}]}
        d = json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}), timeout=600))
        rec = {"qid": it["qid"], "answer": d["message"]["content"], "sources": [], "searches": 0, "model": MODEL,
               "usage": {"prompt_tokens": d.get("prompt_eval_count"), "completion_tokens": d.get("eval_count")},
               "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        with open(out, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        done.add(it["qid"])
print("finished", len(done))
