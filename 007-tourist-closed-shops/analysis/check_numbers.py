#!/usr/bin/env python3
# [Define404] 7호 원고 숫자 대조: 결과 파일에서 기대 문자열을 만들어 원고(md)와 사이트 본문(html)에 있는지 본다.
# 사용: python3 analysis/check_numbers.py <원고.md 또는 .html>...
import json, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
A = json.load(open(R / "analysis/out/results.json"))
B = json.load(open(R / "analysis/out_v10/results.json"))
E = json.load(open(R / "analysis/out/explore.json"))
f1 = lambda x: f"{100 * x:.1f}"
exp = []
def cell(res, m, k):
    c = res[m][k]
    exp.append(f"{c['k']} ({f1(c['p'])}%; {f1(c['lo'])}~{f1(c['hi'])})")
for k in ("closed_ko", "closed_en", "closed_all", "unverified_ko", "unverified_en", "unverified_all"):
    cell(A, "loose", k); cell(B, "loose", k)
def hyp(res, m, h):
    c = res[m][h]
    exp.append(f"{100 * c['diff']:+.1f} ({100 * c['lo']:.1f}~{100 * c['hi']:.1f})".replace("-0.0)", "-0.0)"))
for h in ("H1", "H2", "H3"):
    hyp(A, "loose", h); hyp(B, "loose", h)
L = A["loose"]
for k in ("closed_all", "closed_ko", "closed_en", "unverified_ko", "unverified_en"):
    exp.append(f"{f1(L[k]['p'])}")
exp += [f"{L['H1']['p_one_sided']:.3f}", f"{L['holm']['H1']:.3f}", f"{L['H2']['p_one_sided']:.3f}",
        f"{L['H1']['pairs']}곳" if True else "", f"{L['H3']['pairs']}곳"]
S = A["strict"]
exp += [f"{S['closed_all']['n']}곳 중 {S['closed_all']['k']}곳({f1(S['closed_all']['p'])}%; {f1(S['closed_all']['lo'])}~{f1(S['closed_all']['hi'])})",
        f"{100*S['H1']['diff']:+.1f}%p({100*S['H1']['lo']:.1f}~{100*S['H1']['hi']:.1f})", f"{100*S['H3']['diff']:+.1f}%p({100*S['H3']['lo']:.1f}~{100*S['H3']['hi']:.1f})",
        f1(S['unverified_ko']['p']), f1(S['unverified_en']['p']), f1(S['closed_ko']['p']), f1(S['closed_en']['p'])]
for lg in ("ko", "en"):
    o = E[f"addr_outside_area_{lg}"]; exp.append(f"{o['n']}곳 중 {o['k']}곳({f1(o['k']/o['n'])}%)")
    exp.append(str(E[f"recs_per_answer_{lg}"]["full5"]))
exp += [f"{L['closed_do']['n']}곳 중 {L['closed_do']['k']}곳({f1(L['closed_do']['p'])}%; {f1(L['closed_do']['lo'])}~{f1(L['closed_do']['hi'])})",
        f"{L['closed_metro']['n']}곳 중 {L['closed_metro']['k']}곳({f1(L['closed_metro']['p'])}%; {f1(L['closed_metro']['lo'])}~{f1(L['closed_metro']['hi'])})"]
for p in sys.argv[1:]:
    t = open(p, encoding="utf-8").read().replace("&lt;", "<")
    miss = [e for e in exp if e and e not in t]
    print(p.split("/")[-1], "기대", len([e for e in exp if e]), "없음", len(miss), miss[:8])
