"""정답 원천 수집: 한식진흥원 한식포털 '한식메뉴 외국어 표기법' 목록(길라잡이 800선, 공개 HTML 표).
주소 https://www.hansik.or.kr/board/dn/list/017?menuSn=12&curPage=N&rowSize=50
열: 번호, 요리명, Latina(로마자), English, 日本語, 中文(简体), 中文(繁體), bbsSeq(상세 글 번호).
출력: sampling/raw/hansik_menu_800_<YYYYMMDD>.csv (UTF-8) + SHA256SUMS. 상세 페이지(설명문)는 받지 않는다.
저작권: 한식포털 저작권정책(2026-10-28 확인)상 저작권은 한식진흥원에 있다. 연구 대조용으로만 쓰고 원문 표를 재배포하지 않는다."""
import csv, hashlib, html, re, sys, time, urllib.request
from datetime import date
from pathlib import Path

BASE = "https://www.hansik.or.kr/board/dn/list/017?menuSn=12&rowSize=50&curPage={}"
OUT_DIR = Path(__file__).parent / "raw"

def fetch(page):
    req = urllib.request.Request(BASE.format(page), headers={"User-Agent": "Mozilla/5.0 (define404-research; contact john@define404.com)"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

def parse(doc):
    tb = re.search(r"<table.*?</table>", doc, flags=re.S).group(0)
    total = re.search(r"전체(?:\s|<[^>]+>)*([\d,]+)(?:\s|<[^>]+>)*건", doc)
    rows = []
    for tr in re.findall(r"<tr[^>]*data-bbsseq=\"(\d+)\"[^>]*>(.*?)</tr>", tb, flags=re.S):
        seq, body = tr
        cells = [re.sub(r"<[^>]+>", " ", html.unescape(c)) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", body, flags=re.S)]
        cells = [re.sub(r"\s+", " ", c).strip() for c in cells]
        if len(cells) != 7:
            raise SystemExit(f"열 수 이상: {cells}")
        rows.append(dict(no=int(cells[0]), ko=cells[1], latin=cells[2], en=cells[3], ja=cells[4], zh_hans=cells[5], zh_hant=cells[6], bbsSeq=seq))
    return rows, int(total.group(1).replace(",", "")) if total else None

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"hansik_menu_800_{date.today():%Y%m%d}.csv"
    rows, total, page = [], None, 1
    while True:
        doc = fetch(page)
        got, total = parse(doc)
        if not got:
            break
        rows += got
        print(f"page {page}: {len(got)} rows (누적 {len(rows)}/{total})", file=sys.stderr)
        if total and len(rows) >= total:
            break
        page += 1
        time.sleep(1.0)
    nos = [r["no"] for r in rows]
    assert nos == list(range(1, len(rows) + 1)), "번호가 연속이 아님"
    assert len(set(r["bbsSeq"] for r in rows)) == len(rows), "bbsSeq 중복"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["no", "ko", "latin", "en", "ja", "zh_hans", "zh_hant", "bbsSeq"])
        w.writeheader(); w.writerows(rows)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (OUT_DIR / "SHA256SUMS").write_text(f"{digest}  {out.name}\n", encoding="utf-8")
    print(f"{len(rows)}행 (사이트 표시 전체 {total}건) → {out}\nSHA256 {digest}")

if __name__ == "__main__":
    main()
