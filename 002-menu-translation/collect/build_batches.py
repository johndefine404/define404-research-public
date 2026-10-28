"""질문 배치 생성 (2026-10-28). 표본 sampling/sample_v1.csv x 언어(en, ja) → collect/batches/<시스템>_<언어>_<번호>.json (10문항).
시스템은 S-search(Claude Sonnet, 웹 검색) 하나. 문항 순서는 시드 20261028로 언어마다 섞는다. MANIFEST.json에 배치 목록을 적는다.
배치 파일 형식은 1편과 같다: [{"qid": "M001-en", "q": "..."}, ...]"""
import csv, json, random
from pathlib import Path

HERE = Path(__file__).parent
SAMPLE = HERE.parent / "sampling" / "sample_v1.csv"
OUT = HERE / "batches"
SYSTEMS = ["S-search"]
LANGS = ["en", "ja"]
SEED, SIZE = 20261028, 10

def main():
    tpl = json.loads((HERE / "question_templates.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    OUT.mkdir(exist_ok=True)
    manifest = []
    for system in SYSTEMS:
        for lang in LANGS:
            items = [{"qid": f"{r['sid']}-{lang}", "q": tpl[lang].format(ko=r["ko"])} for r in rows]
            random.Random(f"{SEED}-{lang}").shuffle(items)
            for i in range(0, len(items), SIZE):
                chunk = items[i:i + SIZE]
                name = f"{system}_{lang}_{i // SIZE + 1:03d}"
                (OUT / f"{name}.json").write_text(json.dumps(chunk, ensure_ascii=False, indent=0), encoding="utf-8")
                manifest.append({"batch": name, "system": system, "lang": lang, "n": len(chunk)})
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"배치 {len(manifest)}개, 문항 {sum(m['n'] for m in manifest)}개 → {OUT}")

if __name__ == "__main__":
    main()
