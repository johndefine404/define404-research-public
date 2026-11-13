#!/usr/bin/env python3
# [Define404] 007 관광객 추천 식당: 5문항 배치 생성
# 입력: sampling/sample.csv, collect/question_templates.json
# 출력: collect/batches/S-search_<언어>_NNN.json, MANIFEST.json, collect/items.csv(질문 원문 기록)
# 한 배치 = 한 언어, 서로 다른 시군구 5곳. 같은 시군구의 한국어·영어는 다른 배치(다른 에이전트)가 맡는다.
import csv, json, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SEED = 20261114
BATCH = 5
LANGS = ["ko", "en"]

SIDO_KO = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천", "대전광역시": "대전",
           "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기", "강원특별자치도": "강원", "충청북도": "충북",
           "충청남도": "충남", "전북특별자치도": "전북", "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주"}
SIDO_EN = {"서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "대전": "Daejeon", "울산": "Ulsan",
           "세종": "Sejong", "경기": "Gyeonggi-do", "강원": "Gangwon", "충북": "Chungcheongbuk-do",
           "충남": "Chungcheongnam-do", "전북": "Jeonbuk", "경북": "Gyeongsangbuk-do", "경남": "Gyeongsangnam-do",
           "제주": "Jeju", "광주": "Gwangju", "전남": "Jeollanam-do"}
OLD_GWANGJU_GU = ("동구", "서구", "남구", "북구", "광산구")

# 국어의 로마자 표기법(2000) 기본 대응. 자음 동화 규칙은 넣지 않는다(한글을 함께 적으므로 장소 특정에는 지장 없음).
CHO = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
JUNG = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
JONG = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t", "ng", "t", "t", "k", "t", "p", "t"]


def rr(word):
    out = []
    for ch in word:
        c = ord(ch) - 0xAC00
        if 0 <= c < 11172:
            out.append(CHO[c // 588] + JUNG[(c % 588) // 28] + JONG[c % 28])
        else:
            out.append(ch)
    return "".join(out)


def rr_unit(name):
    # 강릉시 -> Gangneung-si 꼴. 끝 글자(시·군·구)를 하이픈으로 뗀다.
    stem, suf = name[:-1], name[-1]
    s = rr(stem)
    return s[:1].upper() + s[1:] + "-" + {"시": "si", "군": "gun", "구": "gu"}[suf]


def place(row):
    sido, sgg = row["sido"], row["sigungu"]
    if sido.startswith("전남광주"):
        unit = sgg.split()[-1]
        short = "광주" if unit in OLD_GWANGJU_GU else "전남"
    else:
        short = SIDO_KO[sido]
    if sgg == sido:  # 세종
        return short, short, "Sejong"
    unit = sgg.split()[-1]
    ko = f"{short} {unit}"
    en = f"{rr_unit(unit)}, {SIDO_EN[short]} ({ko})"
    return ko, unit, en


def ro(word):
    last = ord(word[-1]) - 0xAC00
    if 0 <= last < 11172:
        jong = last % 28
        return "로" if jong in (0, 8) else "으로"
    return "로"


def main():
    tpl = json.loads((HERE / "question_templates.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(ROOT / "sampling" / "sample.csv", encoding="utf-8")))
    out = HERE / "batches"
    out.mkdir(exist_ok=True)
    manifest, items_log = [], []
    rng = random.Random(SEED)
    for lang in LANGS:
        order = rows[:]
        rng.shuffle(order)
        for b in range(0, len(order), BATCH):
            name = f"S-search_{lang}_{b // BATCH + 1:03d}"
            items = []
            for r in order[b:b + BATCH]:
                ko, unit, en = place(r)
                q = tpl["ko"].format(place_ko=ko, ro=ro(ko)) if lang == "ko" else tpl["en"].format(place_en=en)
                qid = f"{r['area_id']}_{lang}"
                items.append({"qid": qid, "lang": lang, "question": q})
                items_log.append({"qid": qid, "area_id": r["area_id"], "lang": lang, "batch": name, "question": q})
            (out / f"{name}.json").write_text(json.dumps({"batch": name, "system": "S-search", "lang": lang, "items": items},
                                                         ensure_ascii=False, indent=1), encoding="utf-8")
            manifest.append({"batch": name, "system": "S-search", "lang": lang, "n": len(items),
                             "output": f"collect/raw/S-search/{name}.jsonl"})
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(HERE / "items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(items_log[0]))
        w.writeheader()
        w.writerows(items_log)
    print(f"배치 {len(manifest)}개, 문항 {len(items_log)}개, 템플릿 {tpl['version']}")


if __name__ == "__main__":
    main()
