"""Local404 표본 추출 v2 (2026-10-21). v1(draw_sample.py)의 정제·제외 규칙과 지역 분류를 그대로 쓰고,
층에 '카카오 장소 등록 여부'를 더한다. 층 = 영업상태(영업/폐업) x 카카오(있음/없음) x 지역(광역/도), 층마다 100곳.
층 안 후보를 시드 20261021로 섞은 뒤 앞에서부터 카카오 키워드 검색으로 판정해 채운다.
카카오 '있음' = 검색 결과 중 상호(공백 제거·소문자)가 같거나 한쪽이 다른 쪽을 포함(2자 이상)하고, 주소에 같은 시도(약칭)와 시군구 이름이 함께 있는 장소가 1곳 이상.
카카오 결과는 장소 id와 등록 여부만 남긴다(장소명·주소·분류 원문은 저장하지 않는다)."""
import csv, json, random, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import importlib.util
HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("v1", HERE / "draw_sample.py"); v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
KEY = re.search(r"^KAKAO_REST_KEY=(.+)$", (HERE.parents[3] / "tools/leads/.env").read_text(), re.M).group(1).strip().strip('"')
SEED = 20261021; N = 100

def norm(s): return re.sub(r"[\s()\[\]·.,'\-]", "", s or "").lower()

SIDO_SHORT = {"서울특별시": ["서울"], "부산광역시": ["부산"], "대구광역시": ["대구"], "인천광역시": ["인천"], "광주광역시": ["광주"],
    "대전광역시": ["대전"], "울산광역시": ["울산"], "세종특별자치시": ["세종"], "경기도": ["경기"], "강원특별자치도": ["강원"], "강원도": ["강원"],
    "충청북도": ["충북"], "충청남도": ["충남"], "전북특별자치도": ["전북"], "전라북도": ["전북"], "전라남도": ["전남"], "경상북도": ["경북"],
    "경상남도": ["경남"], "제주특별자치도": ["제주"], "전남광주통합특별시": ["광주", "전남"]}

def kakao(row):
    gu = row["시군구"].split()[-1]
    shorts = SIDO_SHORT.get(row["시도"], [row["시도"][:2]])
    q = f'{shorts[0]} {gu} {row["사업장명"]}'
    url = "https://dapi.kakao.com/v2/local/search/keyword.json?" + urllib.parse.urlencode({"query": q, "size": 15})
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": f"KakaoAK {KEY}"}), timeout=20)); break
        except Exception:
            time.sleep(1)
    else:
        return None, q, []
    n = norm(row["사업장명"]); hits = []
    for p in d.get("documents", []):
        pn = norm(p["place_name"]); addr = p.get("address_name", "") + " " + p.get("road_address_name", "")
        if gu in addr and any(addr.startswith(x) or (" " + x) in addr for x in shorts) and len(n) >= 2 and (pn == n or n in pn or (len(pn) >= 2 and pn in n)):
            hits.append({"id": p.get("id")})
    return bool(hits), q, hits


def pools():
    from collections import Counter, defaultdict
    dup = Counter()
    for r in v1.rows():
        a = v1.address_of(r)
        nk = v1.name_key(r["사업장명"] or "")
        if a and len(nk) >= 2:
            dup[(v1.region_parts(a)[1], nk)] += 1
    out = defaultdict(list)
    for r in v1.rows():
        a = v1.address_of(r); name = (r["사업장명"] or "").strip(); nk = v1.name_key(name)
        if not a or len(nk) < 2: continue
        sido, sigungu = v1.region_parts(a)
        if dup[(sigungu, nk)] >= 2: continue
        st = (r["영업상태명"] or "").strip(); cd = (r["폐업일자"] or "").strip()
        if st == "폐업" and not cd[:4].isdigit(): continue
        if st not in ("폐업", "영업/정상"): continue
        out[("영업" if st == "영업/정상" else "폐업", v1.region_class(sido, sigungu))].append({
            "관리번호": r["관리번호"].strip(), "사업장명": name, "영업상태명": st, "폐업일자": cd,
            "인허가일자": (r["인허가일자"] or "").strip(), "시도": sido, "시군구": sigungu, "주소": a,
            "업태구분명": (r["업태구분명"] or "").strip(), "데이터갱신시점": (r["데이터갱신시점"] or "").strip()})
    return out

def main():
    P = pools(); rng = random.Random(SEED); picked = []; log = []; checks = []
    for cell in sorted(P):
        cand = sorted(P[cell], key=lambda x: x["관리번호"]); rng.shuffle(cand)
        need = {True: N, False: N}; got = {True: [], False: []}; i = 0; tried = 0
        with ThreadPoolExecutor(8) as ex:
            while (need[True] or need[False]) and i < len(cand):
                batch = cand[i:i + 64]; i += 64
                for row, (has, q, hits) in zip(batch, ex.map(kakao, batch)):
                    tried += 1
                    if has is None: continue
                    checks.append({"관리번호": row["관리번호"], "query": q, "kakao": has, "hits": hits})
                    if need[has]:
                        need[has] -= 1; got[has].append(dict(row, kakao="있음" if has else "없음", kakao_place_ids=",".join(h["id"] for h in hits), 측정일=time.strftime("%Y-%m-%d")))
        log.append(f"{cell}: 모집단 {len(cand)}, 카카오 조회 {tried}, 있음 {len(got[True])}, 없음 {len(got[False])}, 있음 비율 {sum(c['kakao'] for c in checks[-tried:])}/{tried}")
        for has in (True, False):
            for row in got[has]:
                picked.append(dict(row, stratum=f"{cell[0]}|카카오{'있음' if has else '없음'}|{cell[1]}"))
    for k, r in enumerate(picked, 1): r["item_id"] = f"L{k:04d}"
    cols = ["item_id", "stratum", "관리번호", "사업장명", "영업상태명", "폐업일자", "인허가일자", "시도", "시군구", "주소", "업태구분명", "데이터갱신시점", "kakao", "kakao_place_ids", "측정일"]
    with open(HERE / "sample_v2.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(picked)
    with open(HERE / "kakao_checks_v2.jsonl", "w", encoding="utf-8") as f:
        for c in checks: f.write(json.dumps(c, ensure_ascii=False) + "\n")
    log.append(f"표본 {len(picked)}")
    (HERE / "sample_v2_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8"); print("\n".join(log))

if __name__ == "__main__":
    main()
