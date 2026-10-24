"""LLM 판정 출력 검증·병합. 모델·검색·네트워크를 호출하지 않는다.

  python merge.py [--allow-partial]

입력: in/MANIFEST.json, in/<batch>.jsonl, out/<batch>.jsonl (워크플로 산출), item_key.jsonl (item_id -> system, qid; 판정자는 못 봄)
검증: 모든 배치의 출력 파일이 있고, 줄 수가 n 이고, item_id 가 입력과 정확히 같고(빠짐·중복·낯선 id 없음),
      status in open|closed|unknown, type 이 8개 토큰 또는 null, address 가 문자열 또는 null.
출력: llm_labels.jsonl  (auto_judge.load_llm_labels 형식: key = "<system>|<qid>", status, stated_address, stated_type)
      + note, item_id, answer_sha1 (run_analysis 가 답이 바뀐 낡은 라벨을 쓰지 않게 하는 해시)
      merge_report.json (문제 항목·집계). 문제가 있으면 종료 코드 1 (--allow-partial 이면 유효 항목만 쓰고 0).
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
STATUS = {"open", "closed", "unknown"}
TYPES = {"한식", "중식", "일식", "양식", "분식", "치킨호프주점", "카페디저트", "기타"}
HAS_ROAD_OR_DONG = re.compile(r"(?:대로|로|길)\s?\d|[가-힣0-9](?:로|길|동|읍|면|리)(?:\s|$|\d|\)|,)")


def jl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-partial", action="store_true")
    a = ap.parse_args()
    man = json.loads((HERE / "in" / "MANIFEST.json").read_text(encoding="utf-8"))
    key = {}
    for r in jl(HERE / "item_key.jsonl"):
        key[r["item_id"]] = r
    problems, labels, missing_batches = [], {}, []
    stats = Counter()
    for m in man:
        b = m["batch"]
        inp = [json.loads(x)["item_id"] for x in (HERE / "in" / f"{b}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        op = HERE / "out" / f"{b}.jsonl"
        if not op.exists():
            missing_batches.append(b)
            continue
        seen = set()
        for i, line in enumerate(op.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                problems.append({"batch": b, "line": i, "error": "bad json"}); continue
            iid = d.get("item_id")
            if iid not in inp:
                problems.append({"batch": b, "line": i, "item_id": iid, "error": "unknown item_id for this batch"}); continue
            if iid in seen:
                problems.append({"batch": b, "line": i, "item_id": iid, "error": "duplicate item_id"}); continue
            seen.add(iid)
            addr, typ, st = d.get("address"), d.get("type"), d.get("status")
            err = None
            if st not in STATUS:
                err = f"bad status {st!r}"
            elif typ is not None and typ not in TYPES:
                err = f"bad type {typ!r}"
            elif addr is not None and not isinstance(addr, str):
                err = "address not string/null"
            elif isinstance(addr, str) and not addr.strip():
                addr = None
            if err:
                problems.append({"batch": b, "line": i, "item_id": iid, "error": err}); continue
            note = str(d.get("note") or "")
            stats["status=" + st] += 1
            stats["type=" + str(typ)] += 1
            stats["address=" + ("given" if addr else "null")] += 1
            if "ADDR_CONVERTED" in note:
                stats["address_converted_from_other_script"] += 1
            if addr and not HAS_ROAD_OR_DONG.search(addr):
                stats["address_without_road_or_dong_token(check)"] += 1
            k = key[iid]
            labels[iid] = {"key": f'{k["system"]}|{k["qid"]}', "status": st, "stated_address": addr, "stated_type": typ,
                           "note": note, "item_id": iid, "answer_sha1": k["answer_sha1"]}
        for iid in inp:
            if iid not in seen:
                problems.append({"batch": b, "item_id": iid, "error": "missing from output"})
    out_rows = [labels[i] for i in sorted(labels)]       # item_id 순서 = 키 파일 순서. 같은 key 가 둘이면 나중 항목이 앞선 것을 덮는다.
    dedup = {}
    for r in out_rows:
        dedup[r["key"]] = r
    with open(HERE / "llm_labels.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in dedup.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rep = {"batches": len(man), "batches_missing_output": missing_batches, "items_valid": len(labels), "keys_written": len(dedup),
           "problems": problems, "stats": dict(stats)}
    (HERE / "merge_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in rep.items() if k != "problems"}, ensure_ascii=False), f"problems={len(problems)}")
    bad = bool(problems or missing_batches)
    if bad and not a.allow_partial:
        sys.exit(1)


if __name__ == "__main__":
    main()
