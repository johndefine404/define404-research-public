"""검색 재수집 회차 준비.
1) 완료 배치를 골라 skip 목록(JSON)을 출력하고, 부분 배치는 raw_retry/_partial 로 옮긴다.
2) 검색 한도·미실행 문구 답(analysis/load_data.py 의 LIMIT_RE)은 searches 가 1 이상이어도 무효로 보고,
   유효한 답이 없고 아직 대기 중인 배치에도 없는 문항을 보충 배치로 뒤에 덧붙인다(기존 번호는 건드리지 않는다).
   유효 판정은 load_data.load_answers("strict") 와 같은 함수를 써서 분석 쪽과 어긋나지 않게 한다.
   strict 유효성에는 검색 한도 문구뿐 아니라 언어 이탈 검사(load_data.script_ok: 질문 언어의 문자 체계가 아닌 답)도 들어 있다.
   --dry 를 주면 파일을 옮기거나 쓰지 않고 계산만 한다.
3) 부표본(기본): 결과 분석 전 결정(2026-10-24)으로 검색 2조건은 sampling/subsample_search_v1.csv 의 100곳 x 5언어만 받는다.
   보충 배치는 부표본 문항만 담고, MANIFEST 항목에 "subsample": "v1" 을 붙인다. 부표본이 아닌 기존 배치는 실행하지 않는다
   (출력 skip 에 전부 넣는다). 원래 방식(전수)으로 돌리려면 --full.
   출력 skip = 부표본 보충 배치 중 이미 끝난 것 + 부표본이 아닌 모든 배치. counts 는 시스템|언어별 최대 번호(워크플로가 1..최대를 훑는다).
"""
import json, shutil, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "analysis"))
import load_data as LD   # noqa: E402  (load_answers 와 LIMIT_RE 를 그대로 쓴다)

DRY = "--dry" in sys.argv
SUB = "--full" not in sys.argv                   # 기본: 부표본만 큐에 올린다
SUB_TAG = "v1"
SUB_IDS = LD.subsample_ids() if SUB else None
SIZE = 10
LANGS = ["ko", "en", "ja", "zh", "vi"]
SEARCH_SYSTEMS = ["H-search", "S-search"]
MAN = HERE / "batches_retry/MANIFEST.json"
man = json.loads(MAN.read_text(encoding="utf-8"))
P = HERE / "raw_retry/_partial"
if not DRY: P.mkdir(parents=True, exist_ok=True)

# 1) 완료 배치 / 부분 배치
skip = []
for m in man:
    f = HERE / f"raw_retry/{m['system']}/{m['batch']}.jsonl"
    if not f.exists(): continue
    L = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(L) == m["n"] and all(x.get("searches") for x in L): skip.append(m["batch"])
    elif not DRY:
        dst = P / f"{m['batch']}.jsonl"; i = 1
        while dst.exists(): dst = P / f"{m['batch']}.{i}.jsonl"; i += 1
        shutil.move(str(f), dst)
skipset = set(skip)

# 2) 보충 배치
answers, _, _ = LD.load_answers("strict")
valid = {(a["system"], a["qid"]) for a in answers}      # 원본 또는 재수집에서 유효한 답이 있는 문항
queued = set()                                           # 아직 안 끝난 기존 배치에 들어 있는 문항
maxidx = defaultdict(int)
for m in man:
    k = (m["system"], m["lang"])
    maxidx[k] = max(maxidx[k], int(m["batch"].rsplit("_r", 1)[1]))
    if m["batch"] not in skipset and (not SUB or m.get("subsample") == SUB_TAG):   # 부표본 모드에서는 부표본 배치만 대기로 친다
        for it in json.loads((HERE / f"batches_retry/{m['batch']}.json").read_text(encoding="utf-8")):
            queued.add((m["system"], it["qid"]))
added = {}
new_entries = []
for sysname in SEARCH_SYSTEMS:
    for lang in LANGS:
        orig = []                                        # 원래 표본 순서
        for f in sorted((HERE / "batches").glob(f"{sysname}_{lang}_*.json")):
            orig += json.loads(f.read_text(encoding="utf-8"))
        if SUB:
            orig = [it for it in orig if it["qid"].split("-")[0] in SUB_IDS]
        need = [it for it in orig if (sysname, it["qid"]) not in valid and (sysname, it["qid"]) not in queued]
        added[f"{sysname}|{lang}"] = len(need)
        idx = maxidx[(sysname, lang)]
        for i in range(0, len(need), SIZE):
            idx += 1
            chunk = need[i:i + SIZE]
            b = f"{sysname}_{lang}_r{idx:03d}"
            if not DRY:
                (HERE / f"batches_retry/{b}.json").write_text(json.dumps(chunk, ensure_ascii=False), encoding="utf-8")
            new_entries.append({"batch": b, "system": sysname, "lang": lang, "n": len(chunk), **({"subsample": SUB_TAG} if SUB else {})})
man = man + new_entries
if new_entries and not DRY:
    with open(MAN, "w", encoding="utf-8", newline="\n") as fo:   # 윈도우에서도 LF 유지(줄 끝 변환 금지)
        fo.write(json.dumps(man, indent=0, ensure_ascii=False))

counts = defaultdict(int)
for m in man: counts[f"{m['system']}|{m['lang']}"] += 1
if SUB:
    # 부표본 모드: 대기 = 부표본 배치 중 안 끝난 것. 나머지는 전부 skip.
    pending = {m["batch"] for m in man if m.get("subsample") == SUB_TAG and m["batch"] not in skipset}
    skip = [m["batch"] for m in man if m["batch"] not in pending]
    skipset = set(skip)
remaining_q = sum(m["n"] for m in man if m["batch"] not in skipset)
print(json.dumps({"subsample_mode": SUB, "remaining": len(man) - len(skip), "remaining_questions": remaining_q,
                  "added_batches": len(new_entries), "added_questions": sum(added.values()),
                  "added_by_group": added, "counts": dict(counts), "skip": skip}, ensure_ascii=False))
