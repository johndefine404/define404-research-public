"""원고용 쉬운 그림(그림 1~5)을 만든다.

  python analysis/make_figures.py      # analysis/out/ 를 읽어 report/figures/*.svg 를 쓴다

숫자는 전부 analysis/out 의 결과 파일(results.json, explore_contains.csv)에서 읽는다.
그림 안에 손으로 적은 숫자는 없다. 색은 define404.com 디자인 토큰(site.css)과 같다.
2호(001-local404/analysis/make_figures.py)를 복사해 고쳤다.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "out"
FIG = ROOT / "report" / "figures"

INK, INK2, INK3 = "#141414", "#4A4844", "#6E6A63"
LINE1, LINE2 = "#D6D1C7", "#B9B3A7"
SUNK, RAISED = "#EDEAE3", "#FBFAF7"
BLUE, RED = "#0A6797", "#DA2D2D"
BLUE2 = "#7FB2CC"
FONT = "'Wanted Sans Variable', 'Wanted Sans', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"
W = 360
LANGS = [("en", "영어"), ("ja", "일본어")]


def load():
    d = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    ex = {}
    with open(OUT / "explore_contains.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ex[(r["lang"], r["measure"])] = r
    return d, ex


def rate(d, lang, key):
    return d["preregistered"]["rates_" + lang][key]


def pct(p):
    return f"{p * 100:.1f}%"


def text(x, y, s, size=15, weight=500, fill=INK, anchor="start"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def width(s, size):
    w = 0
    for ch in s:
        if "가" <= ch <= "힣" or "぀" <= ch <= "ヿ" or "一" <= ch <= "鿿":
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


def fig1(d, ex):
    """조사 흐름 5단계."""
    n_menu, n_item = d["n_menus"], d["n_items"]
    steps = [
        (f"한식 메뉴 {n_menu}개를 뽑았어요", "정부 표준 표기가 있는 778개 가운데 음식 갈래별로 골고루"),
        ("사장님처럼 물었어요", "\"외국어 메뉴판을 만드는데 이 메뉴는 뭐라고 써요?\" 영어와 일본어로 하나씩"),
        ("웹 검색을 쓰는 AI가 답했어요", f"Claude Sonnet이 검색한 뒤 메뉴명 하나를 답했어요. 답 {n_item}개"),
        ("정부 표준과 맞춰 봤어요", "한식진흥원 표준 표기와 글자를 맞춰 똑같음, 비슷함, 다름으로 나눴어요"),
        ("출처도 봤어요", "답이 정부 표준 사이트를 출처로 들었는지 세어 봤어요"),
    ]
    body, y = [], 26
    for k, (head, sub) in enumerate(steps, 1):
        body.append(f'<circle cx="28" cy="{y + 10}" r="12" fill="{BLUE}"/>')
        body.append(text(28, y + 15, str(k), 13, 700, "#FFFFFF", "middle"))
        body.append(text(52, y + 16, head, 16, 700))
        lines, ny = para(52, y + 38, sub, 13.5, 500, INK2)
        body += lines
        if k < len(steps):
            body.append(f'<line x1="28" y1="{y + 26}" x2="{28}" y2="{ny + 2}" stroke="{LINE2}" stroke-width="1.5"/>')
        y = ny + 10
    return svg("f1", y + 2, "그림 1. 이렇게 조사했어요",
               f"한식 메뉴 {n_menu}개를 뽑아 영어와 일본어로 묻고, 웹 검색을 쓰는 Claude의 답 {n_item}개를 정부 표준 표기와 맞춰 똑같음, 비슷함, 다름으로 나눈 순서", body)


def waffle(x0, y0, cells, size=11, gap=2, cols=10):
    out = []
    for n, kind in enumerate(cells):
        cx, cy = x0 + (n % cols) * (size + gap), y0 + (n // cols) * (size + gap)
        fill = {"strict": BLUE, "loose": BLUE2, "mismatch": RED}[kind]
        out.append(f'<rect x="{cx}" y="{cy}" width="{size}" height="{size}" rx="2" fill="{fill}"/>')
    return out


def fig2(d, ex):
    """메뉴 100개를 물으면: 언어별 100칸."""
    order = ["strict", "loose", "mismatch"]
    body, y = [], 22
    size, gap = 11, 2
    grid_w = 10 * (size + gap) - gap
    per = {}
    for n, (lg, name) in enumerate(LANGS):
        x0 = 16 + n * 180
        p = per100([(k, rate(d, lg, k)["k"]) for k in order])
        per[lg] = p
        body.append(text(x0, y, name, 16, 700))
        cells = sum(([k] * p[k] for k in order), [])
        body += waffle(x0, y + 12, cells, size, gap)
        yy = y + 12 + 10 * (size + gap) + 16
        for k, col, lab in ((("strict", BLUE, "똑같아요")), ("loose", BLUE2, "비슷해요"), ("mismatch", RED, "달라요")):
            body.append(f'<rect x="{x0}" y="{yy - 10}" width="11" height="11" rx="2" fill="{col}"/>')
            body.append(text(x0 + 17, yy, f"{lab} {p[k]}", 13.5, 600, INK2))
            yy += 20
    y = yy + 4
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    lines, y = para(16, y + 22, "정부 표준과 똑같이 적은 답은 영어도 일본어도 다섯에 하나예요", 14, 700)
    body += lines
    return svg("f2", y + 8, "그림 2. 메뉴 100개를 물으면",
               f"영어는 100개 중 똑같음 {per['en']['strict']}, 비슷함 {per['en']['loose']}, 다름 {per['en']['mismatch']}. "
               f"일본어는 똑같음 {per['ja']['strict']}, 비슷함 {per['ja']['loose']}, 다름 {per['ja']['mismatch']}", body)


def hbar(body, x, y, w_full, segs, h=26):
    """segs: [(비율 0~1, 색)]. 왼쪽부터 쌓는다."""
    xx = x
    for p, col in segs:
        w = p * w_full
        body.append(f'<rect x="{xx:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="{col}"/>')
        xx += w
    return xx


def fig3(d, ex):
    """엄격 대 느슨 이상: 언어별 두 줄."""
    body, y = [], 24
    full = W - 32 - 56
    rows = [("똑같이 적은 답", "strict"), ("비슷하게라도 적은 답", "loose_or_strict")]
    vals = {}
    for head, key in rows:
        body.append(text(16, y, head, 16, 700))
        y += 12
        for lg, name in LANGS:
            r = rate(d, lg, key)
            vals[(lg, key)] = r["p"]
            body.append(text(16, y + 18, name, 13.5, 600, INK2))
            segs = [(rate(d, lg, "strict")["p"], BLUE)]
            if key == "loose_or_strict":
                segs.append((rate(d, lg, "loose")["p"], BLUE2))
            end = hbar(body, 72, y, full, segs)
            body.append(text(end + 6, y + 18, pct(r["p"]), 14, 700))
            y += 34
        y += 22
    body.append(f'<rect x="16" y="{y - 4}" width="11" height="11" rx="2" fill="{BLUE}"/>')
    body.append(text(33, y + 6, "똑같아요", 12.5, 500, INK2))
    body.append(f'<rect x="110" y="{y - 4}" width="11" height="11" rx="2" fill="{BLUE2}"/>')
    body.append(text(127, y + 6, "비슷해요", 12.5, 500, INK2))
    y += 22
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    lines, y = para(16, y + 22, "비슷한 답까지 쳐 주면 영어는 크게 늘고 일본어는 덜 늘어요", 14, 700)
    body += lines
    return svg("f3", y + 8, "그림 3. 비슷한 답까지 쳐 주면",
               f"똑같이 적은 답은 영어 {pct(vals[('en', 'strict')])}, 일본어 {pct(vals[('ja', 'strict')])}로 같은데, "
               f"비슷하게라도 적은 답은 영어 {pct(vals[('en', 'loose_or_strict')])}, 일본어 {pct(vals[('ja', 'loose_or_strict')])}", body)


def fig4(d, ex):
    """답 360개 점 가운데 정부 표준 사이트를 인용한 답."""
    n = d["n_items"]
    k = int(ex[("all", "cites_hansik_or_kr")]["k"])
    cols, size, gap = 30, 8, 3
    x0 = (W - (cols * (size + gap) - gap)) / 2
    body, y = [], 24
    lines, y = para(16, y, f"답 {n}개를 점으로 늘어놓았어요", 16, 700)
    body += lines
    y += 4
    for i in range(n):
        cx, cy = x0 + (i % cols) * (size + gap), y + (i // cols) * (size + gap)
        col = RED if i < k else LINE1
        body.append(f'<rect x="{cx:.1f}" y="{cy}" width="{size}" height="{size}" rx="2" fill="{col}"/>')
    y += (n // cols + (1 if n % cols else 0)) * (size + gap) + 14
    body.append(f'<rect x="16" y="{y - 9}" width="8" height="8" rx="2" fill="{RED}"/>')
    lines, y = para(30, y, f"빨간 점 {k}개: 한식진흥원 사이트를 출처로 든 답", 13.5, 600, INK2)
    body += lines
    body.append(f'<rect x="16" y="{y - 5}" width="8" height="8" rx="2" fill="{LINE1}"/>')
    lines, y = para(30, y + 4, f"회색 점 {n - k}개: 다른 곳만 출처로 든 답", 13.5, 600, INK2)
    body += lines
    y += 6
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    lines, y = para(16, y + 22, "검색을 했는데도 정부 표준 사이트에는 거의 닿지 않았어요", 14, 700)
    body += lines
    return svg("f4", y + 8, "그림 4. 정부 표준 사이트를 출처로 든 답",
               f"답 {n}개를 점으로 늘어놓으면 한식진흥원 사이트를 출처로 든 답은 {k}개뿐", body)


def fig5(d, ex):
    """괄호 안까지 보면: 언어별 두 막대."""
    body, y = [], 24
    full = W - 32 - 56
    vals = {}
    for lg, name in LANGS:
        s = rate(d, lg, "strict")["p"]
        c = float(ex[(lg, "standard_in_name_line")]["rate"])
        vals[lg] = (s, c)
        body.append(text(16, y, name, 16, 700))
        y += 12
        body.append(text(16, y + 18, "본 이름만", 13, 600, INK2))
        end = hbar(body, 86, y, full, [(s, BLUE)])
        body.append(text(end + 6, y + 18, pct(s), 14, 700))
        y += 32
        body.append(text(16, y + 18, "괄호까지", 13, 600, INK2))
        end = hbar(body, 86, y, full, [(c, BLUE2)])
        body.append(text(end + 6, y + 18, pct(c), 14, 700))
        y += 56
    lines, y = para(16, y, "본 이름만: 괄호 밖 이름이 표준과 똑같은 답. 괄호까지: 괄호 안 설명을 포함한 메뉴명 줄 어딘가에 표준 이름이 있는 답", 12, 500, INK3)
    body += lines
    y += 6
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    lines, y = para(16, y + 22, "괄호까지 봐도 영어 열에 여섯, 일본어 열에 일곱은 표준 이름이 없어요", 14, 700)
    body += lines
    return svg("f5", y + 8, "그림 5. 괄호 안 설명까지 보면",
               f"본 이름만 보면 표준과 똑같은 답이 영어 {pct(vals['en'][0])}, 일본어 {pct(vals['ja'][0])}인데, "
               f"괄호 안 설명까지 포함하면 표준 이름이 들어 있는 답이 영어 {pct(vals['en'][1])}, 일본어 {pct(vals['ja'][1])}", body)


def main():
    d, ex = load()
    FIG.mkdir(parents=True, exist_ok=True)
    figs = {"fig1-flow.svg": fig1, "fig2-100-menus.svg": fig2, "fig3-strict-vs-loose.svg": fig3,
            "fig4-cited-hansik.svg": fig4, "fig5-with-parentheses.svg": fig5}
    for name, fn in figs.items():
        (FIG / name).write_text(fn(d, ex), encoding="utf-8")
        print("wrote", FIG / name)


if __name__ == "__main__":
    main()
