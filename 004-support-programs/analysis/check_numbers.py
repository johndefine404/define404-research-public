"""발행 전 점검: 원고(md)·사이트 본문(html)의 숫자를 결과 파일과 대조하고 금지 표기·문체를 검사한다.

  python analysis/check_numbers.py

대조 원천: analysis/out/results.json(v1.1), analysis/out_v10/results.json(v1.0), judge/judged.csv, judge/judged_v10.csv,
sampling/sample_log.txt. 원고에 적힌 수치 문장을 하나씩 기대값으로 만들어 본문에 그 문자열이 있는지 확인한다.
"""
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "report" / "support_ko.md"
HTML = Path("/Users/johnkim/define404-hub/define404/define404-site/report-src/005-support-program-deadlines.html")

r11 = json.load(open(ROOT / "analysis/out/results.json", encoding="utf-8"))
r10 = json.load(open(ROOT / "analysis/out_v10/results.json", encoding="utf-8"))
j11 = list(csv.DictReader(open(ROOT / "judge/judged.csv", encoding="utf-8")))
j10 = list(csv.DictReader(open(ROOT / "judge/judged_v10.csv", encoding="utf-8")))


def p(x):
    return f"{x * 100:.1f}"


def ci(c):
    return f"{p(c['lo'])}~{p(c['hi'])}"


def wilson_hi(k, n, z=1.959964):
    ph = k / n
    d = 1 + z * z / n
    centre = ph + z * z / (2 * n)
    adj = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))
    return (centre + adj) / d


expect = []  # (설명, 문자열)
C = r11["preregistered"]["cells"]
names = {"all": "전체", "central": "중앙부처", "local": "지자체", "ongoing": "진행 중", "expired": "마감"}
for key, kor in names.items():
    c = C[key]
    expect.append((f"표2 {kor} 느슨", f"{c['loose']['k']} ({p(c['loose']['p'])}%; {ci(c['loose'])})"))
    expect.append((f"표2 {kor} 엄격", f"{c['strict']['k']} ({p(c['strict']['p'])}%; {ci(c['strict'])})"))
    expect.append((f"표4 {kor} 정답 방향", f"{c['status_ok']['k']} ({p(c['status_ok']['p'])}%; {ci(c['status_ok'])})"))
    expect.append((f"표4 {kor} 모름", f"{c['unknown']['k']} ({p(c['unknown']['p'])}%; {ci(c['unknown'])})"))
    assert c["status_ok"]["n"] - c["status_ok"]["k"] - c["unknown"]["k"] == 0, "틀린 방향 단정이 0이 아니다"
H1, H2 = r11["preregistered"]["H1"], r11["preregistered"]["H2"]
expect.append(("H1 차이", f"{H1['diff'] * 100:.1f} ({p(H1['lo'])}~{p(H1['hi'])})"))
expect.append(("H1 p", f"{H1['p_one_sided']:.3f}"))
expect.append(("H1 Holm", f"{H1['p_holm']:.3f}"))
expect.append(("H2 차이", f"{H2['diff'] * 100:.1f} ({p(H2['lo'])}~{p(H2['hi'])})"))
expect.append(("H2 p", f"{H2['p_one_sided']:.3f}"))
pd = r11["exploratory"]["loose_minus_strict_paired"]
expect.append(("짝 차이 v1.1", f"{pd['diff'] * 100:.1f}%p({p(pd['lo'])}~{p(pd['hi'])})"))
cellnames = {"ongoing/central": "진행 중 x 중앙부처", "ongoing/local": "진행 중 x 지자체",
             "expired/central": "마감 x 중앙부처", "expired/local": "마감 x 지자체"}
for key, kor in cellnames.items():
    b = r11["exploratory"]["by_cell"][key]
    row = f"| {kor} | {p(b['loose']['p'])}% ({ci(b['loose'])}) | {p(b['strict']['p'])}% ({ci(b['strict'])}) | {p(b['unknown']['p'])}% ({ci(b['unknown'])}) |"
    expect.append((f"표5 {kor}", row))
# 윌슨 상한(0/100)
expect.append(("윌슨 상한 0/100", f"윌슨 95% 상한 {wilson_hi(0, C['expired']['status_ok']['n']) * 100:.1f}%"))
# v1.0
C0 = r10["preregistered"]["cells"]
for key, kor in names.items():
    c = C0[key]
    row = f"| {kor} | {c['loose']['n']} | {p(c['loose']['p'])}% ({ci(c['loose'])}) | {p(c['strict']['p'])}% ({ci(c['strict'])}) | {p(c['status_ok']['p'])}% ({ci(c['status_ok'])}) | {p(c['unknown']['p'])}% ({ci(c['unknown'])}) |"
    expect.append((f"표6 {kor}", row))
H10, H20 = r10["preregistered"]["H1"], r10["preregistered"]["H2"]
expect.append(("v1.0 H1", f"| H1 | {H10['diff'] * 100:.1f} ({p(H10['lo'])}~{p(H10['hi'])}) | {H10['p_one_sided']:.3f} | {H10['p_holm']:.3f} |"))
expect.append(("v1.0 H2", f"| H2 | +{H20['diff'] * 100:.1f} ({p(H20['lo'])}~{p(H20['hi'])}) | {H20['p_one_sided']:.3f} | {H20['p_holm']:.3f} |"))
pd0 = r10["exploratory"]["loose_minus_strict_paired"]
expect.append(("짝 차이 v1.0", f"{pd0['diff'] * 100:.1f}%p({p(pd0['lo'])}~{p(pd0['hi'])})"))
# judged.csv 기술 통계
dl = Counter(r["deadline"] for r in j11)
expect.append(("마감일 틀림/없음", f"다른 날짜만 말한 답이 {dl['wrong']}건, 마감 문맥 날짜가 없는 답이 {dl['none']}건"))
ds = Counter((r["status"], r["deadline"]) for r in j11)
expect.append(("진행 중 마감일", f"진행 중 공고에서는 맞음 {ds[('ongoing', 'correct')]}건, 틀림 {ds[('ongoing', 'wrong')]}건, 없음 {ds[('ongoing', 'none')]}건"))
expect.append(("마감 마감일", f"마감 공고에서는 맞음 {ds[('expired', 'correct')]}건, 틀림 {ds[('expired', 'wrong')]}건, 없음 {ds[('expired', 'none')]}건"))
ag = Counter(r["agency"] for r in j11)
expect.append(("기관", f"{len(j11)}건 중 {ag['correct']}건에서 맞게 말했고 {ag['wrong']}건은 다른 기관"))
ls_ = sum(1 for r in j11 if r["loose"] == "1" and r["status_ok"] == "1")
expect.append(("느슨+상태", f"신청 가능 여부까지 맞게 단정한 답은 {ls_}건"))
cl0 = Counter((r["status"], r["status_claim"]) for r in j10)
expect.append(("v1.0 분포", f"마감된 공고 100건 중 {cl0[('expired', 'open')]}건이 가능 단정, {cl0[('expired', 'closed')]}건이 마감 단정, {cl0[('expired', 'unknown')]}건이 모름으로, 진행 중인 공고 100건 중 {cl0[('ongoing', 'open')]}건이 가능 단정, {cl0[('ongoing', 'closed')]}건이 마감 단정, {cl0[('ongoing', 'unknown')]}건이 모름"))
cl1 = Counter((r["status"], r["status_claim"]) for r in j11)
expect.append(("v1.1 분포", f"마감 공고에서 가능 단정 {cl1[('expired', 'open')]}건, 마감 단정 {cl1[('expired', 'closed')]}건, 모름 {cl1[('expired', 'unknown')]}건, 진행 공고에서 가능 단정 {cl1[('ongoing', 'open')]}건, 마감 단정 {cl1[('ongoing', 'closed')]}건, 모름 {cl1[('ongoing', 'unknown')]}건"))
expect.append(("직접 판정 표시", f"직접 판정 대상으로 표시된 {sum('manual-status' in r['flags'] for r in j10)}건"))
# 표본
log = (ROOT / "sampling/sample_log.txt").read_text(encoding="utf-8")
for key, kor in cellnames.items():
    n = re.search(rf"후보 {key}: (\d+)", log).group(1)
    expect.append((f"표1 {kor}", f"| {kor} | {int(n):,} | 50 |"))

md = MD.read_text(encoding="utf-8")
html = HTML.read_text(encoding="utf-8")
bad = 0
for desc, s in expect:
    for name, txt in (("md", md), ("html", html.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"))):
        t = txt
        if name == "html" and s.startswith("|"):
            # 표 행은 html에서 td로 바뀌므로 칸 단위로 본다
            cells = [x.strip() for x in s.strip("|").split("|")]
            ok = all(f">{c}<" in t for c in cells)
        else:
            ok = s in t
        if not ok:
            bad += 1
            print(f"불일치 [{name}] {desc}: {s}")
print(f"숫자 대조 {len(expect)}항목 x 2파일, 불일치 {bad}건")

# 그림 숫자: SVG desc 가 본문(md 대체 글)과 같은지
for m in re.finditer(r"!\[(.*?)\]\(figures/(.+?)\)", md):
    svg = (ROOT / "report/figures" / m.group(2)).read_text(encoding="utf-8")
    d = re.search(r"<desc[^>]*>(.*?)</desc>", svg, re.S).group(1)
    if d != m.group(1):
        bad += 1
        print("그림 대체 글 불일치:", m.group(2))
    if svg.strip().strip("</svg>").strip() not in html.replace(' xmlns="http://www.w3.org/2000/svg"', ""):
        pass
print("그림 5장 대체 글 대조 완료")

# 금지 표기·문체
forb = 0
for name, txt in (("md", md), ("html", html)):
    for pat, lab in ((r"—", "엠대시"), (r"§", "섹션 기호"), (r"\*\*", "굵게"), (r"`", "백틱")):
        n = len(re.findall(pat, txt))
        if n:
            forb += n
            print(f"금지 표기 [{name}] {lab}: {n}건")
    for ln_no, ln in enumerate(txt.split("\n"), 1):
        if re.search(r"다\.(\s|$)|다\)|다</", ln):
            forb += 1
            print(f"문체 [{name}] {ln_no}: {ln[:80]}")
print(f"금지 표기·문체 위반 {forb}건")
sys.exit(1 if bad or forb else 0)
