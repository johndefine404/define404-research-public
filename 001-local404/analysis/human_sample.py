"""(b) 사람 판정 표본 200답 선정 + 평가 시트 + 코헨 카파 (judge/rules.md 5절, prereg 6절).

선정: 분석 대상 답 전체(유효 답, W-mem 제외)를 (system, qid) 순으로 정렬한 뒤 random.Random(20261021).sample(., 200).
      -> 같은 입력이면 항상 같은 표본. 시스템별 층화 없음 (prereg 가 '무작위 200답'이라고만 해서. README 모호성 참조).
평가 시트: 평가자에게는 질문·답 본문만 준다. 정답·시스템·자동 판정은 주지 않는다. 평가자는 답이 '말한 것'을 적는다
      (status, stated_address, stated_type). 정답 대조는 코드가 한다 (자동 판정과 같은 방식, rules.md 5절).
카파: 자동 판정 대 사람 A·B, 사람 A 대 B.  모두 이 모듈에서 계산한다. 평가자 파일이 없으면 계산하지 않는다.

CLI
  python human_sample.py draw  --out DIR [--dryrun]       # 표본 키·시트 쓰기 (DIR/human_sample/)
  python human_sample.py kappa --out DIR --a A.csv --b B.csv   # 평가자 시트 채운 뒤
"""
import argparse
import csv
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

import config as C

STATUS_VALUES = ["open", "closed", "unknown"]
TYPE_VALUES = ["한식", "중식", "일식", "양식", "분식", "치킨호프주점", "카페디저트", "기타", ""]


def cohen_kappa(a, b):
    """두 평가자의 명목 범주 일치 카파. 범주가 하나뿐이면(pe=1) nan."""
    assert len(a) == len(b)
    n = len(a)
    if n == 0:
        return float("nan")
    cats = sorted(set(a) | set(b), key=str)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if pe >= 1.0:
        return float("nan")
    return (po - pe) / (1 - pe)


def kappa_with_ci(a, b, n_boot=2000, seed=C.SEED):
    """카파와 percentile 부트스트랩 95% CI (표본 행 재추출). 일치율 포함."""
    a, b = list(a), list(b)
    n = len(a)
    k = cohen_kappa(a, b)
    po = sum(x == y for x, y in zip(a, b)) / n if n else float("nan")
    rng = np.random.default_rng(seed)
    ks = []
    A, B = np.array(a, dtype=object), np.array(b, dtype=object)
    for _ in range(n_boot if n >= 5 else 0):
        idx = rng.integers(0, n, n)
        kk = cohen_kappa(list(A[idx]), list(B[idx]))
        if not math.isnan(kk):
            ks.append(kk)
    lo, hi = (float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5))) if len(ks) > 50 else (float("nan"), float("nan"))
    return {"n": n, "agreement": po, "kappa": k, "kappa_ci_lo": lo, "kappa_ci_hi": hi}


def draw_sample(answers, n=C.HUMAN_SAMPLE_N, seed=C.SEED):
    keys = sorted((a["system"], a["qid"]) for a in answers)
    if len(keys) < n:
        return keys, "pool smaller than %d" % n
    rng = random.Random(seed)
    return sorted(rng.sample(keys, n)), ""


def question_text(qid, system):
    pref = C.SYSTEMS[system]["batch_prefix"]
    for f in sorted((C.COLLECT / "batches").glob(f"{pref}_{qid.split('-')[1]}_*.json")):
        for it in json.loads(f.read_text(encoding="utf-8")):
            if it["qid"] == qid:
                return it["q"]
    return ""


def write_sheets(sample_keys, answers, out_dir, dryrun):
    out = Path(out_dir) / "human_sample"
    out.mkdir(parents=True, exist_ok=True)
    by_key = {(a["system"], a["qid"]): a for a in answers}
    rng = random.Random(C.SEED + 1)        # 평가자에게 보이는 순서(시스템·가게 순서 단서 제거)
    order = list(sample_keys)
    rng.shuffle(order)
    banner = "DRYRUN-PROVISIONAL" if dryrun else "FINAL"
    with open(out / "sample_keys.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rating_id", "system", "qid", "mode"])
        for i, (s, q) in enumerate(order, 1):
            w.writerow([f"R{i:03d}", s, q, banner])
    for who in ("A", "B"):
        with open(out / f"rater_{who}_blank.csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["rating_id", "question", "answer", "status[open|closed|unknown]",
                        "stated_address(대상 가게 주소로 제시한 문자열, 없으면 빈칸)",
                        "stated_type[한식|중식|일식|양식|분식|치킨호프주점|카페디저트|기타|빈칸]"])
            for i, (s, q) in enumerate(order, 1):
                w.writerow([f"R{i:03d}", question_text(q, s), by_key[(s, q)]["answer"], "", "", ""])
    (out / "README_rating.txt").write_text(
        f"[{banner}] 서로 모르게 판정한다. rules.md 1~3절 기준으로 '답이 말한 것'만 적는다. 정답은 모른다.\n"
        "status: 지금 영업 중이라 단정=open, 폐업이라 단정=closed, 결론 없음=unknown (마지막 결론 문장 기준).\n"
        "stated_address: 답이 대상 가게의 주소라고 말한 문자열 그대로. 다른 가게 주소만 있으면 빈칸.\n"
        "stated_type: 답이 말한 업종을 8개 묶음 중 하나로. 말하지 않았으면 빈칸.\n"
        "파일명: rater_A_filled.csv / rater_B_filled.csv 로 저장(열 구성 유지).\n", encoding="utf-8")
    return out


def _read_rater(path):
    rows = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.reader(f):
            if not r or r[0] == "rating_id":
                continue
            rows[r[0]] = {"status": r[3].strip().lower(), "stated_address": r[4].strip(), "stated_type": r[5].strip()}
    return rows


def derive_labels(raw, truth_row):
    """평가자(또는 LLM) 원 라벨 + 정답 -> 자동 판정과 같은 범주."""
    import auto_judge as J
    status = raw["status"] or "unknown"
    addr = J._addr_from_stated(raw["stated_address"], truth_row["address"]) if truth_row["address"] else "na"
    tb = J.truth_bundle(truth_row["biz_type"])
    sb = raw["stated_type"]
    typ = "na" if tb == "기타" else ("none" if not sb else ("match" if sb == tb else "wrong"))
    _, strict = J.score(status, addr, typ, truth_row["truth"])
    if status == "unknown" or (status in ("open", "closed") and status != truth_row["truth"]):
        strict = False                       # 분석 정의(A4)와 같게: 모름·틀림은 0
    return {"status": status, "address": addr, "type": typ, "lenient": status == truth_row["truth"], "strict": strict}


def compute_kappas(out_dir, judge_rows, store_by_id, path_a, path_b):
    """judge_rows: auto_judge.judge_all 결과(해결된 라벨). 반환 kappa 행 목록."""
    keys = {}
    with open(Path(out_dir) / "human_sample" / "sample_keys.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            keys[r["rating_id"]] = (r["system"], r["qid"])
    A, B = _read_rater(path_a), _read_rater(path_b)
    auto = {(r["system"], r["qid"]): r for r in judge_rows}
    lab = {"A": {}, "B": {}, "auto": {}}
    for rid, (s, q) in keys.items():
        tr = store_by_id[q.split("-")[0]]
        if rid in A: lab["A"][rid] = derive_labels(A[rid], tr)
        if rid in B: lab["B"][rid] = derive_labels(B[rid], tr)
        ar = auto.get((s, q))
        if ar is not None:
            res = ar["status"] in ("open", "closed", "unknown")
            strict = ar["correct_strict"]
            if ar["status"] == "unknown" or (ar["status"] in ("open", "closed") and ar["status"] != tr["truth"]):
                strict = False
            lab["auto"][rid] = {"status": ar["status"], "address": ar["address"], "type": ar["type"],
                                "lenient": (ar["status"] == tr["truth"]) if res else None, "strict": strict if res else None}
    out = []
    for field in ("status", "address", "type", "lenient", "strict"):
        for x, y in (("auto", "A"), ("auto", "B"), ("A", "B")):
            ids = [i for i in keys if i in lab[x] and i in lab[y]
                   and lab[x][i][field] not in (None, "review", "na") and lab[y][i][field] not in (None, "review", "na")]
            r = kappa_with_ci([str(lab[x][i][field]) for i in ids], [str(lab[y][i][field]) for i in ids])
            r.update(field=field, pair=f"{x} vs {y}", n_excluded_unresolved_or_na=len(keys) - len(ids))
            out.append(r)
    return out


# ------------------------------------------------------------------------------ 독립 LLM 판정자 B (사람 2인 판정 대체; DEVIATIONS.md)
_B_STATUS = {"open", "closed", "unknown"}
_B_TYPES = {"한식", "중식", "일식", "양식", "분식", "치킨호프주점", "카페디저트", "기타"}


def load_rater_b(llm_dir, answers):
    """llm_dir/rater_b_key.jsonl + out_b/*.jsonl -> ({(system,qid): raw}, 문제 목록).
    raw = derive_labels 입력 형식 {status, stated_address, stated_type}. 키 파일의 답 해시가 현재 답과 다르면 문제로 보고한다."""
    import hashlib
    llm_dir = Path(llm_dir)
    problems, raw = [], {}
    kp = llm_dir / "rater_b_key.jsonl"
    if not kp.exists():
        return raw, ["rater_b_key.jsonl missing (build_rater_b.py not run)"]
    cur = {(a["system"], a["qid"]): hashlib.sha1(a["answer"].encode("utf-8")).hexdigest() for a in answers}
    key = {}
    for line in kp.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            key[d["item_id"]] = d
    out = {}
    files = sorted((llm_dir / "out_b").glob("B*.jsonl")) if (llm_dir / "out_b").exists() else []
    for f in files:
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                problems.append(f"{f.name}:{i} bad json")
                continue
            iid = d.get("item_id")
            if iid not in key:
                problems.append(f"{f.name}:{i} unknown item_id {iid}")
                continue
            if iid in out:
                problems.append(f"{f.name}:{i} duplicate {iid}")
                continue
            addr, typ = d.get("address"), d.get("type")
            if d.get("status") not in _B_STATUS or (typ is not None and typ not in _B_TYPES) or (addr is not None and not isinstance(addr, str)):
                problems.append(f"{f.name}:{i} bad value {iid}")
                continue
            out[iid] = {"status": d["status"], "stated_address": (addr or "").strip(), "stated_type": typ or ""}
    for iid, k in key.items():
        kk = (k["system"], k["qid"])
        if iid not in out:
            problems.append(f"missing output {iid}")
            continue
        if cur.get(kk) != k["answer_sha1"]:
            problems.append(f"answer changed since build_rater_b for {iid}")
            continue
        raw[kk] = out[iid]
    return raw, problems


def compute_kappas_b(judge_rows, store_by_id, raw_b, llm_labels):
    """독립 판정자 B 대 (1) 주 판정(사전+Sonnet 보조, 분석에 쓴 라벨) (2) Sonnet 단독(llm_labels; 사전 미사용).
    B 와 Sonnet 은 둘 다 '답이 단정한 것'을 적고 정답 대조는 derive_labels 가 한다. 필드별 카파+부트스트랩 CI.
    Sonnet 단독 쪽은 llm_labels 에 라벨이 있는 표본 항목만 센다(n 보고)."""
    import hashlib
    primary = {(r["system"], r["qid"]): r for r in judge_rows}
    ansh = {(r["system"], r["qid"]): hashlib.sha1(r["_answer"].encode("utf-8")).hexdigest() for r in judge_rows}
    out = []
    for field in ("status", "address", "type", "lenient", "strict"):
        for pair in ("B vs primary(dictionary+Sonnet)", "B vs Sonnet-only"):
            x, y = [], []
            n_total = len(raw_b)
            for kk, rb in raw_b.items():
                tr = store_by_id[kk[1].split("-")[0]]
                lb = derive_labels(rb, tr)
                if pair.startswith("B vs primary"):
                    pr = primary.get(kk)
                    if pr is None:
                        continue
                    res = pr["status"] in ("open", "closed", "unknown")
                    strict = pr["correct_strict"]
                    if pr["status"] == "unknown" or (pr["status"] in ("open", "closed") and pr["status"] != tr["truth"]):
                        strict = False
                    ly = {"status": pr["status"], "address": pr["address"], "type": pr["type"],
                          "lenient": (pr["status"] == tr["truth"]) if res else None, "strict": strict if res else None}
                else:
                    lab = llm_labels.get(f"{kk[0]}|{kk[1]}")
                    if not lab or (lab.get("answer_sha1") and lab["answer_sha1"] != ansh.get(kk)):
                        continue
                    ly = derive_labels({"status": lab["status"], "stated_address": lab.get("stated_address") or "",
                                        "stated_type": lab.get("stated_type") or ""}, tr)
                if lb[field] in (None, "review", "na") or ly[field] in (None, "review", "na"):
                    continue
                x.append(str(lb[field]))
                y.append(str(ly[field]))
            r = kappa_with_ci(x, y) if x else {"n": 0, "agreement": float("nan"), "kappa": float("nan"),
                                              "kappa_ci_lo": float("nan"), "kappa_ci_hi": float("nan")}
            r.update(field=field, pair=pair, n_excluded_unresolved_or_na=n_total - len(x))
            out.append(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["draw", "kappa"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--dryrun", action="store_true")
    ap.add_argument("--a"); ap.add_argument("--b")
    ap.add_argument("--search-validity", default="strict", choices=["strict", "searches_only"])
    a = ap.parse_args(argv)
    import load_data as L, auto_judge as J
    answers, _, _ = L.load_answers(a.search_validity)
    store = {r["item_id"]: r for r in L.load_sample()}
    if a.cmd == "draw":
        keys, note = draw_sample(answers)
        p = write_sheets(keys, answers, a.out, a.dryrun)
        print(f"drew {len(keys)} -> {p} {note}")
    else:
        rows = J.judge_all(answers, store, J.load_llm_labels(Path(a.out) / "llm_labels.jsonl"))
        for r in compute_kappas(a.out, rows, store, a.a, a.b):
            print(r)


if __name__ == "__main__":
    main()
