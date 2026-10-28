#!/usr/bin/env python3
# [Define404] 004 지원사업 질문: 10문항 배치 생성
# 입력: sampling/sample.csv, collect/question_templates.json
# 출력: collect/batches/<시스템>_ko_NNN.json, collect/batches/MANIFEST.json
# 응답 에이전트는 배치 파일의 qid·question만 본다. 정답 칸(apply_end 등)은 넣지 않는다.

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SYSTEMS = ["S-search"]          # 응답 시스템 1개: Claude Sonnet, 웹 검색 조건
BATCH_SIZE = 10


def main():
    tpl = json.loads((HERE / "question_templates.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(ROOT / "sampling" / "sample.csv", encoding="utf-8")))
    out = HERE / "batches"
    out.mkdir(exist_ok=True)
    manifest = []
    for system in SYSTEMS:
        for i in range(0, len(rows), BATCH_SIZE):
            chunk = rows[i:i + BATCH_SIZE]
            name = f"{system}_ko_{i // BATCH_SIZE + 1:03d}"
            items = [{"qid": r["qid"], "lang": "ko", "question": tpl["ko"].format(title=r["title"])} for r in chunk]
            (out / f"{name}.json").write_text(json.dumps(
                {"batch": name, "system": system, "lang": "ko", "items": items},
                ensure_ascii=False, indent=1), encoding="utf-8")
            manifest.append({"batch": name, "system": system, "lang": "ko", "n": len(items),
                             "output": f"collect/raw/{system}/{name}.jsonl"})
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"배치 {len(manifest)}개, 문항 {sum(m['n'] for m in manifest)}개, 템플릿 {tpl['version']}")


if __name__ == "__main__":
    main()
