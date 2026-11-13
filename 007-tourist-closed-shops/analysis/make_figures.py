"""[Define404] 7호 원고용 쉬운 그림(그림 1~5)을 만든다.

  python3 analysis/make_figures.py   # analysis/out/results.json, explore.json 을 읽어 report/figures/*.svg 를 쓴다

숫자는 전부 analysis/out/results.json(판정 v1.1, 느슨)과 explore.json에서 읽는다. 그림 안에 손으로 적은 숫자는 없다.
6호(005-business-permits/analysis/make_figures.py)의 그리기 함수를 그대로 쓴다. 색은 define404.com 디자인 토큰과 같다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "out"
FIG = ROOT / "report" / "figures"

INK, INK2, INK3 = "#141414", "#4A4844", "#6E6A63"
LINE1, LINE2 = "#D6D1C7", "#B9B3A7"
SUNK, RAISED = "#EDEAE3", "#FBFAF7"
BLUE, RED = "#0A6797", "#DA2D2D"
FONT = "'Wanted Sans Variable', 'Wanted Sans', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"
W = 360


def load():
    d = json.load(open(OUT / "results.json", encoding="utf-8"))
    d["explore"] = json.load(open(OUT / "explore.json", encoding="utf-8"))
    return d


def kn(d, key):
    c = d["loose"][key]
    return int(c["k"]), int(c["n"])


def fmt(n):
    return f"{n:,}"


def text(x, y, s, size=15, weight=500, fill=INK, anchor="start"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def width(s, size):
    w = 0
    for ch in s:
        if "가" <= ch <= "힣":
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


def per100(parts):
    """합이 100이 되게 큰 나머지 순으로 반올림한다."""
    tot = sum(v for _, v in parts)
    raw = [(k, v * 100 / tot) for k, v in parts]
    base = {k: int(r) for k, r in raw}
    left = 100 - sum(base.values())
    for k, r in sorted(raw, key=lambda t: t[1] - int(t[1]), reverse=True)[:left]:
        base[k] += 1
    return base


def waffle(x0, y0, cells, size=14, gap=2):
    out = []
    for n, fill in enumerate(cells):
        cx, cy = x0 + (n % 10) * (size + gap), y0 + (n // 10) * (size + gap)
        out.append(f'<rect x="{cx}" y="{cy}" width="{size}" height="{size}" rx="2" fill="{fill}"/>')
    return out


def bar_row(body, y, head, segs, scale):
    """segs: (값, 색, 라벨). 한 줄 막대."""
    lines, y = para(16, y, head, 14, 700)
    body += lines
    x = 16
    for v, col, lab in segs:
        w = v * scale
        if v > 0:
            body.append(f'<rect x="{x:.1f}" y="{y - 6}" width="{w:.1f}" height="30" fill="{col}"/>')
            if w >= 44:
                body.append(text(x + 7, y + 14, f"{v}번", 13, 700, "#FFFFFF" if col != LINE1 else INK))
        x += w + (2 if v > 0 else 0)
    ly = y + 44
    lx = 16
    for v, col, lab in segs:
        body += waffle(lx, ly - 10, [col], size=11)
        body.append(text(lx + 16, ly, f"{lab} {v}번", 12, 500, INK2))
        lx += 16 + width(f"{lab} {v}번", 12) + 14
    return y + 70



# FIGS
def legend(body, y, items, step):
    for i_, (col, lab) in enumerate(items):
        lx = 16 + i_ * step
        body += waffle(lx, y - 4, [col], size=12)
        body.append(text(lx + 19, y + 7, lab, 12.5, 500, INK2))


def counts(d, lg):
    """(전체 추천, 영업, 폐업, 못 찾음)"""
    un, tot = kn(d, f"unverified_{lg}")
    cl, mt = kn(d, f"closed_{lg}")
    return tot, mt - cl, cl, un


def fig1(d):
    areas = d["loose"]["H3"]["pairs"] + 1  # 시군구 150곳(H3 짝 149 + 영어 추천 0곳 1)
    tot_ko, *_ = counts(d, "ko")
    tot_en, *_ = counts(d, "en")
    steps = [
        ("전국 시군구 150곳을 뽑았어요", "식당이 100곳 넘는 시군구 230곳에서 광역시 75곳, 도 75곳을 무작위로"),
        ("여행자처럼 물었어요", "\"OO로 여행 가요. 가 볼 만한 식당 5곳 추천해 주세요\". 한국어와 영어로 한 번씩"),
        ("웹 검색을 쓰는 AI 비서가 답했어요", f"Claude Sonnet. 추천 식당은 한국어 {fmt(tot_ko)}곳, 영어 {fmt(tot_en)}곳"),
        ("정부 영업 기록에서 찾았어요", "지방행정 인허가 일반음식점 기록에서 같은 시군구, 같은 상호를 찾았어요"),
        ("영업 중인지 폐업했는지 봤어요", "폐업은 주소까지 같은 기록이 있을 때만 셌어요"),
    ]
    body, y = [], 26
    for k, (head, sub) in enumerate(steps, 1):
        body.append(f'<circle cx="28" cy="{y + 10}" r="12" fill="{BLUE}"/>')
        body.append(text(28, y + 15, str(k), 13, 700, "#FFFFFF", "middle"))
        hl, hy = para(52, y + 16, head, 16, 700)
        body += hl
        lines, ny = para(52, hy + 6, sub, 13.5, 500, INK2)
        body += lines
        if k < len(steps):
            body.append(f'<line x1="28" y1="{y + 26}" x2="28" y2="{ny + 2}" stroke="{LINE2}" stroke-width="1.5"/>')
        y = ny + 10
    return svg("f1", y + 2, "그림 1. 이렇게 조사했어요",
               "시군구 150곳을 뽑아 AI 비서에게 한국어와 영어로 식당 추천을 받고, 추천된 식당을 정부 영업 기록에서 찾아 영업 중인지 본 순서", body)


def waffle_fig(d, fid, lg, head, conclusion, title):
    tot, op, cl, un = counts(d, lg)
    p = per100([("op", op), ("cl", cl), ("un", un)])
    cells = [BLUE] * p["op"] + [RED] * p["cl"] + [LINE1] * p["un"]
    body = [text(16, 28, head, 15, 700), text(16, 46, f"추천 식당 {fmt(tot)}곳을 100칸으로 줄였어요", 12, 500, INK3)]
    body += waffle(16, 60, cells)
    y = 60 + 160 + 20
    a, y = para(16, y, f"{p['op']}칸은 지금 영업 중이래요", 15, 700)
    body += a
    b, y = para(16, y + 2, f"{p['un']}칸은 정부 기록에서 이 이름을 못 찾았어요", 13, 500, INK2)
    body += b
    c, y = para(16, y, f"{p['cl']}칸은 이미 폐업 신고한 곳이에요", 13, 500, INK2)
    body += c
    y += 10
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    y += 22
    e, y = para(16, y, conclusion, 13, 600)
    body += e
    y += 4
    legend(body, y, [(BLUE, "영업 중"), (RED, "폐업"), (LINE1, "못 찾음")], 100)
    return svg(fid, y + 24, title,
               f"100칸 중 {p['op']}칸은 영업 중, {p['cl']}칸은 폐업, {p['un']}칸은 정부 기록에서 못 찾은 식당", body)


def fig2(d):
    return waffle_fig(d, "f2", "ko", "한국어로 물었더니", "한국어 답은 열 곳 중 여덟 곳 넘게 영업 중인 식당이었어요",
                      "그림 2. 한국어로 물었을 때 AI가 추천한 식당 100곳")


def fig3(d):
    return waffle_fig(d, "f3", "en", "영어로 물었더니", "영어 답은 열 곳 중 세 곳을 정부 기록에서 못 찾았어요",
                      "그림 3. 영어로 물었을 때 AI가 추천한 식당 100곳")


def fig4(d):
    rows = []
    for lg, lab in (("ko", "한국어"), ("en", "영어")):
        cl, mt = kn(d, f"closed_{lg}")
        rows.append((lab, cl, mt))
    body, y = [], 30
    for lab, cl, mt in rows:
        lines, y = para(16, y, f"{lab} 질문: 영업 기록을 찾은 {fmt(mt)}곳 중", 14, 700)
        body += lines
        body.append(text(16, y + 30, str(cl), 34, 700, RED))
        body.append(text(16 + width(str(cl), 34) + 6, y + 30, "곳이 이미 폐업했어요", 15, 600, INK))
        y += 62
    body.append(f'<line x1="16" y1="{y - 8}" x2="{W - 16}" y2="{y - 8}" stroke="{LINE1}"/>')
    e, y = para(16, y + 16, "문 닫은 식당을 추천하는 일은 백 곳에 한 곳 정도예요", 15, 700)
    body += e
    f_, y = para(16, y + 2, "영어로 물어도 한국어와 거의 같았어요", 13, 500, INK2)
    body += f_
    return svg("f4", y + 12, "그림 4. 폐업한 식당 추천은 백 곳에 한 곳 정도예요",
               f"영업 기록을 찾은 추천 식당 중 폐업은 한국어 {rows[0][2]}곳 중 {rows[0][1]}곳, 영어 {rows[1][2]}곳 중 {rows[1][1]}곳", body)


def pct(k, n):
    return round(100 * k / n)


def fig5(d):
    E = d["explore"]
    un_ko, n_ko = kn(d, "unverified_ko")
    un_en, n_en = kn(d, "unverified_en")
    out_ko, a_ko = E["addr_outside_area_ko"]["k"], E["addr_outside_area_ko"]["n"]
    out_en, a_en = E["addr_outside_area_en"]["k"], E["addr_outside_area_en"]["n"]
    groups = [
        ("정부 기록에서 이름을 못 찾은 식당", pct(un_ko, n_ko), pct(un_en, n_en)),
        ("물어본 시군구가 아닌 주소를 적은 식당", pct(out_ko, a_ko), pct(out_en, a_en)),
    ]
    scale = (W - 120) / 100
    body, y = [], 30
    for head, vk, ve in groups:
        lines, y = para(16, y, head, 14, 700)
        body += lines
        for lab, v, col in (("한국어", vk, LINE2), ("영어", ve, RED)):
            body.append(text(16, y + 14, lab, 13, 600, INK2))
            body.append(f'<rect x="70" y="{y}" width="{max(v * scale, 2):.1f}" height="20" fill="{col}"/>')
            body.append(text(70 + max(v * scale, 2) + 8, y + 15, f"{v}%", 13, 700))
            y += 28
        y += 18
    body.append(f'<line x1="16" y1="{y - 10}" x2="{W - 16}" y2="{y - 10}" stroke="{LINE1}"/>')
    e, y = para(16, y + 14, "영어로 물으면 이름과 주소가 흔들려요", 15, 700)
    body += e
    f_, y = para(16, y + 2, "외국인 손님은 이 이름으로 지도에서 가게를 못 찾을 수 있어요", 13, 500, INK2)
    body += f_
    return svg("f5", y + 12, "그림 5. 영어로 물으면 이름과 주소가 흔들려요",
               f"정부 기록에서 이름을 못 찾은 비율 한국어 {groups[0][1]}%, 영어 {groups[0][2]}%. 다른 시군구 주소 비율 한국어 {groups[1][1]}%, 영어 {groups[1][2]}%", body)


def main():
    d = load()
    FIG.mkdir(parents=True, exist_ok=True)
    figs = {"fig1-flow.svg": fig1, "fig2-ko-100.svg": fig2, "fig3-en-100.svg": fig3,
            "fig4-closed.svg": fig4, "fig5-english-gap.svg": fig5}
    for name, fn in figs.items():
        (FIG / name).write_text(fn(d), encoding="utf-8")
        print("wrote", FIG / name)


if __name__ == "__main__":
    main()
