#!/usr/bin/env python3
# [Define404] 005 영업 행정 질문: 표본 추출 (시드 고정)
# 입력: sampling/raw/minwon_<공공데이터포털 번호>.csv (시군구 민원사무편람 6개, 2026-11-10 내려받음, SHA256은 raw/SHA256SUMS)
# 출력: sampling/sample.csv, sampling/sample_log.txt
# 실행: python3 sampling/draw_sample.py  (표준 라이브러리만 쓴다)

import csv
import hashlib
import io
import random
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
SEED = 20261110
N_TARGET = 200

# 공공데이터포털 번호: (시군구, 민원명 열, 처리기간 열, 수수료 열, 근거법령 열, 편람 기준일)
FILES = {
    "15148494": ("경상북도 김천시", "민원사무명", "처리기간", "수수료", "관련법규", "2025-09-03"),
    "15149514": ("서울특별시 강서구", "민원사무명", "처리기간", "수수료", "관련법규", "2025-09-16"),
    "15153992": ("경상남도 창녕군", "제목", "처리기간", "수수료", "근거법규", "2025-11-25"),
    "15154160": ("강원특별자치도 강릉시", "민원사무명", "처리기한", "수수료", "관련법규", "2025-11-21"),
    "15164706": ("경기도 시흥시", "제목", "처리기한", "수수료", "근거법령", "2026-09-11"),
    "15166216": ("대구광역시 북구", "업무명", "민원처리기간", "수수료", "관련법규", "2026-09-03"),
}

# 영업을 새로 시작할 때 내는 민원만 남긴다: 업종 낱말 + 신고·등록·허가·지정, 변경·폐업·재발급 등은 뺀다
BIZ = re.compile(r"업")
ACT = re.compile(r"신고|등록|허가|지정")
EXCL = re.compile(r"폐업|휴업|재개|변경|승계|재발급|재교부|양도|양수|말소|취소|갱신|정정|확인|증명|발급|열람|합병|상속|지위|사본|교부|반납|철회|위치|이전")


def load(pk):
    b = (RAW / f"minwon_{pk}.csv").read_bytes()
    for enc in ("utf-8-sig", "cp949"):
        try:
            return list(csv.DictReader(io.StringIO(b.decode(enc))))
        except UnicodeDecodeError:
            continue
    raise ValueError(pk)


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def norm_period(s):
    """단일값만 정답으로 쓴다: '즉시' 또는 'N일'. 괄호 안 보충(토·일 제외 등)은 지운다."""
    s = re.sub(r"\(.*?\)", "", clean(s)).strip()
    s = re.sub(r"^처리기간\s*", "", s).strip()
    if s == "즉시":
        return "즉시"
    m = re.fullmatch(r"(\d+)\s*일(\s*이내)?", s)
    return f"{int(m.group(1))}일" if m else None


def norm_fee(s):
    """단일값만 정답으로 쓴다: '무료' 또는 'N원'."""
    s = clean(s)
    if s in ("무료", "없음", "0원", "면제", "수수료 없음", "-"):
        return "무료"
    m = re.fullmatch(r"([\d,]+)\s*원", s)
    return f"{int(m.group(1).replace(',', ''))}원" if m else None


def period_group(p):
    # H2 층: 짧음 = 즉시~3일, 김 = 4일 이상
    return "short" if p == "즉시" or int(p[:-1]) <= 3 else "long"


def main():
    log, reasons, pool = [], Counter(), []
    for pk, (city, nc, pc, fc, lc, asof) in FILES.items():
        rows = load(pk)
        log.append(f"{city} ({pk}, 기준일 {asof}): {len(rows)}행")
        for r in rows:
            name = clean(r.get(nc))
            if not name:
                reasons["no-name"] += 1
                continue
            if not (BIZ.search(name) and ACT.search(name)) or EXCL.search(name):
                reasons["not-business-start"] += 1
                continue
            if len(name) < 6:
                reasons["short-name"] += 1
                continue
            p, f = norm_period(r.get(pc)), norm_fee(r.get(fc))
            if not p or not f:
                reasons["period-or-fee-not-single"] += 1
                continue
            pool.append({"pk": pk, "city": city, "name": name, "period": p, "fee": f,
                         "law": clean(r.get(lc))[:300], "asof": asof})
    key = Counter((x["city"], x["name"]) for x in pool)
    dup = [x for x in pool if key[(x["city"], x["name"])] > 1]
    pool = [x for x in pool if key[(x["city"], x["name"])] == 1]
    reasons["dup-in-city"] = len(dup)
    log.append(f"제외: {dict(reasons)}")
    log.append(f"후보: {len(pool)}")
    pool.sort(key=lambda x: (x["pk"], x["name"]))
    rng = random.Random(SEED)
    rng.shuffle(pool)
    sample = pool[:N_TARGET]
    for i, x in enumerate(sample, 1):
        x["qid"] = f"B{i:03d}"
        x["pgroup"] = period_group(x["period"])
        x["paid"] = "free" if x["fee"] == "무료" else "paid"
    cols = ["qid", "pk", "city", "name", "period", "fee", "pgroup", "paid", "asof", "law"]
    out = HERE / "sample.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for x in sample:
            w.writerow({c: x[c] for c in cols})
    log.append(f"표본: {len(sample)}, 시드 {SEED}")
    log.append(f"시군구별: {dict(Counter(x['city'] for x in sample))}")
    log.append(f"처리기간 층: {dict(Counter(x['pgroup'] for x in sample))}")
    log.append(f"수수료 유무: {dict(Counter(x['paid'] for x in sample))}")
    log.append(f"sample.csv SHA256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
    (HERE / "sample_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
