#!/usr/bin/env python3
# [Define404]
"""Local404 표본 추출. 표준 라이브러리만 쓴다.

입력: raw/식품_일반음식점_20261021.csv (CP949)
출력: sample.csv (UTF-8), sample_log.txt

제외 판정 순서: 주소 없음 -> 상호 2자 미만 -> 같은 시군구 동일 상호(2행 이상)
-> 폐업인데 폐업일자 없음 -> 영업/폐업 외 상태.
동일 상호 집계는 주소와 상호 조건을 통과한 행 전부(영업·폐업·기타 상태 불문)로 한다.
"""
import csv
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "식품_일반음식점_20261021.csv")
OUT = os.path.join(HERE, "sample.csv")
LOG = os.path.join(HERE, "sample_log.txt")
SEED = 20261021

METRO = ("서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종")
OPEN_N = 200
CLOSED_N = 50
YEAR_BINS = ["~2019", "2020-2022", "2023-2024", "2025-2026"]

csv.field_size_limit(sys.maxsize)


def address_of(row):
    a = (row["도로명주소"] or "").strip()
    if not a:
        a = (row["지번주소"] or "").strip()
    return a


def region_parts(addr):
    toks = addr.split()
    sido = toks[0]
    if sido.startswith("세종") or len(toks) < 2:
        sigungu = sido
    else:
        sigungu = toks[0] + " " + toks[1]
    return sido, sigungu


def name_key(name):
    return "".join(name.split()).lower()


# 2026년 원본은 광주광역시와 전라남도를 "전남광주통합특별시" 하나로 적는다.
# 옛 광주광역시 5개 구는 도시 성격이 그대로이므로 "광역"으로 분류한다(2026-10-21 결정).
OLD_GWANGJU_GU = ("동구", "서구", "남구", "북구", "광산구")


def region_class(sido, sigungu=""):
    if sido.startswith("전남광주") and sigungu.split()[-1:] and sigungu.split()[-1] in OLD_GWANGJU_GU:
        return "광역"
    return "광역" if sido.startswith(METRO) else "도"


def year_bin(y):
    if y <= 2019:
        return "~2019"
    if y <= 2022:
        return "2020-2022"
    if y <= 2024:
        return "2023-2024"
    return "2025-2026"


def rows():
    with open(SRC, encoding="cp949", errors="replace", newline="") as f:
        yield from csv.DictReader(f)


def main():
    # 1차: 동일 상호 집계
    dup = Counter()
    for r in rows():
        addr = address_of(r)
        if not addr:
            continue
        nk = name_key(r["사업장명"] or "")
        if len(nk) < 2:
            continue
        dup[(region_parts(addr)[1], nk)] += 1

    # 2차: 제외 판정과 층 배정
    total = 0
    excl = Counter()
    status_seen = Counter()
    odd = Counter()
    strata = defaultdict(list)
    for r in rows():
        total += 1
        status = (r["영업상태명"] or "").strip()
        status_seen[status] += 1
        if "�" in "".join(v or "" for v in r.values()):
            odd["디코딩 대체문자 포함 행"] += 1
        addr = address_of(r)
        if not addr:
            excl["주소 없음"] += 1
            continue
        name = (r["사업장명"] or "").strip()
        nk = name_key(name)
        if len(nk) < 2:
            excl["상호 2자 미만"] += 1
            continue
        sido, sigungu = region_parts(addr)
        if dup[(sigungu, nk)] >= 2:
            excl["같은 시군구 동일 상호"] += 1
            continue
        closed_date = (r["폐업일자"] or "").strip()
        reg = region_class(sido, sigungu)
        if status == "폐업":
            if not closed_date:
                excl["폐업인데 폐업일자 없음"] += 1
                continue
            try:
                y = int(closed_date[:4])
            except ValueError:
                excl["폐업일자 형식 오류"] += 1
                continue
            if y > 2026 or y < 1900:
                odd[f"폐업연도 범위 밖 {y}"] += 1
            key = f"폐업|{reg}|{year_bin(y)}"
        elif status == "영업/정상":
            key = f"영업|{reg}"
        else:
            excl[f"영업/폐업 외 상태({status or '빈칸'})"] += 1
            continue
        strata[key].append({
            "관리번호": r["관리번호"].strip(),
            "사업장명": name,
            "영업상태명": status,
            "폐업일자": closed_date,
            "인허가일자": (r["인허가일자"] or "").strip(),
            "시도": sido,
            "시군구": sigungu,
            "주소": addr,
            "업태구분명": (r["업태구분명"] or "").strip(),
            "데이터갱신시점": (r["데이터갱신시점"] or "").strip(),
        })

    targets = {f"영업|{g}": OPEN_N for g in ("광역", "도")}
    for g in ("광역", "도"):
        for b in YEAR_BINS:
            targets[f"폐업|{g}|{b}"] = CLOSED_N

    rng = random.Random(SEED)
    picked = []
    report = []
    for key in sorted(targets):
        cands = sorted(strata.get(key, []), key=lambda d: d["관리번호"])
        n = min(targets[key], len(cands))
        if n < targets[key]:
            odd[f"층 모집단 부족 {key}"] += 1
        draw = rng.sample(cands, n)
        report.append((key, len(cands), n))
        for d in draw:
            picked.append((key, d))

    fields = ["item_id", "stratum", "관리번호", "사업장명", "영업상태명", "폐업일자",
              "인허가일자", "시도", "시군구", "주소", "업태구분명", "데이터갱신시점"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for i, (key, d) in enumerate(picked, 1):
            w.writerow({"item_id": f"L{i:04d}", "stratum": key, **d})

    kept = sum(len(v) for v in strata.values())
    lines = [
        "Local404 표본 추출 로그",
        f"입력: {os.path.relpath(SRC, HERE)}",
        f"시드: {SEED}",
        "",
        f"원본 행 수: {total}",
        "영업상태명 분포(원본):",
    ]
    lines += [f"  {k or '빈칸'}: {v}" for k, v in status_seen.most_common()]
    lines += ["", "제외 사유별 건수(판정 순서대로 첫 사유 1회만 집계):"]
    lines += [f"  {k}: {v}" for k, v in excl.most_common()]
    lines += [f"  제외 합계: {sum(excl.values())}", f"층 배정 행 수: {kept}", "",
              "층별 모집단 수 / 추출 수 (추출 순서):"]
    lines += [f"  {k}: 모집단 {p} / 추출 {n}" for k, p, n in report]
    lines += ["", f"최종 표본 수: {len(picked)}"]
    if odd:
        lines += ["", "참고(이상 신호):"]
        lines += [f"  {k}: {v}" for k, v in odd.most_common()]
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
