"""가짜 입력으로 run_analysis.py 를 끝까지 돌려 본다. 실제 1편 결과 파일은 읽지 않는다.

  python analysis/tests/test_fake_input.py
"""
import csv
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent / "run_analysis.py"
LANGS = ["ko", "en", "ja", "zh", "vi"]


def make_fake(path, seed=7, ko_bonus=0.25):
    """가게 800곳(H-mem·L-mem), 검색 2조건은 그중 100곳. 한국어 업종 언급 확률을 ko_bonus 만큼 높여 둔다."""
    rng = random.Random(seed)
    shops = []
    for i in range(800):
        shops.append({"item_id": f"L{i:04d}", "truth": rng.choice(["open", "closed"]),
                      "kakao": rng.choice(["registered", "unregistered"]), "region": rng.choice(["metro", "province"]),
                      "etc": rng.random() < 0.1})       # 정답이 기타인 가게 -> type na
    sub = set(s["item_id"] for s in rng.sample(shops, 100))
    cols = ["system", "qid", "item_id", "lang", "status", "status_reason", "address", "type", "judge_source",
            "correct_lenient", "correct_strict", "truth", "kakao", "region", "days_since_close", "resolved", "mode"]
    rows = []
    for sy in ["H-mem", "H-search", "S-search", "L-mem"]:
        for s in shops:
            if sy in ("H-search", "S-search") and s["item_id"] not in sub:
                continue
            for lg in LANGS:
                if sy == "L-mem" and lg in ("zh", "vi"):
                    continue
                base = 0.2 + (0.1 if s["kakao"] == "registered" else 0)
                p = base + (ko_bonus if lg == "ko" else 0)
                if s["etc"]:
                    typ = "na"
                elif rng.random() < p:
                    typ = "match" if rng.random() < 0.8 else "wrong"
                else:
                    typ = "none" if rng.random() < 0.97 else "review"
                addr = "none" if rng.random() < 0.95 else ("match" if rng.random() < 0.9 else "wrong")
                if sy == "L-mem":
                    st = rng.choice(["open", "closed", "unknown", "unknown", "review"])
                else:
                    st = "unknown"
                rows.append({"system": sy, "qid": f'{s["item_id"]}-{lg}', "item_id": s["item_id"], "lang": lg,
                             "status": st, "status_reason": "", "address": addr, "type": typ, "judge_source": "dict",
                             "correct_lenient": "", "correct_strict": "", "truth": s["truth"], "kakao": s["kakao"],
                             "region": s["region"], "days_since_close": "", "resolved": str(st != "review"), "mode": "fake"})
    with open(path, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader(); wr.writerows(rows)
    return len(rows)


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        n = make_fake(td / "judgments.csv")
        out = td / "out"
        r = subprocess.run([sys.executable, str(RUN), "--judgments", str(td / "judgments.csv"), "--out", str(out)],
                           capture_output=True, text=True)
        print(r.stdout.strip()); print(r.stderr.strip())
        assert r.returncode == 0, "run_analysis failed"
        for f in ["h1.csv", "h2.csv", "h3.csv", "holm.csv", "explore_pairs.csv", "explore_inconsistency.csv",
                  "explore_correctness.csv", "explore_address.csv", "explore_lmem_status.csv", "data_inventory.csv", "results.json"]:
            assert (out / f).exists(), f
        res = json.loads((out / "results.json").read_text(encoding="utf-8"))
        h1 = res["confirmatory"]["H1"]
        assert h1["n_shops"] > 600 and h1["diff"] > 0.1, h1              # 심어 둔 한국어 가산이 복원돼야 한다
        assert h1["ci_lo"] > 0, h1
        h3 = res["confirmatory"]["H3"]
        assert h3["n_registered"] + h3["n_unregistered"] == h1["n_shops"], h3
        holm = res["confirmatory"]["holm"]
        assert len(holm) == 4 and all(r["in_family"] for r in holm), holm
        assert all(r["holm_p_two"] >= r["p_two"] for r in holm), holm
        print(f"fake rows {n}; H1 diff {h1['diff']:.3f} ({h1['ci_lo']:.3f}~{h1['ci_hi']:.3f}), n {h1['n_shops']}; "
              f"H3 diff {h3['diff']:.3f}; holm ok")
        # 효과 없음 입력: 차이가 0 근처여야 한다
        make_fake(td / "j0.csv", seed=11, ko_bonus=0.0)
        r0 = subprocess.run([sys.executable, str(RUN), "--judgments", str(td / "j0.csv"), "--out", str(td / "out0")],
                            capture_output=True, text=True)
        assert r0.returncode == 0, r0.stderr
        h1z = json.loads((td / "out0" / "results.json").read_text(encoding="utf-8"))["confirmatory"]["H1"]
        assert abs(h1z["diff"]) < 0.06, h1z
        print(f"null input: H1 diff {h1z['diff']:.3f}, p_two {h1z['p_two']:.3f}")
    print("OK")


if __name__ == "__main__":
    main()
