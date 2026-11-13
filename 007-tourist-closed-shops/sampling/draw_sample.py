"""8호 관광객 추천 식당 폐업 비율: 시군구 표본 추출 (2026-11-14).
원천: 1편과 같은 지방행정 인허가 일반음식점 파일(2026-10-21 수신, SHA256 2b548c6e...24b4).
단위: 시군구(주소 첫 두 토큰, 세종은 시도 하나). 1편 region_parts·region_class 규칙을 그대로 쓴다.
대상: 영업 중 일반음식점이 100곳 이상인 시군구. 층: 광역/도, 층마다 75곳, 시드 20261114.
"""
import csv, os, random, sys, json, hashlib
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "001-local404", "sampling", "raw", "식품_일반음식점_20261021.csv")
SEED = 20261114
PER_STRATUM = 75
MIN_OPEN = 100
METRO = ("서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종")
OLD_GWANGJU_GU = ("동구", "서구", "남구", "북구", "광산구")
csv.field_size_limit(sys.maxsize)


def address_of(r):
    return (r["도로명주소"] or "").strip() or (r["지번주소"] or "").strip()


def region_parts(addr):
    t = addr.split()
    sido = t[0]
    sgg = sido if (sido.startswith("세종") or len(t) < 2) else t[0] + " " + t[1]
    return sido, sgg


def region_class(sido, sgg=""):
    if sido.startswith("전남광주") and sgg.split()[-1:] and sgg.split()[-1] in OLD_GWANGJU_GU:
        return "광역"
    return "광역" if sido.startswith(METRO) else "도"


def main():
    n_open, n_closed, cls = Counter(), Counter(), {}
    with open(SRC, encoding="cp949", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            a = address_of(r)
            if not a:
                continue
            sido, sgg = region_parts(a)
            last = sgg.split()[-1]
            if sgg != sido and not last.endswith(("시", "군", "구")):
                continue  # 주소 형식이 어긋난 행
            st = (r["영업상태명"] or "").strip()
            if st == "영업/정상" or st == "영업":
                n_open[sgg] += 1
            elif st == "폐업":
                n_closed[sgg] += 1
            cls[sgg] = region_class(sido, sgg)
    elig = sorted(s for s in n_open if n_open[s] >= MIN_OPEN)
    rng = random.Random(SEED)
    out = []
    for g in ("광역", "도"):
        pool = [s for s in elig if cls[s] == g]
        rng.shuffle(pool)
        out += [(g, s) for s in pool[:PER_STRATUM]]
    with open(os.path.join(HERE, "sample.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["area_id", "stratum", "sido", "sigungu", "open_n", "closed_n"])
        for i, (g, s) in enumerate(out, 1):
            w.writerow([f"A{i:03d}", g, s.split()[0], s, n_open[s], n_closed[s]])
    pools = Counter(cls[s] for s in elig)
    log = {"seed": SEED, "min_open": MIN_OPEN, "eligible": len(elig), "eligible_by_stratum": dict(pools),
           "all_sigungu": len(cls), "sampled": len(out),
           "sample_sha256": hashlib.sha256(open(os.path.join(HERE, "sample.csv"), "rb").read()).hexdigest()}
    json.dump(log, open(os.path.join(HERE, "sample_log.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(log, ensure_ascii=False))


if __name__ == "__main__":
    main()
