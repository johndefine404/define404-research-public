"""원고용 쉬운 그림(그림 1~5)을 만든다. 2편(001-local404) make_figures.py 를 복사해 고쳤다.

  python analysis/make_figures.py      # analysis/out/ 를 읽어 report/figures/*.svg 를 쓴다

숫자는 전부 analysis/out 의 결과 파일에서 읽는다. 그림 안에 손으로 적은 숫자는 없다.
색은 define404.com 디자인 토큰(site.css)과 같다.
"""
import csv
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
LANG_NAME = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어", "vi": "베트남어"}
LANGS = ["ko", "en", "ja", "zh", "vi"]


def rows(name):
    with open(OUT / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load():
    d = {}
    h1 = rows("h1.csv")
    d["h1"] = next(r for r in h1 if r["confirmatory"] == "True")
    d["h1_lang"] = {r["comparison"].split(" - ")[1]: r for r in h1 if r["confirmatory"] == "False"}
    d["h2"] = {r["system"]: r for r in rows("h2.csv") if r["confirmatory"] == "True"}
    d["inv"] = {r["system"]: r for r in rows("data_inventory.csv")}
    d["corr"] = {r["lang"]: r for r in rows("explore_correctness.csv")
                 if r["system"] == "H-mem" and r["kind"] == "match_rate_among_said"}
    d["incons"] = next(r for r in rows("explore_inconsistency.csv") if r["system"] == "H-mem" and r["group"] == "all")
    return d


def i(r, k):
    return int(float(r[k]))


def pct(r, k):
    """비율 열을 소수 첫째 자리 퍼센트로."""
    return round(float(r[k]) * 100, 1)


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


def fig1(d):
    """조사 흐름 5단계."""
    inv = d["inv"]["H-mem"]
    n_shops, n_ans, n_na, n_ok = i(inv, "n_shops"), i(inv, "n_answers"), i(inv, "type_na_excluded(truth=기타)"), i(inv, "shops_complete_5lang_said_type")
    steps = [
        ("지난 조사의 답을 다시 꺼냈어요", f"음식점 {n_shops}곳에 5개 언어로 물어 받은 Claude Haiku의 답 {fmt(n_ans)}개. 새로 묻지 않았어요"),
        ("보기 전에 질문을 먼저 적었어요", "\"한국어로 물으면 업종을 더 자주 말할까?\" 답을 보기 전에 저장소에 기록했어요"),
        ("답마다 업종을 말했는지 표시했어요", "말했으면 1, 안 했으면 0. 판정은 지난 조사 것을 그대로 썼어요"),
        ("가게마다 언어끼리 비교했어요", f"5개 언어 답이 다 갖춰진 {n_ok}곳. 업태가 기타인 가게의 답 {n_na}개는 뺐어요"),
        ("차이와 오차 범위를 쟀어요", "한국어 대 나머지 4개 언어 평균. 웹 검색 조건과 카카오 등록 여부도 같이 봤어요"),
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
               f"지난 조사의 답 {fmt(n_ans)}개를 다시 꺼내, 질문을 먼저 기록하고, 답마다 업종을 말했는지 표시한 뒤, 5개 언어 답이 갖춰진 {n_ok}곳에서 언어끼리 비교한 순서", body)


def hbars(items, y0, scale, label_w=72):
    """items: (이름, 값(%), 색, 굵게). 가로 막대 한 줄씩."""
    body, y = [], y0
    x0 = 16 + label_w
    for name, v, col, bold in items:
        body.append(text(16, y + 15, name, 13.5, 700 if bold else 500, INK if bold else INK2))
        w = v * scale
        body.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="22" fill="{col}"/>')
        body.append(text(x0 + w + 6, y + 15, f"{v:.1f}%", 13, 700 if bold else 500, INK))
        y += 32
    return body, y


def fig2(d):
    """H1: 기억 조건 언어별 업종 말한 비율."""
    h1, hl = d["h1"], d["h1_lang"]
    n = i(h1, "n_shops")
    ko = pct(h1, "rate_ko")
    others = pct(h1, "rate_others_mean")
    diff = pct(h1, "diff")
    items = [("한국어", ko, BLUE, True)] + [(LANG_NAME[lg], pct(hl[lg], "rate_others_mean"), LINE2, False) for lg in ["vi", "zh", "ja", "en"]]
    items[1:] = sorted(items[1:], key=lambda t: -t[1])
    body = [text(16, 26, f"같은 가게 {n}곳, 업종을 말한 비율", 15, 700),
            text(16, 46, "웹 검색 없이 기억만으로 답한 Claude Haiku", 12, 500, INK3)]
    bars, y = hbars(items, 62, (W - 16 - 72 - 60) / 100)
    body += bars
    body.append(f'<line x1="16" y1="{y + 2}" x2="{W - 16}" y2="{y + 2}" stroke="{LINE1}"/>')
    lines, y2 = para(16, y + 26, f"한국어로 물으면 {ko:.1f}%, 나머지 4개 언어 평균은 {others:.1f}%예요", 14, 700)
    body += lines
    lines, y3 = para(16, y2 + 4, f"한국어가 {diff:.1f}%p 더 자주 업종을 말했어요", 13, 500, INK2)
    body += lines
    return svg("f2", y3 + 8, "그림 2. 어느 언어로 물으면 업종을 말할까요",
               f"기억 조건에서 같은 가게 {n}곳에 대해 업종을 말한 비율은 한국어 {ko:.1f}%, " +
               ", ".join(f"{LANG_NAME[lg]} {pct(hl[lg], "rate_others_mean"):.1f}%" for lg in ["vi", "zh", "ja", "en"]) +
               f". 한국어가 나머지 평균보다 {diff:.1f}%p 높아요", body)


def fig3(d):
    """H2: 웹 검색 조건에서는 차이가 작다."""
    h2 = d["h2"]
    cards = [("Claude Sonnet, 웹 검색", h2["S-search"]), ("Claude Haiku, 웹 검색", h2["H-search"])]
    n = i(h2["S-search"], "n_shops")
    body = [text(16, 26, f"웹 검색을 켜고 답한 {n}곳에서는", 15, 700)]
    y = 44
    scale = (W - 16 - 108 - 60) / 100
    for name, r in cards:
        body.append(text(16, y + 14, name, 13.5, 700))
        y += 22
        ko, ot = pct(r, "rate_ko"), pct(r, "rate_others_mean")
        bars, y = hbars([("한국어", ko, BLUE, True), ("나머지 4개 평균", ot, LINE2, False)], y, scale, label_w=108)
        body += bars
        body.append(text(16, y + 2, f"차이 {pct(r, "diff"):.1f}%p, 오차 범위 안이에요", 12, 500, INK3))
        y += 26
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    lines, y2 = para(16, y + 24, "웹 검색을 켜면 언어에 따른 차이가 거의 안 보였어요", 14, 700)
    body += lines
    lines, y3 = para(16, y2 + 4, f"다만 {n}곳이라 작은 차이는 못 잡아요", 13, 500, INK2)
    body += lines
    s, h = h2["S-search"], h2["H-search"]
    return svg("f3", y3 + 8, "그림 3. 웹 검색을 켜면 어떨까요",
               f"웹 검색 조건 {n}곳에서 업종을 말한 비율은 Sonnet 한국어 {pct(s, "rate_ko"):.1f}% 대 나머지 평균 {pct(s, "rate_others_mean"):.1f}%, "
               f"Haiku 한국어 {pct(h, "rate_ko"):.1f}% 대 {pct(h, "rate_others_mean"):.1f}%. 차이는 오차 범위 안", body)


def fig4(d):
    """탐색: 업종을 말했을 때 맞은 비율은 언어별로 비슷하다."""
    c = d["corr"]
    items = [(LANG_NAME[lg], pct(c[lg], "value"), BLUE, lg == "ko") for lg in LANGS]
    body = [text(16, 26, "업종을 말했을 때 맞은 비율", 15, 700)]
    lines, y = para(16, 46, "기억 조건, 업종을 말한 답만. 답 수는 " + ", ".join(f"{LANG_NAME[lg]} {i(c[lg], 'n_answers')}개" for lg in LANGS), 12, 500, INK3)
    body += lines
    bars, y = hbars(items, y + 6, (W - 16 - 72 - 60) / 100)
    body += bars
    body.append(f'<line x1="16" y1="{y + 2}" x2="{W - 16}" y2="{y + 2}" stroke="{LINE1}"/>')
    lo = min(pct(c[lg], "value") for lg in LANGS)
    hi = max(pct(c[lg], "value") for lg in LANGS)
    lines, y2 = para(16, y + 26, f"어느 언어든 {lo:.1f}~{hi:.1f}%, 서로 비슷해요", 14, 700)
    body += lines
    lines, y3 = para(16, y2 + 4, "더 자주 말한다고 더 자주 맞지는 않았어요", 13, 500, INK2)
    body += lines
    return svg("f4", y3 + 8, "그림 4. 말한 업종은 맞았을까요",
               "기억 조건에서 업종을 말한 답 가운데 맞은 비율은 " + ", ".join(f"{LANG_NAME[lg]} {pct(c[lg], "value"):.1f}%" for lg in LANGS) + ". 언어 간 차이가 작아요", body)


def waffle(x0, y0, cells, size=14, gap=2):
    out = []
    for n, kind in enumerate(cells):
        cx, cy = x0 + (n % 10) * (size + gap), y0 + (n // 10) * (size + gap)
        fill = {"split": BLUE, "same": LINE1}[kind]
        out.append(f'<rect x="{cx}" y="{cy}" width="{size}" height="{size}" rx="2" fill="{fill}"/>')
    return out


def fig5(d):
    """논의 요지: 가게 100곳 중 몇 곳이 언어에 따라 답이 갈렸나."""
    r = d["incons"]
    n, k = i(r, "n_shops"), i(r, "n_inconsistent")
    split = round(k * 100 / n)
    cells = ["split"] * split + ["same"] * (100 - split)
    body = [text(16, 26, f"가게 {n}곳을 100곳으로 줄이면", 15, 700),
            text(16, 46, "기억 조건, 5개 언어 답이 다 갖춰진 가게", 12, 500, INK3)]
    body += waffle(16, 60, cells)
    y = 60 + 160 + 20
    body += waffle(16, y - 11, ["split"], size=12)
    body.append(text(35, y, f"{split}곳: 언어에 따라 업종을 말하기도, 안 하기도 했어요", 12.5, 500, INK2))
    y += 22
    body += waffle(16, y - 11, ["same"], size=12)
    body.append(text(35, y, f"{100 - split}곳: 5개 언어가 모두 말했거나 모두 안 했어요", 12.5, 500, INK2))
    body.append(f'<line x1="16" y1="{y + 16}" x2="{W - 16}" y2="{y + 16}" stroke="{LINE1}"/>')
    lines, y2 = para(16, y + 40, "같은 가게인데 묻는 언어에 따라 답이 달라져요", 14, 700)
    body += lines
    lines, y3 = para(16, y2 + 4, "외국인 손님이 쓰는 언어로 직접 물어 확인해 보세요", 13, 500, INK2)
    body += lines
    return svg("f5", y3 + 8, "그림 5. 같은 가게, 언어마다 다른 답",
               f"기억 조건 {n}곳 중 {k}곳({split}%)은 언어에 따라 업종을 말하기도 안 하기도 했고, 나머지는 5개 언어가 모두 말했거나 모두 안 했어요", body)


def main():
    d = load()
    FIG.mkdir(parents=True, exist_ok=True)
    figs = {"fig1-flow.svg": fig1, "fig2-h1-by-language.svg": fig2, "fig3-search-no-gap.svg": fig3,
            "fig4-correct-when-said.svg": fig4, "fig5-split-shops.svg": fig5}
    for name, fn in figs.items():
        (FIG / name).write_text(fn(d), encoding="utf-8")
        print("wrote", FIG / name)


if __name__ == "__main__":
    main()
