"""발행 전 점검: 원고(md)·사이트 본문(html)의 숫자를 결과 파일과 대조하고 금지 표기·문체를 검사한다.

  python analysis/check_numbers.py [사이트 html 경로]

대조 원천: analysis/out/results.json(v1.1), analysis/out_v10/results.json(v1.0), judge/audit_result.json, sampling/sample_log.txt.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "report" / "permits_ko.md"
r11 = json.load(open(ROOT / "analysis/out/results.json", encoding="utf-8"))
r10 = json.load(open(ROOT / "analysis/out_v10/results.json", encoding="utf-8"))
aud = json.load(open(ROOT / "judge/audit_result.json", encoding="utf-8"))


def p(x):
    return f"{x * 100:.1f}"


def cell(c):
    return f"{c['k']} ({p(c['p'])}%; {p(c['lo'])}~{p(c['hi'])})"


expect = []
for tag, r in (("v1.1", r11), ("v1.0", r10)):
    a = r["preregistered"]["cells"]["all"]
    for k in ("period_loose", "period_strict", "period_wrong", "period_unknown", "fee_loose", "fee_strict",
              "fee_wrong", "fee_unknown", "both_loose", "both_strict"):
        expect.append((f"{tag} {k}", cell(a[k])))
    for h in ("H1", "H2"):
        v = r["preregistered"][h]
        expect.append((f"{tag} {h}", f"{v['diff'] * 100:+.1f} ({p(v['lo'])}~{p(v['hi'])})".replace("+-", "-").replace("-0.0 ", "-0.0 ") if v['diff'] < 0 or v['diff'] > 0 else f"+0.0 ({p(v['lo'])}~{p(v['hi'])})"))
        expect.append((f"{tag} {h} p", f"{v['p_one_sided']:.3f}"))
C = r11["preregistered"]["cells"]
for k in ("free", "paid"):
    for m in ("period_loose", "fee_loose", "both_strict"):
        expect.append((f"표4 {k} {m}", cell(C[k][m])))
for k in ("short", "long"):
    v = C[k]["period_loose"]
    expect.append((f"H2 {k}", f"{p(v['p'])}%({p(v['lo'])}~{p(v['hi'])})"))
e = r11["exploratory"]
g = e["given_claim"]
expect.append(("숫자 말한 처리기간", f"{g['period']['n']}건 중 {g['period']['k']}건, {p(g['period']['p'])}%({p(g['period']['lo'])}~{p(g['period']['hi'])})"))
expect.append(("숫자 말한 수수료", f"{g['fee']['n']}건 중에서는 {g['fee']['k']}건, {p(g['fee']['p'])}%({p(g['fee']['lo'])}~{p(g['fee']['hi'])})"))
for k in ("period", "fee"):
    v = e[f"loose_minus_strict_{k}"]
    expect.append((f"짝 차이 {k}", f"{p(v['diff'])}%p({p(v['lo'])}~{p(v['hi'])})"))
expect.append(("틀린 방향", f"주장값이 하나인 {e['period_wrong_direction']['n_single_wrong']}건은 모두 안내표보다 길게"))
assert e["period_wrong_direction"]["shorter"] == 0
fk = e["fee_wrong_kind"]
expect.append(("수수료 틀림 종류", f"수수료가 틀린 {fk['n_wrong']}건 가운데 {fk['free_said_paid']}건은 무료 민원에 금액"))
assert fk["paid_said_free"] == 0
assert e["hedged"]["rate"]["k"] == r11["n_used"] == 200
expect.append(("검수", f"30건 중 {aud['dev_v10_answers_with_error']}건에서 등록 규칙"))
expect.append(("검증", f"30건 중 {aud['answers_with_extraction_error']}건에 추출 차이가 남았고, 판정 {aud['verdict_cells']}칸(처리기간·수수료) 가운데 {aud['verdict_cells_changed']}칸"))
gv = r10["exploratory"]["given_claim"]
expect.append(("v1.0 숫자", f"처리기간 {gv['period']['n']}건 중 {gv['period']['k']}건({p(gv['period']['p'])}%), 수수료 {gv['fee']['n']}건 중 {gv['fee']['k']}건({p(gv['fee']['p'])}%)"))
bc = e["by_city"]
expect.append(("강서구", f"강서구(n={bc['서울특별시 강서구']['period_loose']['n']})가 처리기간 {bc['서울특별시 강서구']['period_loose']['k']}건, 수수료 {bc['서울특별시 강서구']['fee_loose']['k']}건"))
expect.append(("김천시", f"김천시(n={bc['경상북도 김천시']['period_loose']['n']})가 처리기간 {bc['경상북도 김천시']['period_loose']['k']}건, 수수료 {bc['경상북도 김천시']['fee_loose']['k']}건"))


def check(path, label):
    t = Path(path).read_text(encoding="utf-8")
    t_plain = re.sub(r"<[^>]+>", "", t)
    bad = [(d, s) for d, s in expect if s not in t and s not in t_plain]
    print(f"[{label}] 숫자 대조 {len(expect) - len(bad)}/{len(expect)} 일치")
    for d, s in bad:
        print("  없음:", d, "|", s)
    body = t_plain if path.suffix == ".html" else t
    banned = re.findall(r"—|§|\*\*|`", body)
    print(f"[{label}] 금지 표기 {len(banned)}건")
    ends = [ln for ln in re.split(r"(?<=[.!?])\s+|\n", body) if re.search(r"다\.$", ln.strip())]
    print(f"[{label}] '~다.' 문장 끝 {len(ends)}건")
    for x in ends[:10]:
        print("   ", x.strip()[:80])
    return not bad and not banned and not ends


ok = check(MD, "md")
if len(sys.argv) > 1:
    ok = check(Path(sys.argv[1]), "html") and ok
sys.exit(0 if ok else 1)
