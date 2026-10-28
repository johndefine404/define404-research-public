"""규칙 자동 판정 (judge/rules.md v1.0). 입력 collect/raw/<시스템>/*.jsonl ({qid, answer, sources, searches}),
정답 sampling/sample_v1.csv. 출력 judge/judged.csv (문항마다 한 줄), judge/manual_todo.csv (추출 실패분, 허브 직접 판정 대상).
직접 판정 결과는 judge/manual.csv (qid, candidate)로 두면 다음 실행에서 읽어 쓴다. 표준 라이브러리만 쓴다."""
import csv, json, re, unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
SAMPLE = ROOT / "sampling" / "sample_v1.csv"
RAW = ROOT / "collect" / "raw"

VARIANTS = [(r"\bgimchi\b", "kimchi"), (r"\b(ddeok|dduk|ddok|ttok)\b", "tteok"), (r"\b(chigae|jigae)\b", "jjigae"),
            (r"\bgook\b", "guk"), (r"\bbab\b", "bap"), (r"\btahng\b", "tang")]
STOP = {"a", "an", "the", "and", "with"}
INGREDIENTS = {"beef", "pork", "chicken", "duck", "mussel", "skate", "clam", "oyster", "squid", "octopus", "crab", "shrimp",
               "prawn", "anchovy", "mackerel", "pollack", "cod", "flounder", "eel", "abalone", "tofu", "egg", "potato",
               "sweet", "radish", "cabbage", "cucumber", "spinach", "mushroom", "bean", "seaweed", "kelp", "laver", "barley", "rice"}

def norm_en(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s.replace("-", " ").replace("/", " ").replace("&", " "))
    for pat, rep in VARIANTS:
        s = re.sub(pat, rep, s)
    return " ".join(w for w in s.split() if w not in STOP)

def norm_ja(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    return re.sub(r"[\s・ーッ]", "", s)

def extract(answer):
    """rules.md 2절. 반환 (candidate|None, flags)"""
    flags = []
    if not answer or not answer.strip():
        return None, ["empty"]
    m = re.search(r"name\s*[:：]\s*(.+)", answer, flags=re.I)
    if m:
        cand = m.group(1).strip()
    else:
        first = answer.strip().splitlines()[0].strip()
        if first and len(first) <= 20 and not re.search(r"[.!?。！？]$", first):
            cand = first
        elif first and len(first.split()) <= 8 and not re.search(r"[.!?。！？]$", first):
            cand = first
        else:
            return None, ["extract_fail"]
    cand = cand.strip(" \"'“”‘’「」『』*`")
    cand = re.sub(r"[.。]$", "", cand).strip()
    if re.search(r"\s(/|or|または|もしくは)\s|／", cand, flags=re.I):
        flags.append("multiple")
        cand = re.split(r"\s(/|or|または|もしくは)\s|／", cand, flags=re.I)[0].strip()
    return cand, flags

def judge_one(lang, cand, std, latin):
    if cand is None:
        return "no_answer"
    if lang == "en":
        c, s = norm_en(cand), norm_en(std)
        if c == s:
            return "strict"
        cw, sw = set(c.split()), set(s.split())
        jac = len(cw & sw) / len(cw | sw) if cw | sw else 0
        lat = norm_en(latin).replace(" ", "")
        if jac >= 0.5 or (lat and lat in c.replace(" ", "")):
            return "loose"
        return "mismatch"
    c, s = norm_ja(cand), norm_ja(std)
    if c == s:
        return "strict"
    bg = lambda x: {x[i:i + 2] for i in range(len(x) - 1)}
    a, b = bg(c), bg(s)
    dice = 2 * len(a & b) / (len(a) + len(b)) if (a or b) else 0
    if dice >= 0.5 or (s and s in c):
        return "loose"
    return "mismatch"

def ingredient_flag(cand, std):
    cw, sw = set(norm_en(cand).split()), set(norm_en(std).split())
    return int(bool(sw & INGREDIENTS) and not (sw & INGREDIENTS & cw) and bool(cw & INGREDIENTS))

def main():
    sample = {r["sid"]: r for r in csv.DictReader(SAMPLE.open(encoding="utf-8"))}
    manual = {}
    if (HERE / "manual.csv").exists():
        manual = {r["qid"]: r["candidate"] for r in csv.DictReader((HERE / "manual.csv").open(encoding="utf-8"))}
    out, todo = [], []
    for path in sorted(RAW.glob("*/*.jsonl")):
        system = path.parent.name
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            sid, lang = rec["qid"].rsplit("-", 1)
            row = sample[sid]
            cand, flags = extract(rec.get("answer", ""))
            if cand is None and "extract_fail" in flags:
                if rec["qid"] in manual:
                    cand, flags = manual[rec["qid"]], ["manual"]
                else:
                    todo.append({"qid": rec["qid"], "answer": rec.get("answer", "")})
            verdict = judge_one(lang, cand, row[lang], row["latin"])
            sources = rec.get("sources") or []
            out.append({"qid": rec["qid"], "system": system, "sid": sid, "lang": lang, "category": row["category"], "ko": row["ko"],
                        "standard": row[lang], "candidate": cand or "", "verdict": verdict, "flags": "|".join(flags),
                        "cites_hansik": int(any("hansik.or.kr" in u for u in sources)), "searches": rec.get("searches", 0),
                        "ingredient_mismatch": ingredient_flag(cand, row["en"]) if (lang == "en" and cand and verdict == "mismatch") else 0})
    fields = list(out[0].keys()) if out else ["qid"]
    with (HERE / "judged.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    with (HERE / "manual_todo.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "answer"]); w.writeheader(); w.writerows(todo)
    print(f"판정 {len(out)}문항, 추출 실패(직접 판정 대상) {len(todo)}문항 → judged.csv, manual_todo.csv")

if __name__ == "__main__":
    main()
