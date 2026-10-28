"""메뉴 번역 편 표본 추출 v1 (2026-10-28). 모집단 = sampling/raw/hansik_menu_800_20261028.csv (778행).
층 = 한국어 요리명 끝말로 정한 음식 갈래(규칙은 CATEGORY_RULES, 위에서부터 첫 일치). 비례 배분, 층마다 최소 5.
시드 20261028. 결과 sampling/sample_v1.csv, 기록 sampling/sample_v1_log.txt."""
import csv, hashlib, random, re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "raw" / "hansik_menu_800_20261028.csv"
OUT = HERE / "sample_v1.csv"
SEED, N = 20261028, 180

CATEGORY_RULES = [
    ("정식·상차림", r"(정식|백반|한정식|상|한마리|신선로)$"),
    ("밥·죽", r"(밥|죽|덮밥|비빔밥|국밥|볶음밥|초밥|주먹밥|누룽지|옹심이)$"),
    ("면", r"(면|국수|국시|냉면|라면|우동|칼국수|수제비|쫄면|당면|사발)$"),
    ("국·탕", r"(국|탕|곰탕|설렁탕|해장국|매운탕|삼계탕|개장|백숙|순두부)$"),
    ("찌개·전골", r"(찌개|전골|지짐이|뚝배기|강된장)$"),
    ("찜·조림·수육", r"(찜|조림|갈비찜|장조림|수육|머릿고기|순대|족발|편육|찜닭|삼합|선)$"),
    ("구이·볶음·튀김", r"(구이|볶음|튀김|바비큐|불고기|갈비|삼겹살|강정|부침|전|빈대떡|지짐|떡볶이|라볶이|두루치기|주물럭|치킨|꼬치|적|로스|통닭|오리|너비아니|호롱|뱅뱅|굴비|편채|김)$"),
    ("무침·김치·반찬", r"(무침|김치|깍두기|겉절이|장아찌|나물|쌈|젓갈|젓|샐러드|절임|잡채|채|회|묵|구절판)$"),
    ("떡·한과·음료", r"(떡|한과|약과|다식|엿|정과|차|주|막걸리|식혜|수정과|화채|음료|쌍화차)$"),
    ("장·양념", r"(장|식초|초|기름|소금|가루|액젓)$"),
]

def category(name):
    key = re.sub(r"\s", "", name)
    for cat, pat in CATEGORY_RULES:
        if re.search(pat, key):
            return cat
    return "기타"

def main():
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    for r in rows:
        r["category"] = category(r["ko"])
    by = {}
    for r in rows:
        by.setdefault(r["category"], []).append(r)
    cnt = Counter(r["category"] for r in rows)
    # 비례 배분(최대 나머지법), 층마다 최소 5
    quota = {c: max(5, int(N * cnt[c] / len(rows))) for c in cnt}
    while sum(quota.values()) < N:
        c = max(cnt, key=lambda k: N * cnt[k] / len(rows) - quota[k])
        quota[c] += 1
    while sum(quota.values()) > N:
        c = max((k for k in cnt if quota[k] > 5), key=lambda k: quota[k] - N * cnt[k] / len(rows))
        quota[c] -= 1
    rng = random.Random(SEED)
    sample = []
    for c in sorted(by):
        cand = sorted(by[c], key=lambda r: int(r["no"]))
        rng.shuffle(cand)
        sample += cand[:quota[c]]
    sample.sort(key=lambda r: int(r["no"]))
    for i, r in enumerate(sample, 1):
        r["sid"] = f"M{i:03d}"
    fields = ["sid", "no", "category", "ko", "latin", "en", "ja", "zh_hans", "zh_hant", "bbsSeq"]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r[k] for k in fields} for r in sample)
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    log = [f"원천 {SRC.name} SHA256 {hashlib.sha256(SRC.read_bytes()).hexdigest()}", f"모집단 {len(rows)}행, 시드 {SEED}, 표본 {len(sample)}",
           "층(모집단 수 → 배분):"] + [f"  {c}: {cnt[c]} → {quota[c]}" for c in sorted(cnt)] + [f"결과 {OUT.name} SHA256 {digest}"]
    (HERE / "sample_v1_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))

if __name__ == "__main__":
    main()
