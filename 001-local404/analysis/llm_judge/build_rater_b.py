"""독립 판정자 B 입력 만들기. 모델·검색·네트워크를 호출하지 않는다.

human_sample.draw_sample 과 같은 방식(시드 config.SEED=20261021, 분석 대상 유효 답 전체에서 200답)으로 최종 풀에서 표본을 뽑아
  in_b/B001.jsonl, B002.jsonl  (각 100줄; item_id, lang, question, answer 뿐 — 정답·시스템·qid 없음)
  rater_b_key.jsonl            (item_id -> system, qid, batch, answer_sha1; 판정자는 읽지 않는다)
를 쓴다. L-mem 유효 답이 4,000 미만이면 거부(--force 로 시험 가능). --dry 는 파일을 쓰지 않고 요약만 낸다.

  python build_rater_b.py [--force] [--dry]
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.dont_write_bytecode = True
import config as C            # noqa: E402
import load_data as L         # noqa: E402
import human_sample as HS     # noqa: E402
from build_inputs import question_map   # noqa: E402

IN_B, KEY_B = HERE / "in_b", HERE / "rater_b_key.jsonl"
LMEM_FULL = 4000
PER_BATCH = 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="L-mem 이 4,000 미만이어도 진행(시험용)")
    ap.add_argument("--dry", action="store_true", help="파일을 쓰지 않고 요약만")
    a = ap.parse_args()
    answers, inv, _ = L.load_answers("strict")
    lmem = next((r["valid"] for r in inv if r["system"] == "L-mem"), 0)
    if lmem < LMEM_FULL and not a.force:
        sys.exit(f"REFUSED: L-mem valid answers {lmem} < {LMEM_FULL}. 수집 완료 후 실행하거나 --force(시험용).")
    keys, note = HS.draw_sample(answers)
    if len(keys) != HS.C.HUMAN_SAMPLE_N:
        sys.exit(f"REFUSED: pool too small for a {C.HUMAN_SAMPLE_N} sample ({note})")
    by = {(x["system"], x["qid"]): x for x in answers}
    qm = question_map()
    order = list(keys)
    random.Random(C.SEED + 2).shuffle(order)          # 시스템·가게 순서 단서 제거
    lines, keyrows = {}, []
    for i, k in enumerate(order):
        b = f"B{i // PER_BATCH + 1:03d}"
        iid = f"B{i + 1:05d}"
        x = by[k]
        line = json.dumps({"item_id": iid, "lang": x["lang"], "question": qm[k], "answer": x["answer"]}, ensure_ascii=False)
        assert len(line) < 1900, (iid, len(line))
        lines.setdefault(b, []).append(line)
        keyrows.append({"item_id": iid, "system": k[0], "qid": k[1], "batch": b,
                        "answer_sha1": hashlib.sha1(x["answer"].encode("utf-8")).hexdigest()})
    by_sys = {}
    for k in order:
        by_sys[k[0]] = by_sys.get(k[0], 0) + 1
    summary = {"lmem_valid": lmem, "forced": bool(a.force and lmem < LMEM_FULL), "n": len(order),
               "batches": {b: len(v) for b, v in lines.items()}, "by_system": by_sys, "dry": a.dry,
               "args_for_workflow": {"dir": HERE.as_posix(), "count": len(lines), "sizes": {b: len(v) for b, v in lines.items()}}}
    if not a.dry:
        IN_B.mkdir(exist_ok=True)
        for b, v in lines.items():
            (IN_B / f"{b}.jsonl").write_text("\n".join(v) + "\n", encoding="utf-8", newline="\n")
        KEY_B.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keyrows), encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
