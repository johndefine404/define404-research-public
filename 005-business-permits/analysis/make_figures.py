"""원고용 쉬운 그림(그림 1~5)을 만든다.

  python analysis/make_figures.py      # analysis/out/results.json 을 읽어 report/figures/*.svg 를 쓴다

숫자는 전부 analysis/out/results.json(판정 규칙 v1.0)에서 읽는다. 그림 안에 손으로 적은 숫자는 없다.
5호(004-support-programs/analysis/make_figures.py)를 복사해 고쳤다. 색은 define404.com 디자인 토큰(site.css)과 같다.
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
    with open(OUT / "results.json", encoding="utf-8") as f:
        return json.load(f)


def cell(d, name, k):
    """사전 등록 칸의 (k, n)."""
    c = d["preregistered"]["cells"][name][k]
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
def eul(w):
    """목적격 조사: 받침 있으면 을, 없으면 를."""
    c = ord(w[-1]) - 0xAC00
    return w + ("을" if 0 <= c < 11172 and c % 28 else "를")


def ex(d, *keys):
    v = d["exploratory"]
    for k in keys:
        v = v[k]
    return v


def legend(body, y, items, step):
    for i_, (col, lab) in enumerate(items):
        lx = 16 + i_ * step
        body += waffle(lx, y - 4, [col], size=12)
        body.append(text(lx + 19, y + 7, lab, 12.5, 500, INK2))


def fig1(d):
    """조사 흐름 5단계."""
    n = cell(d, "all", "period_loose")[1]
    n_s, n_l = cell(d, "short", "period_loose")[1], cell(d, "long", "period_loose")[1]
    steps = [
        ("시군구 민원 안내표 6곳을 모았어요", "공공데이터포털에 처리기간과 수수료를 공개한 시군구 민원사무편람"),
        ("영업을 시작할 때 내는 민원을 골랐어요", f"신고·등록·허가 민원 중 무작위로 {n}건. 처리기간 짧은 민원 {n_s}건, 긴 민원 {n_l}건"),
        ("민원마다 똑같이 물었어요", "\"OO시에 이 민원을 내려고 해요. 처리기간은 며칠이고 수수료는 얼마인가요?\""),
        ("웹 검색을 쓰는 AI 비서가 답했어요", "Claude Sonnet, 문항마다 검색"),
        ("민원 안내표와 맞춰 봤어요", "답에 나온 날 수와 금액을 그 시군구 안내표 값과 비교했어요"),
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
               f"시군구 민원 안내표 6곳에서 영업 시작 민원 {n}건을 뽑아 AI 비서에게 처리기간과 수수료를 묻고, 답을 안내표 값과 맞춰 본 순서", body)


def waffle_fig(d, fid, key, title_head, what, conclusion, title):
    ok, n = cell(d, "all", f"{key}_loose")
    wrong, _ = cell(d, "all", f"{key}_wrong")
    unk, _ = cell(d, "all", f"{key}_unknown")
    p = per100([("ok", ok), ("wrong", wrong), ("unk", unk)])
    cells = [BLUE] * p["ok"] + [RED] * p["wrong"] + [LINE1] * p["unk"]
    body = [text(16, 28, title_head, 15, 700), text(16, 46, f"답 {n}개를 100개로 줄였어요", 12, 500, INK3)]
    body += waffle(16, 60, cells)
    y = 60 + 160 + 20
    a, y = para(16, y, f"{p['unk']}개는 {eul(what)} 말하지 않았어요", 15, 700)
    body += a
    b, y = para(16, y + 2, f"{p['ok']}개는 안내표와 같은 {eul(what)} 말했어요", 13, 500, INK2)
    body += b
    c, y = para(16, y, f"{p['wrong']}개는 다른 {what}만 말했어요", 13, 500, INK2)
    body += c
    y += 10
    body.append(f'<line x1="16" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    y += 22
    e, y = para(16, y, conclusion, 13, 600)
    body += e
    y += 4
    legend(body, y, [(BLUE, "맞음"), (RED, "틀림"), (LINE1, "말 안 함")], 100)
    return svg(fid, y + 24, title,
               f"100칸 중 {p['ok']}칸은 맞는 {what}, {p['wrong']}칸은 틀린 {what}, {p['unk']}칸은 {eul(what)} 말하지 않은 답", body)


def fig2(d):
    return waffle_fig(d, "f2", "period", "처리기간을 물었더니", "처리기간",
                      "절반 넘게는 며칠 걸리는지 답을 못 했어요", "그림 2. AI에게 100번 물으면 처리기간을 맞게 말한 답")


def fig3(d):
    return waffle_fig(d, "f3", "fee", "수수료를 물었더니", "수수료",
                      "수수료도 처리기간과 똑같이 셋 중 하나쯤만 맞았어요", "그림 3. AI에게 100번 물으면 수수료를 맞게 말한 답")


def fig4(d):
    """물어본 수 → 처리기간 맞음 → 둘 다 맞음 → 숫자 하나만 정확히."""
    pl, n = cell(d, "all", "period_loose")
    bl, _ = cell(d, "all", "both_loose")
    bs, _ = cell(d, "all", "both_strict")
    scale = (W - 36) / n
    rows = [
        (f"물어본 민원 {n}건", n, SUNK),
        (f"처리기간이 맞은 답 {pl}번", pl, BLUE),
        (f"처리기간과 수수료가 둘 다 맞은 답 {bl}번", bl, BLUE),
        (f"다른 숫자 섞지 않고 둘 다 정확히 맞은 답 {bs}번", bs, BLUE),
    ]
    body, y = [], 30
    for head, v, col in rows:
        lines, y = para(16, y, head, 14, 700)
        body += lines
        w = v * scale
        body.append(f'<rect x="16" y="{y - 6}" width="{W - 32}" height="26" fill="{SUNK}"/>')
        if col != SUNK:
            body.append(f'<rect x="16" y="{y - 6}" width="{w:.1f}" height="26" fill="{col}"/>')
            if w >= 44:
                body.append(text(23, y + 12, f"{v}번", 13, 700, "#FFFFFF"))
        y += 56
    body.append(f'<line x1="16" y1="{y - 14}" x2="{W - 16}" y2="{y - 14}" stroke="{LINE1}"/>')
    e, y2 = para(16, y + 10, f"{n}번 물어서 사장님이 그대로 믿어도 되는 답은 {bs}번이에요", 15, 700)
    body += e
    f_, y2 = para(16, y2 + 2, "나머지는 구청·시청 안내를 다시 봐야 해요", 13, 500, INK2)
    body += f_
    return svg("f4", y2 + 12, "그림 4. 처리기간과 수수료를 둘 다 정확히 맞힌 답은 열에 하나예요",
               f"{n}번 중 처리기간 맞음 {pl}번, 둘 다 맞음 {bl}번, 다른 숫자 없이 둘 다 정확히 맞음 {bs}번", body)


def fig5(d):
    """숫자를 말한 답만: 맞음 대 틀림."""
    body, y = [], 30
    rows = []
    for key, lab in (("period", "처리기간"), ("fee", "수수료")):
        g = ex(d, "given_claim", key)
        rows.append((lab, int(g["k"]), int(g["n"])))
    scale = (W - 36) / max(r[2] for r in rows)
    for lab, k, n in rows:
        y = bar_row(body, y, f"{eul(lab)} 숫자로 말한 답 {n}번", [(k, BLUE, "안내표와 같음"), (n - k, RED, "다름")], scale) + 8
    body.append(f'<line x1="16" y1="{y - 6}" x2="{W - 16}" y2="{y - 6}" stroke="{LINE1}"/>')
    e, y = para(16, y + 18, "숫자를 말할 때는 대체로 맞았어요", 15, 700)
    body += e
    f_, y = para(16, y + 2, "그런데 답 전부에 \"이 지역 값은 확인 못 했어요\"가 붙어 있었어요. 다른 지역 안내나 법령 서식에서 빌려 온 숫자였어요", 13, 500, INK2)
    body += f_
    return svg("f5", y + 12, "그림 5. 숫자를 말할 때는 대체로 맞았지만, 전부 \"확인 못 했어요\"가 붙었어요",
               f"처리기간을 숫자로 말한 답 {rows[0][2]}번 중 {rows[0][1]}번, 수수료를 숫자로 말한 답 {rows[1][2]}번 중 {rows[1][1]}번이 안내표와 같았어요", body)


def main():
    d = load()
    FIG.mkdir(parents=True, exist_ok=True)
    figs = {"fig1-flow.svg": fig1, "fig2-period-100.svg": fig2, "fig3-fee-100.svg": fig3,
            "fig4-both.svg": fig4, "fig5-given-claim.svg": fig5}
    for name, fn in figs.items():
        (FIG / name).write_text(fn(d), encoding="utf-8")
        print("wrote", FIG / name)


if __name__ == "__main__":
    main()
