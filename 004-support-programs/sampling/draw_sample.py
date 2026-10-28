#!/usr/bin/env python3
# [Define404] 004 지원사업 질문: 층화 무작위 표본 추출 (시드 고정)
# 입력: sampling/raw/bizinfo_ongoing_20261028.csv, bizinfo_expired_20261028.csv
#       (기업마당 지원사업 공고 엑셀 내려받기 2026-10-28, SHA256은 raw/SHA256SUMS)
# 출력: sampling/sample.csv, sampling/sample_log.txt
# 실행: python3 sampling/draw_sample.py  (표준 라이브러리만 쓴다)

import csv
import hashlib
import random
import re
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
SEED = 20261028
FIXED_AT = date(2026, 10, 28)          # 정답 고정 시점 (엑셀 내려받은 날)
COLLECT_END = date(2026, 11, 11)       # 수집 마감 예정일 (prereg 3절)
PER_STRATUM = 50                       # 층마다 50곳, 4개 층 = 200곳

# 진행 중 층: 이미 접수가 시작됐고, 수집 마감 뒤에도 최소 7일 남는 공고
ONGOING_END_MIN = date(2026, 11, 18)
ONGOING_END_MAX = date(2027, 6, 30)    # 상시·연중 공고(2027-07 이후 마감)는 뺀다
# 마감 층: 수집 시작 기준 최소 7일 전에 마감됐고, 최근 3개월 안에 마감된 공고
EXPIRED_END_MIN = date(2026, 8, 1)
EXPIRED_END_MAX = date(2026, 10, 21)

LOCAL_RE = re.compile(r"(특별시|광역시|특별자치시|특별자치도|도)$")


def parse_date(s):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s or "")
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def load(name, status):
    rows = []
    with open(RAW / name, encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            row["status"] = status
            row["pblancId"] = row["공고상세URL"].rsplit("=", 1)[-1]
            rows.append(row)
    return rows


def jurisdiction(row):
    # 지자체 공고 = 소관부처가 시·도 이름. 그 밖은 중앙부처(청·위원회 포함).
    return "local" if LOCAL_RE.search(row["소관부처"].strip()) else "central"


def eligible(row):
    s, e = parse_date(row["신청시작일자"]), parse_date(row["신청종료일자"])
    if not s or not e:
        return False, "no-date"
    if len(row["공고명"].strip()) < 10:
        return False, "short-title"
    if row["status"] == "ongoing":
        if s > FIXED_AT:
            return False, "not-yet-open"
        if not (ONGOING_END_MIN <= e <= ONGOING_END_MAX):
            return False, "ongoing-end-out-of-window"
    else:
        if not (EXPIRED_END_MIN <= e <= EXPIRED_END_MAX):
            return False, "expired-end-out-of-window"
    return True, ""


def main():
    rows = load("bizinfo_ongoing_20261028.csv", "ongoing") + load("bizinfo_expired_20261028.csv", "expired")
    log = []
    log.append(f"원천 행: 진행 {sum(r['status']=='ongoing' for r in rows)}, 마감 {sum(r['status']=='expired' for r in rows)}")

    # 같은 공고명이 두 번 이상이면 전부 뺀다(어느 공고를 묻는지 애매해진다)
    title_count = Counter(r["공고명"].strip() for r in rows)
    reasons = Counter()
    pool = {("ongoing", "central"): [], ("ongoing", "local"): [], ("expired", "central"): [], ("expired", "local")
            : []}
    for r in rows:
        if title_count[r["공고명"].strip()] > 1:
            reasons["duplicate-title"] += 1
            continue
        ok, why = eligible(r)
        if not ok:
            reasons[why] += 1
            continue
        pool[(r["status"], jurisdiction(r))].append(r)
    log.append("제외 사유: " + ", ".join(f"{k} {v}" for k, v in sorted(reasons.items())))
    for k, v in pool.items():
        log.append(f"후보 {k[0]}/{k[1]}: {len(v)}")

    rng = random.Random(SEED)
    sample = []
    for key in [("ongoing", "central"), ("ongoing", "local"), ("expired", "central"), ("expired", "local")]:
        cand = sorted(pool[key], key=lambda r: r["pblancId"])
        rng.shuffle(cand)
        picked = cand[:PER_STRATUM]
        if len(picked) < PER_STRATUM:
            log.append(f"경고: {key} 후보 부족 {len(picked)}")
        for i, r in enumerate(picked):
            sample.append({
                "qid": f"S{len(sample)+1:03d}",
                "pblancId": r["pblancId"],
                "status": key[0],
                "jurisdiction": key[1],
                "title": r["공고명"].strip(),
                "ministry": r["소관부처"].strip(),
                "agency": r["사업수행기관"].strip(),
                "field": r["지원분야"].strip(),
                "apply_start": r["신청시작일자"],
                "apply_end": r["신청종료일자"],
                "registered": r["등록일자"],
                "url": r["공고상세URL"],
            })
    # 질문 순서도 시드로 섞는다(배치 안에서 층이 섞이게)
    rng.shuffle(sample)
    for i, s in enumerate(sample):
        s["qid"] = f"S{i+1:03d}"

    out = HERE / "sample.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sample[0].keys()))
        w.writeheader()
        w.writerows(sample)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    log.append(f"표본 {len(sample)}곳, 시드 {SEED}, sample.csv SHA256 {sha}")
    (HERE / "sample_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
