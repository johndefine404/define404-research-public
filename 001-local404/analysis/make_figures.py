"""원고용 쉬운 그림(그림 1~5)을 만든다.

  python analysis/make_figures.py      # analysis/out_final/ 를 읽어 report/figures/*.svg 를 쓴다

숫자는 전부 out_final 의 결과 파일에서 읽는다. 그림 안에 손으로 적은 숫자는 없다.
색은 define404.com 디자인 토큰(site.css)과 같다.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "out_final"
FIG = ROOT / "report" / "figures"

INK, INK2, INK3 = "#141414", "#4A4844", "#6E6A63"
LINE1, LINE2 = "#D6D1C7", "#B9B3A7"
SUNK, RAISED = "#EDEAE3", "#FBFAF7"
BLUE, RED = "#0A6797", "#DA2D2D"
FONT = "'Wanted Sans Variable', 'Wanted Sans', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"
W = 360
CLAUDE = ["S-search", "H-search", "H-mem"]


def load():
    rows = {}
    with open(OUT / "exploratory_summary.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[(r["system"], r["scope"], r["value"])] = r
    return rows


def i(r, k):
    return int(float(r[k]))


def fmt(n):
    return f"{n:,}"


def text(x, y, s, size=15, weight=500, fill=INK, anchor="start"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def width(s, size):
    w = 0
    for ch in s:
        if "\uac00" <= ch <= "\ud7a3":
            w += size * 0.88
        elif ch == " ":
            w += size * 0.28
        elif ch.isascii() and ch.isalnum():
            w += size * 0.58
        else:
            w += size * 0.4
    return w


def wrap(s, size, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if cur and width(t, size) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = t
    return lines + [cur]


def para(x, y, s, size=14, weight=500, fill=INK, maxw=None, lh=None):
    """줄을 나눠 쓴다. (요소들, 다음 줄 y)"""
    maxw = maxw or (W - x - 16)
    lh = lh or round(size * 1.45)
    out = []
    for n, line in enumerate(wrap(s, size, maxw)):
        out.append(text(x, y + n * lh, line, size, weight, fill))
    return out, y + len(out) * lh


def svg(fid, h, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" role="img" '
            f'aria-labelledby="{fid}-t {fid}-d" font-family="{FONT}">\n'
            f'<title id="{fid}-t">{title}</title>\n<desc id="{fid}-d">{desc}</desc>\n'
            f'<rect width="{W}" height="{h}" fill="{RAISED}"/>\n' + "\n".join(body) + "\n</svg>\n")


def fig1(d):
    """조사 흐름 5단계."""
    total = sum(i(d[(s, "all", "all")], "n") for s in CLAUDE) + i(d[("L-mem", "all", "all")], "n")
    steps = [
        ("음식점 800곳을 뽑았어요", "공공 인허가 자료에서 영업 중 400곳, 폐업 400곳"),
        ("가게마다 똑같이 물었어요", "\"지금도 영업해요? 주소와 업종은요?\" 한국어, 영어, 일본어, 중국어, 베트남어로"),
        ("AI 네 가지가 답했어요", "Claude Haiku(기억만, 웹 검색), Claude Sonnet(웹 검색), Llama 3.1 8B(기억만)"),
        ("답을 세 갈래로 나눴어요", "영업 중이래요, 폐업했대요, 모른대요"),
        ("정답과 맞춰 봤어요", f"답 {fmt(total)}개를 인허가 자료의 실제 영업 상태와 비교했어요"),
    ]
    body, y = [], 26
    for k, (head, sub) in enumerate(steps, 1):
        body.append(f'<circle cx="28" cy="{y + 10}" r="12" fill="{BLUE}"/>')
        body.append(text(28, y + 15, str(k), 13, 700, "#FFFFFF", "middle"))
        body.append(text(52, y + 16, head, 16, 700))
        lines, ny = para(52, y + 38, sub, 13.5, 500, INK2)
        body += lines
        if k < len(steps):
            body.append(f'<line x1="28" y1="{y + 26}" x2="28" y2="{ny + 2}" stroke="{LINE2}" stroke-width="1.5"/>')
        y = ny + 10
    return svg("f1", y + 2, "그림 1. 이렇게 조사했어요",
               "음식점 800곳을 뽑아 5개 언어로 묻고, AI 네 가지의 답을 영업, 폐업, 모름으로 나눠 실제 영업 상태와 맞춰 본 순서", body)


def waffle(x0, y0, cells, size=14, gap=2):
    out = []
    for n, kind in enumerate(cells):
        cx, cy = x0 + (n % 10) * (size + gap), y0 + (n // 10) * (size + gap)
        if kind == "unres":
            out.append(f'<rect x="{cx + .75}" y="{cy + .75}" width="{size - 1.5}" height="{size - 1.5}" rx="2" fill="{RAISED}" stroke="{LINE2}" stroke-width="1.5"/>')
        else:
            fill = {"open": BLUE, "closed": INK, "unknown": LINE1}[kind]
            out.append(f'<rect x="{cx}" y="{cy}" width="{size}" height="{size}" rx="2" fill="{fill}"/>')
    return out


def per100(parts):
    """합이 100이 되게 큰 나머지 순으로 반올림한다."""
    tot = sum(v for _, v in parts)
    raw = [(k, v * 100 / tot) for k, v in parts]
    base = {k: int(r) for k, r in raw}
    left = 100 - sum(base.values())
    for k, r in sorted(raw, key=lambda t: t[1] - int(t[1]), reverse=True)[:left]:
        base[k] += 1
    return base


def fig2(d):
    """100번 물으면: Claude 계열과 Llama의 답 분포."""
    c = {k: sum(i(d[(s, "all", "all")], k) for s in CLAUDE) for k in ("n", "open", "closed", "unknown", "review")}
    l = d[("L-mem", "all", "all")]
    order = ["open", "closed", "unknown", "review"]
    lp = per100([(k, i(l, k)) for k in order])
    cp = per100([(k, c[k]) for k in order])
    cells_c = sum(([("unres" if k == "review" else k)] * cp[k] for k in order), [])
    cells_l = sum(([("unres" if k == "review" else k)] * lp[k] for k in order), [])
    L, R, cw = 16, 192, 156
    body = [text(L, 28, "Claude 계열 세 조건", 15, 700), text(R, 28, "Llama 3.1 8B", 15, 700),
            text(L, 46, f"답 {fmt(c['n'])}개를 100개로", 12, 500, INK3), text(R, 46, f"답 {fmt(i(l, 'n'))}개를 100개로", 12, 500, INK3)]
    body += waffle(L, 60, cells_c) + waffle(R, 60, cells_l)
    y = 60 + 160 + 16
    a, ya = para(L, y, f"{cp['unknown']}개 모두 \"확인할 수 없어요\"", 13.5, 650, INK, cw)
    b, yb = para(R, y, f"{lp['open'] + lp['closed']}개는 딱 잘라 말했어요", 13.5, 650, INK, cw)
    a2, ya = para(L, ya, f"단정한 답은 {fmt(c['n'])}개 중 {c['open'] + c['closed']}개", 12, 500, INK2, cw)
    b2, yb = para(R, yb, f"영업 중 {lp['open']}개, 폐업 {lp['closed']}개", 12, 500, INK2, cw)
    body += a + b + a2 + b2
    ly = max(ya, yb) + 18
    legend = [("open", "영업 중이래요"), ("closed", "폐업했대요"), ("unknown", "모른대요"), ("unres", "분류 못 함")]
    for n, (k, lab) in enumerate(legend):
        lx = (L, R)[n % 2]
        yy = ly + (n // 2) * 22
        body += waffle(lx, yy - 11, [k], size=12)
        body.append(text(lx + 19, yy, lab, 12.5, 500, INK2))
    return svg("f2", ly + 36, "그림 2. AI에게 100번 물으면",
               f"Claude 계열은 100개 모두 확인할 수 없다고 답했고, Llama는 100개 중 영업 중 {lp['open']}개, 폐업 {lp['closed']}개, 모름 {lp['unknown']}개, 분류 못 함 {lp['review']}개", body)


def bar_rows(rows, scale, y0):
    """rows: (제목, [(값, 색, 아래 글)])"""
    body, y = [], y0
    for head, segs in rows:
        lines, y = para(16, y, head, 14, 700)
        x = 16
        for v, col, lab in segs:
            w = v * scale
            body.append(f'<rect x="{x:.1f}" y="{y - 6}" width="{w:.1f}" height="30" fill="{col}"/>')
            if w >= 40:
                body.append(text(x + 7, y + 14, f"{v}번", 13, 700, "#FFFFFF"))
            if lab:
                body.append(text(x + 1, y + 44, lab, 12, 500, INK2))
            x += w + 2
        body += lines
        y += 70
    return body, y


def fig3(d):
    """Llama가 단정한 답의 맞음·틀림."""
    c, o = d[("L-mem", "truth", "closed")], d[("L-mem", "truth", "open")]
    co, cc, oo, oc = i(c, "open"), i(c, "closed"), i(o, "open"), i(o, "closed")
    right, wrong = cc + oo, co + oc
    rows = [
        (f"실제로는 폐업한 가게에 딱 잘라 말한 {co + cc}번", [(co, RED, "\"영업 중\" 틀림"), (cc, BLUE, "\"폐업\" 맞음")]),
        (f"실제로 영업 중인 가게에 딱 잘라 말한 {oo + oc}번", [(oo, BLUE, "\"영업 중\" 맞음"), (oc, RED, "\"폐업\" 틀림")]),
    ]
    body, y = bar_rows(rows, (W - 34) / max(co + cc, oo + oc), 30)
    body.append(f'<line x1="16" y1="{y - 6}" x2="{W - 16}" y2="{y - 6}" stroke="{LINE1}"/>')
    body.append(text(16, y + 18, f"맞음 {right}번, 틀림 {wrong}번", 15, 700))
    body.append(text(16, y + 38, "동전을 던져 고른 것과 비슷해요", 13, 500, INK2))
    return svg("f4", y + 54, "그림 4. Llama가 딱 잘라 말한 답",
               f"폐업한 가게에 단정한 {co + cc}번 중 {co}번이 영업 중이라는 오답, 영업 중인 가게에 단정한 {oo + oc}번 중 {oc}번이 폐업이라는 오답. 맞음 {right}번, 틀림 {wrong}번", body)


def fig4(d):
    """Claude가 주소를 말한 답: 영업 가게 대 폐업 가게."""
    def s(tr, k):
        return sum(i(d[(x, "truth", tr)], k) for x in CLAUDE)
    oa, oc = s("open", "address_asserted"), s("open", "address_correct_given_asserted")
    ca, cc = s("closed", "address_asserted"), s("closed", "address_correct_given_asserted")
    rows = [
        (f"영업 중인 가게: 주소를 말한 답 {oa}번", [(oc, BLUE, "맞는 주소"), (oa - oc, RED, "")]),
        (f"폐업한 가게: 주소를 말한 답 {ca}번", [(cc, BLUE, ""), (ca - cc, RED, "")]),
    ]
    body, y = bar_rows(rows, (W - 34) / oa, 30)
    body.append(text(16, y - 26, "빨간 칸은 틀린 주소예요", 12, 500, INK3))
    body.append(f'<line x1="16" y1="{y - 8}" x2="{W - 16}" y2="{y - 8}" stroke="{LINE1}"/>')
    body.append(text(16, y + 16, f"주소를 말한 {oa + ca}번 중 {oc + cc}번이 맞았어요", 15, 700))
    body.append(text(16, y + 36, "AI는 아는 가게만 주소를 말했어요", 13, 500, INK2))
    return svg("f3", y + 52, "그림 3. Claude가 주소를 말한 답",
               f"Claude 계열 세 조건에서 주소를 말한 답은 영업 중인 가게 {oa}번(맞음 {oc}), 폐업한 가게 {ca}번(맞음 {cc})", body)


def fig5(d):
    """두 가지 실패: 판단 유보와 틀린 단정."""
    cl = {tr: {k: sum(i(d[(s, "truth", tr)], k) for s in CLAUDE) for k in ("n", "open", "closed")} for tr in ("open", "closed")}
    lc = d[("L-mem", "truth", "closed")]
    cards = [
        ("Claude 계열", "\"확인할 수 없어요\"", INK3, [
            (BLUE, f"폐업한 가게를 영업 중이라고 한 답: {fmt(cl['closed']['n'])}번 중 {cl['closed']['open']}번"),
            (BLUE, "손님이 헛걸음할 일은 거의 없어요"),
            (RED, f"영업 중인 가게를 영업 중이라고 한 답: {fmt(cl['open']['n'])}번 중 {cl['open']['open']}번"),
            (RED, "문을 연 가게도 AI 답에는 나오지 않아요"),
        ]),
        ("Llama 3.1 8B", "\"영업 중이에요\"", RED, [
            (RED, f"폐업한 가게에 딱 잘라 말한 {i(lc, 'open') + i(lc, 'closed')}번 중 {i(lc, 'open')}번이 \"영업 중\""),
            (RED, "그 말을 믿은 손님은 헛걸음을 해요"),
        ]),
    ]
    body, y = [], 14
    for name, quote, qcol, items in cards:
        inner, yy = [], y + 64
        for col, s_ in items:
            inner.append(f'<rect x="26" y="{yy - 9}" width="7" height="7" rx="1" fill="{col}"/>')
            lines, yy = para(40, yy, s_, 13, 500, INK2, W - 40 - 26)
            inner += lines
            yy += 4
        h = yy - y - 2
        body.append(f'<rect x="10.5" y="{y + .5}" width="{W - 21}" height="{h}" rx="2" fill="#FFFFFF" stroke="{LINE1}"/>')
        body.append(text(26, y + 26, name, 14, 700))
        body.append(text(W - 26, y + 26, quote, 14, 700, qcol, "end"))
        body.append(f'<line x1="26" y1="{y + 40}" x2="{W - 26}" y2="{y + 40}" stroke="{LINE1}"/>')
        body += inner
        y += h + 12
    lines, y = para(16, y + 8, "파란 점은 가게와 손님에게 좋은 점, 빨간 점은 문제예요", 12, 500, INK3)
    body += lines
    return svg("f5", y + 6, "그림 5. 판단을 미루는 AI와 틀리게 단정하는 AI",
               "Claude 계열은 폐업 가게를 영업 중이라고 하지 않았지만 영업 중인 가게도 거의 알려 주지 않았고, Llama는 폐업 가게에 단정한 답의 대부분이 영업 중이라는 오답", body)


def main():
    d = load()
    FIG.mkdir(parents=True, exist_ok=True)
    figs = {"fig1-flow.svg": fig1, "fig2-100-answers.svg": fig2, "fig3-claude-address.svg": fig4,
            "fig4-llama-right-wrong.svg": fig3, "fig5-two-failures.svg": fig5}
    for name, fn in figs.items():
        (FIG / name).write_text(fn(d), encoding="utf-8")
        print("wrote", FIG / name)


if __name__ == "__main__":
    main()
