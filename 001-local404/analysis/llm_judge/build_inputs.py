"""LLM 판정 입력 만들기. 모델·검색·네트워크를 호출하지 않는다. collect/ sampling/ judge/ 는 읽기만 한다.

설계 (judge/rules.md 5절: 보조 분류는 규칙 원문만 보고 답 하나씩 분류, 정답은 보지 않는다. 정답 대조는 코드가 한다)
  - 판정자에게 주는 것: item_id, lang, question, answer 뿐. 정답·시스템 이름·조건·가게 번호(qid)는 없다.
  - item_id -> (system, qid) 대응표는 item_key.jsonl (판정자는 이 파일을 읽지 않는다. 워크플로는 in/<batch>.jsonl 하나만 읽게 한다).
  - 범위: (1) 검색 조건(H-search, S-search) 유효 답 전부, (2) H-mem 중 사전이 확신하지 못한 답(status/address/type 중 review),
          (3) H-mem 무작위 200답(시드 20261024; 사전 대 LLM 일치 점검용). H-mem 사전 상태 라벨은 4,000개 전부 unknown(확신)이라 전수는 하지 않는다.
          (4) --include-lmem: L-mem 의 review 답 전부(표본 아님; 미판정 0 을 위해) + 무작위 200답(같은 시드) + 독립 판정자 B 표본 200답. L-mem 은 수집이 끝난 뒤에 붙인다.
  - 추가 방식: 이미 item_key 에 있는 (system,qid)는 그대로 두고, 새 답만 새 번호의 새 배치로 덧붙인다(앞선 배치 결과를 다시 돌리지 않는다).
    답이 바뀐 경우(재수집으로 H-search ja 가 교체됨)는 같은 (system,qid)라도 답 해시가 달라지면 새 항목으로 덧붙인다.
  - 배치 순서는 시드로 섞어 시스템·언어 순서 단서를 없앤다.

  python build_inputs.py [--include-lmem] [--dry]
"""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.dont_write_bytecode = True
import config as C          # noqa: E402
import load_data as L       # noqa: E402
import auto_judge as J      # noqa: E402

SEED = 20261024
SAMPLE_N = 200
BATCH_TARGET = 100
IN_DIR, KEY, MAN = HERE / "in", HERE / "item_key.jsonl", HERE / "in" / "MANIFEST.json"


def sha1(t):
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


def question_map():
    qm = {}
    for system, meta in C.SYSTEMS.items():
        for f in sorted((C.COLLECT / "batches").glob(f"{meta['batch_prefix']}_*.json")):
            for it in json.loads(f.read_text(encoding="utf-8")):
                qm[(system, it["qid"])] = it["q"]
    return qm


def read_jsonl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-lmem", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    answers, _, _ = L.load_answers("strict")
    store = {r["item_id"]: r for r in L.load_sample()}
    rows = J.judge_all(answers, store, {})
    ans = {(x["system"], x["qid"]): x for x in answers}
    rev = {(r["system"], r["qid"]) for r in rows if "review" in (r["status"], r["address"], r["type"])}

    want = {}      # (system,qid) -> reason
    for k in ans:
        if k[0] in C.SUBSAMPLE_SYSTEMS:
            want[k] = "search_all"
    def add_mem(system, tag):
        keys = sorted(k for k in ans if k[0] == system)
        for k in sorted(rev & set(keys)):
            want.setdefault(k, f"{tag}_review")
        for k in sorted(random.Random(SEED).sample(keys, min(SAMPLE_N, len(keys)))):
            want[k] = (want[k] + "+" if k in want else "") + f"{tag}_agreement_sample"
    add_mem("H-mem", "Hmem")
    if a.include_lmem:
        add_mem("L-mem", "Lmem")
        # 독립 판정자 B 표본 200답(human_sample.draw_sample, 최종 풀)도 주 판정 풀에 넣는다: B 대 Sonnet 단독 카파를 200건 전부로 낸다.
        import human_sample as HS
        bkeys, _ = HS.draw_sample(list(answers))
        for k in bkeys:
            want[k] = (want[k] + "+" if k in want else "") + "raterB_sample"

    old = read_jsonl(KEY)
    done = {(o["system"], o["qid"], o["answer_sha1"]) for o in old}
    new = [k for k in sorted(want) if (k[0], k[1], sha1(ans[k]["answer"])) not in done]
    random.Random(SEED + len(old)).shuffle(new)
    qm = question_map()
    nid = max([int(o["item_id"][1:]) for o in old], default=0)
    nb = max([int(o["batch"][1:]) for o in old], default=0)
    man = json.loads(MAN.read_text(encoding="utf-8")) if MAN.exists() else []
    nbatch = max(1, math.ceil(len(new) / BATCH_TARGET)) if new else 0
    size = math.ceil(len(new) / nbatch) if new else 0
    keyrows, files = [], {}
    for bi in range(nbatch):
        chunk = new[bi * size:(bi + 1) * size]
        nb += 1
        b = f"J{nb:03d}"
        lines = []
        for k in chunk:
            nid += 1
            iid = f"J{nid:05d}"
            x = ans[k]
            lines.append(json.dumps({"item_id": iid, "lang": x["lang"], "question": qm[k], "answer": x["answer"]}, ensure_ascii=False))
            assert len(lines[-1]) < 1900, (iid, len(lines[-1]))      # Read 도구가 긴 줄을 자르지 않게
            keyrows.append({"item_id": iid, "system": k[0], "qid": k[1], "batch": b, "answer_sha1": sha1(x["answer"]), "reason": want[k]})
        files[b] = lines
        man.append({"batch": b, "n": len(chunk)})
    summary = {"pool_total": len(want), "already_keyed": len(old), "new_items": len(new), "new_batches": nbatch,
               "by_reason": {}, "by_system_new": {}}
    for k in new:
        summary["by_reason"][want[k]] = summary["by_reason"].get(want[k], 0) + 1
        summary["by_system_new"][k[0]] = summary["by_system_new"].get(k[0], 0) + 1
    if not a.dry:
        IN_DIR.mkdir(exist_ok=True)
        for b, lines in files.items():
            (IN_DIR / f"{b}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        with open(KEY, "a", encoding="utf-8", newline="\n") as f:
            for r in keyrows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        MAN.write_text(json.dumps(man, ensure_ascii=False, indent=0), encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
