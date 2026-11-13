#!/usr/bin/env python3
# [Define404] 007 관광객 추천 식당: 규칙 자동 판정 v1.0 (규칙 원문 judge/rules.md)
# 입력: collect/raw/S-search/*.jsonl, collect/items.csv, sampling/sample.csv, 1편 인허가 원천 파일
# 출력: judge/answers.csv(답 단위), judge/judged.csv(추천 가게 단위)
import csv, glob, json, os, re, sys, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT.parent / "001-local404" / "sampling" / "raw" / "식품_일반음식점_20261021.csv"
RAW = os.environ.get("D404_RAW", str(ROOT / "collect" / "raw" / "S-search"))
csv.field_size_limit(sys.maxsize)
LIMIT_WORDS = ("검색 한도", "search limit", "rate limit", "검색을 수행할 수 없", "unable to search", "couldn't search", "could not search")
ROAD = re.compile(r"([가-힣0-9]+(?:대로|로|길))\s*(\d+(?:-\d+)?)")


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[^0-9a-z가-힣]", "", s)


def norm_loose(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\(\[（].*?[\)\]）]", "", s)
    n = norm(s)
    return n[:-2] if n.endswith("본점") and len(n) > 4 else n


def road_key(addr):
    m = ROAD.search(unicodedata.normalize("NFKC", addr or "").replace(" ", " "))
    return (m.group(1), m.group(2).split("-")[0]) if m else None


def area_of(addr):
    t = addr.split()
    sido = t[0]
    return sido if (sido.startswith("세종") or len(t) < 2) else t[0] + " " + t[1]


def load_registry(areas):
    reg = {a: {} for a in areas}
    with open(SRC, encoding="cp949", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            addr = (r["도로명주소"] or "").strip() or (r["지번주소"] or "").strip()
            if not addr:
                continue
            a = area_of(addr)
            if a not in reg:
                continue
            st = (r["영업상태명"] or "").strip()
            st = "영업" if st.startswith("영업") else ("폐업" if st == "폐업" else "기타")
            reg[a].setdefault(norm(r["사업장명"]), []).append((st, r["도로명주소"] or "", r["폐업일자"] or "", r["관리번호"]))
    return reg


def status_of(rows):
    sts = {r[0] for r in rows}
    return "영업" if "영업" in sts else ("폐업" if "폐업" in sts else "기타")


def match(rec, table):
    n = norm(rec.get("name", ""))
    if len(n) < 2:
        return None, None, []
    if n in table:
        return "strict", status_of(table[n]), table[n]
    nl = norm_loose(rec.get("name", ""))
    hits = [k for k in table if norm_loose(k) == nl] if len(nl) >= 2 else []
    if hits:
        rows = [x for k in hits for x in table[k]]
        return "loose_name", status_of(rows), rows
    rk = road_key(rec.get("address", ""))
    if rk and len(nl) >= 3:
        rows = []
        for k, lst in table.items():
            if len(k) >= 3 and (nl in k or k in nl):
                rows += [x for x in lst if road_key(x[1]) == rk]
        if rows:
            return "loose_addr", status_of(rows), rows
    return None, None, []


def main():
    items = {r["qid"]: r for r in csv.DictReader(open(ROOT / "collect" / "items.csv", encoding="utf-8"))}
    sample = {r["area_id"]: r for r in csv.DictReader(open(ROOT / "sampling" / "sample.csv", encoding="utf-8"))}
    answers = []
    for p in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                o["_file"] = os.path.basename(p)
                answers.append(o)
    reg = load_registry({s["sigungu"] for s in sample.values()})
    a_rows, r_rows = [], []
    for o in answers:
        it = items[o["qid"]]
        area = sample[it["area_id"]]
        ans = o.get("answer", "") or ""
        low = ans.lower()
        invalid = ""
        if not ans.strip():
            invalid = "빈 답"
        elif int(o.get("searches", 0) or 0) < 1:
            invalid = "검색 0회"
        elif any(w.lower() in low for w in LIMIT_WORDS):
            invalid = "검색 한도 문구"
        recs = o.get("recs") or []
        a_rows.append({"qid": o["qid"], "area_id": it["area_id"], "lang": it["lang"], "stratum": area["stratum"],
                       "searches": o.get("searches", 0), "n_recs": len(recs), "invalid": invalid, "file": o["_file"]})
        if invalid:
            continue
        unit = area["sigungu"].split()[-1]
        unit_stem = unit[:-1] if len(unit) > 2 else unit
        nans = norm(ans)
        for i, rec in enumerate(recs[:5], 1):
            in_ans = norm(rec.get("name", "")) in nans if norm(rec.get("name", "")) else False
            kind, st, rows = match(rec, reg[area["sigungu"]])
            addr = rec.get("address", "") or ""
            r_rows.append({
                "qid": o["qid"], "area_id": it["area_id"], "lang": it["lang"], "stratum": area["stratum"], "rec": i,
                "name": rec.get("name", ""), "address": addr, "in_answer": int(in_ans),
                "addr_in_area": int(unit_stem in addr) if addr else "",
                "match": kind or "none", "strict_status": st if kind == "strict" else "미확인",
                "loose_status": st if kind else "미확인",
                "closed_dates": ";".join(sorted({x[2] for x in rows if x[0] == "폐업" and x[2]}))[:60],
                "n_reg_rows": len(rows)})
    with open(HERE / "answers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(a_rows[0]))
        w.writeheader(); w.writerows(a_rows)
    with open(HERE / "judged.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(r_rows[0]))
        w.writeheader(); w.writerows(r_rows)
    from collections import Counter
    print("답", len(a_rows), "무효", Counter(a["invalid"] for a in a_rows if a["invalid"]),
          "추천", len(r_rows), "판정(느슨)", Counter(r["loose_status"] for r in r_rows),
          "매칭", Counter(r["match"] for r in r_rows))


if __name__ == "__main__":
    main()
