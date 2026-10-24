"""W-mem 수집: Cloudflare Workers AI @cf/meta/llama-3.1-8b-instruct-fp8-fast, 도구 없음, 최대 300토큰.
하루 무료 1만 뉴런 중 9,000까지만 쓰고 멈춘다(사용량 추정 = 입력 4,119 + 출력 34,868 뉴런/100만 토큰, 2026-10-20 가격 문서).
이미 받은 qid는 건너뛴다. 다시 실행하면 이어간다."""
import json, re, time, urllib.request, urllib.error, datetime
from pathlib import Path
HERE = Path(__file__).parent
env = (HERE.parents[3] / "2-side/dec27/Blog/.env").read_text()  # 개인 Cloudflare 계정(Workers AI 권한 있는 토큰)
ACC = re.search(r"^CLOUDFLARE_ACCOUNT_ID=(.+)$", env, re.M).group(1).strip().strip('"')
TOK = re.search(r"^CLOUDFLARE_API_TOKEN=(.+)$", env, re.M).group(1).strip().strip('"')
MODEL = "@cf/meta/llama-3.1-8b-instruct-fp8-fast"
BUDGET = 9000.0
OUT = HERE / "raw/W-mem"
BFILE = HERE / ".wmem_budget.json"  # UTC 날짜별 누적 사용량. 프로세스를 다시 켜도 그날 사용량을 이어 센다
TODAY = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
_b = json.loads(BFILE.read_text()) if BFILE.exists() else {}
used = float(_b.get(TODAY, 0.0))
done = {json.loads(l)["qid"] for f in OUT.glob("*.jsonl") for l in f.read_text().splitlines() if l.strip()}
for bf in sorted((HERE / "batches").glob("W-mem_*.json")):
    out = OUT / (bf.stem + ".jsonl")
    for it in json.loads(bf.read_text()):
        if it["qid"] in done: continue
        if used >= BUDGET: print("budget stop", round(used)); raise SystemExit
        body = {"messages": [{"role": "user", "content": it["q"]}], "max_tokens": 300}
        for k in range(3):
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACC}/ai/run/{MODEL}",
                    data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"}), timeout=60))
                break
            except urllib.error.HTTPError as e:
                err = e.read().decode()[:200]
                if "neurons" in err.lower() or e.code == 429: print("limit", err); raise SystemExit
                time.sleep(3)
        else:
            print("call failed 3 times", it["qid"], err if 'err' in dir() else ''); raise SystemExit
        res = r.get("result", {}); u = res.get("usage", {})
        used += u.get("prompt_tokens", 80) * 4119 / 1e6 + u.get("completion_tokens", 300) * 34868 / 1e6
        BFILE.write_text(json.dumps({TODAY: used}))
        rec = {"qid": it["qid"], "answer": res.get("response", ""), "sources": [], "searches": 0, "model": MODEL,
               "usage": u, "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "retries": k}
        with open(out, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        done.add(it["qid"])
print("finished", round(used), len(done))
