"""원고용 쉬운 그림(그림 1~5)을 만든다.

  python analysis/make_figures.py      # analysis/out/results.json 을 읽어 report/figures/*.svg 를 쓴다

숫자는 전부 analysis/out/results.json(판정 규칙 v1.1)에서 읽는다. 그림 안에 손으로 적은 숫자는 없다.
2호(001-local404/analysis/make_figures.py)를 복사해 고쳤다. 색은 define404.com 디자인 토큰(site.css)과 같다.
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


def fig1(d):
    """조사 흐름 5단계."""
    n_all = cell(d, "all", "loose")[1]
    n_on, n_ex = cell(d, "ongoing", "loose")[1], cell(d, "expired", "loose")[1]
    n_ce, n_lo = cell(d, "central", "loose")[1], cell(d, "local", "loose")[1]
    steps = [
        (f"지원사업 공고 {n_all}건을 뽑았어요", f"기업마당 목록에서 진행 중 {n_on}건, 마감 {n_ex}건 (중앙부처 {n_ce}건, 지자체 {n_lo}건)"),
        ("공고마다 똑같이 물었어요", "\"지금 신청할 수 있나요? 마감일과 수행 기관은요?\" 한국어로, 공고 이름 그대로"),
        ("웹 검색을 쓰는 AI 비서가 답했어요", "Claude Sonnet, 문항마다 검색"),
        ("답에서 세 가지를 뽑았어요", "마감일, 신청 가능 여부(돼요·끝났어요·모름), 수행 기관"),
        ("공고 목록과 맞춰 봤어요", f"답 {n_all}개를 기업마당 공고의 신청 마감일·상태·수행 기관과 비교했어요"),
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
               "기업마당 공고 200건을 뽑아 AI 비서에게 한국어로 묻고, 답에서 마감일·신청 가능 여부·수행 기관을 규칙으로 뽑아 공고 목록과 맞춰 본 순서", body)


def fig2(d):
    """마감일을 맞게 말한 답: 100칸 점그림."""
    k, n = cell(d, "all", "loose")
    kc, nc = cell(d, "central", "loose")
    kl, nl = cell(d, "local", "loose")
    p = per100([("ok", k), ("no", n - k)])
    cells = [BLUE] * p["ok"] + [LINE1] * p["no"]
    L = 16
    body = [text(L, 28, "마감일을 물었더니", 15, 700), text(L, 46, f"답 {n}개를 100개로 줄였어요", 12, 500, INK3)]
    body += waffle(L, 60, cells)
    y = 60 + 160 + 20
    a, y = para(L, y, f"{p['ok']}개는 맞는 마감일을 말했어요", 15, 700, INK)
    body += a
    b, y = para(L, y + 2, f"{p['no']}개는 다른 날짜를 말했거나 마감일을 말하지 않았어요", 13, 500, INK2)
    body += b
    y += 10
    body.append(f'<line x1="{L}" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    y += 22
    body.append(text(L, y, f"중앙부처 공고 {nc}건 중 {kc}건, 지자체 공고 {nl}건 중 {kl}건", 13, 600, INK))
    y += 20
    body.append(text(L, y, "지자체라고 더 못 맞히지는 않았어요", 13, 500, INK2))
    y += 18
    legend = [(BLUE, "맞는 마감일"), (LINE1, "틀리거나 없음")]
    for i_, (col, lab) in enumerate(legend):
        lx = L + i_ * 150
        body += waffle(lx, y - 4, [col], size=12)
        body.append(text(lx + 19, y + 7, lab, 12.5, 500, INK2))
    return svg("f2", y + 24, "그림 2. AI에게 100번 물으면 마감일을 맞게 말한 답",
               f"마감일을 맞게 말한 답은 100칸 중 {p['ok']}칸, 중앙부처 공고는 {nc}건 중 {kc}건, 지자체 공고는 {nl}건 중 {kl}건", body)


def fig3(d):
    """신청 가능 여부: 모름 71 / 정답 방향 29 / 틀린 방향 0."""
    ok, n = cell(d, "all", "status_ok")
    unk, _ = cell(d, "all", "unknown")
    wrong = n - ok - unk
    p = per100([("unk", unk), ("ok", ok), ("wrong", wrong)])
    cells = [BLUE] * p["ok"] + [RED] * p["wrong"] + [LINE1] * p["unk"]
    L = 16
    body = [text(L, 28, "지금 신청할 수 있는지 물었더니", 15, 700), text(L, 46, f"답 {n}개를 100개로 줄였어요", 12, 500, INK3)]
    body += waffle(L, 60, cells)
    y = 60 + 160 + 20
    a, y = para(L, y, f"{p['unk']}개는 \"확인 못 했어요\"", 15, 700, INK)
    body += a
    b, y = para(L, y + 2, f"{p['ok']}개는 맞는 방향으로 딱 잘라 말했어요", 13, 500, INK2)
    body += b
    c, y = para(L, y, f"틀린 방향으로 딱 잘라 말한 답은 {wrong}개예요", 13, 500, INK2)
    body += c
    y += 10
    body.append(f'<line x1="{L}" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{LINE1}"/>')
    y += 22
    body.append(text(L, y, "10번 중 7번은 결국 공고를 직접 열어 봐야 해요", 13, 600, INK))
    y += 20
    legend = [(LINE1, "모른대요"), (BLUE, "맞게 단정"), (RED, "틀리게 단정")]
    for i_, (col, lab) in enumerate(legend):
        lx = L + i_ * 112
        body += waffle(lx, y - 4, [col], size=12)
        body.append(text(lx + 19, y + 7, lab, 12.5, 500, INK2))
    return svg("f3", y + 24, "그림 3. 신청 가능 여부를 물으면 10번 중 7번은 \"확인 못 했어요\"",
               f"100칸 중 {p['unk']}칸은 확인하지 못했다는 답, {p['ok']}칸은 정답 방향으로 단정한 답, 틀린 방향으로 단정한 답은 {p['wrong']}칸", body)


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


def fig4(d):
    """틀린 방향 단정 0: 마감 공고와 진행 공고 각 100건."""
    ex_ok, ex_n = cell(d, "expired", "status_ok")
    ex_unk, _ = cell(d, "expired", "unknown")
    on_ok, on_n = cell(d, "ongoing", "status_ok")
    on_unk, _ = cell(d, "ongoing", "unknown")
    ex_wrong, on_wrong = ex_n - ex_ok - ex_unk, on_n - on_ok - on_unk
    scale = (W - 36) / max(ex_n, on_n)
    body, y = [], 30
    y = bar_row(body, y, f"이미 마감된 공고 {ex_n}건", [(ex_ok, BLUE, "\"끝났어요\" 맞음"), (ex_wrong, RED, "\"아직 돼요\" 틀림"), (ex_unk, LINE1, "모름")], scale)
    y = bar_row(body, y + 8, f"지금 진행 중인 공고 {on_n}건", [(on_ok, BLUE, "\"아직 돼요\" 맞음"), (on_wrong, RED, "\"끝났어요\" 틀림"), (on_unk, LINE1, "모름")], scale)
    body.append(f'<line x1="16" y1="{y - 2}" x2="{W - 16}" y2="{y - 2}" stroke="{LINE1}"/>')
    body.append(text(16, y + 22, f"틀린 방향으로 딱 잘라 말한 답은 {ex_wrong + on_wrong}번이에요", 15, 700))
    body.append(text(16, y + 42, "끝난 사업을 아직 된다고 한 답은 없었어요", 13, 500, INK2))
    return svg("f4", y + 58, "그림 4. 틀린 방향으로 딱 잘라 말한 답은 0번이에요",
               f"마감된 공고 {ex_n}건에 \"마감됐어요\" {ex_ok}번, \"아직 돼요\" {ex_wrong}번, 모름 {ex_unk}번. 진행 중인 공고 {on_n}건에 \"아직 돼요\" {on_ok}번, \"마감됐어요\" {on_wrong}번, 모름 {on_unk}번", body)


def fig5(d):
    """느슨한 점수 → 엄격한 점수."""
    loose, n = cell(d, "all", "loose")
    strict, _ = cell(d, "all", "strict")
    scale = (W - 36) / n
    body, y = [], 30
    rows = [
        (f"물어본 공고 {n}건", [(n, SUNK, None)]),
        (f"마감일을 맞게 말한 답 {loose}번", [(loose, BLUE, None), (n - loose, SUNK, None)]),
        (f"신청 가능 여부와 수행 기관까지 다 맞은 답 {strict}번", [(strict, BLUE, None), (n - strict, SUNK, None)]),
    ]
    for head, segs in rows:
        lines, y = para(16, y, head, 14, 700)
        body += lines
        x = 16
        for v, col, _ in segs:
            w = v * scale
            body.append(f'<rect x="{x:.1f}" y="{y - 6}" width="{w:.1f}" height="26" fill="{col}"/>')
            if col == BLUE and w >= 44:
                body.append(text(x + 7, y + 12, f"{v}번", 13, 700, "#FFFFFF"))
            x += w + 2
        y += 56
    body.append(f'<line x1="16" y1="{y - 14}" x2="{W - 16}" y2="{y - 14}" stroke="{LINE1}"/>')
    body.append(text(16, y + 10, f"{n}번 중 다 맞은 답은 {strict}번이에요", 15, 700))
    body.append(text(16, y + 30, "마감일은 알아도 신청할 수 있는지는 자주 비워 뒀어요", 13, 500, INK2))
    return svg("f5", y + 46, "그림 5. 마감일은 맞았는데 전부 맞은 답은 더 적어요",
               f"{n}번 중 마감일을 맞게 말한 답은 {loose}번, 그중 신청 가능 여부와 수행 기관까지 다 맞은 답은 {strict}번", body)


def main():
    d = load()
    FIG.mkdir(parents=True, exist_ok=True)
    figs = {"fig1-flow.svg": fig1, "fig2-deadline-100.svg": fig2, "fig3-status-100.svg": fig3,
            "fig4-wrong-direction.svg": fig4, "fig5-loose-strict.svg": fig5}
    for name, fn in figs.items():
        (FIG / name).write_text(fn(d), encoding="utf-8")
        print("wrote", FIG / name)


if __name__ == "__main__":
    main()
