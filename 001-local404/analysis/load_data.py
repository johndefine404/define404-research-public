"""(a) 답 적재·검증. 읽기 전용: collect/ 와 sampling/ 은 읽기만 한다.

규칙 (prereg 5·8절, HANDOFF 3·7절):
  - 시범 수집 답(qid 가 'P-' 로 시작, collect/pilot/)은 분석에서 뺀다. raw/ 에는 들어 있지 않지만 방어적으로 거른다.
  - 검색 조건(S-search, H-search)에서 searches == 0 인 답은 무효. 같은 qid 의 raw_retry 재수집 답(searches > 0,
    _partial 제외)이 있으면 그걸 쓰고, 없으면 결측.
  - W-mem 은 탐색 전용이라 확증 분석 입력에서 제외.
  - 검색 조건(S-search, H-search)은 결과 분석 전 결정(2026-10-24)으로 부표본 100곳 x 5언어(500문항)만 대상이다.
    부표본 밖 가게의 답은 raw 에 있어도 분석에 쓰지 않는다(outside_subsample_dropped 로 집계).
  - 이 모듈은 판정을 하지 않는다.
"""
import csv
import datetime as dt
import json
import re
import unicodedata
from pathlib import Path

import config as C

QID_RE = re.compile(r"^(L\d{4})-(ko|en|ja|zh|vi)$")
# 검색 조건 답인데 본문이 검색 한도 소진·미실행을 말하는 경우 (searches 필드가 1이어도 실제 검색은 안 된 답이 있다).
# 기본(strict)은 이런 답을 무효로 본다. HANDOFF 3절의 'searches==0 만 무효' 와 다르므로 확인 필요 (README 모호성 1번).
LIMIT_RE = re.compile(
    r"(?:검색|사용|이용|호출|횟수|쿼터)\s*한도|한도\s*(?:가\s*|를\s*)?(?:초과|소진|도달|에 달|다 )|소진|검색이?\s*(?:실행되지|수행되지)|search (?:limit|budget|quota|tool)|usage limit|rate limit|"
    r"budget .{0,40}(?:used|ran out)|ran out|no search (?:was|could)|search(?:es)? (?:was|were) not (?:run|executed)|"
    r"検索.{0,8}(?:上限|制限|実行されなかった|実行できなかった)|利用上限|上限に達|"
    r"配额|额度|已用完|已用尽|未能执行|没有执行|未执行|执行不成功|搜索(?:未成功|失败)|未能搜索|"
    r"hạn mức|đã hết|không thực hiện được|chưa thực hiện được", re.I)


def _script_counts(text):
    """글자(Unicode L*)를 문자 체계별로 센다: hangul, kana, han, latin, other."""
    c = {"hangul": 0, "kana": 0, "han": 0, "latin": 0, "other": 0}
    for ch in text:
        if not ch.isalpha():
            continue
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F:
            c["hangul"] += 1
        elif 0x3040 <= o <= 0x30FF or 0x31F0 <= o <= 0x31FF or 0xFF66 <= o <= 0xFF9F:
            c["kana"] += 1
        elif 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0xF900 <= o <= 0xFAFF:
            c["han"] += 1
        elif unicodedata.name(ch, "").startswith("LATIN"):
            c["latin"] += 1
        else:
            c["other"] += 1
    return c


def script_ok(lang, text):
    """언어 이탈(language drift) 검사. 보수적: 명백히 다른 문자 체계일 때만 False.
    수집 에이전트가 사용자 메모리('한국어로만 답하라')의 영향으로 일본어 질문에 한국어로 답한 사례를 거르려는 목적(2026-10-24).
      ja: 가나가 있으면 유효. 가나 없고 한글이 우세(나머지 글자의 2배 초과)면 무효 (영어·한자만 있는 답은 보수적으로 유효).
      zh: 한자가 있고 한글 우세가 아니어야 유효.
      ko: 한글이 있어야 유효.
      en/vi: 라틴 글자가 절반 이상이고 한글 우세가 아니어야 유효 (성조 없는 베트남어도 라틴이라 유효)."""
    c = _script_counts(str(text))
    tot = sum(c.values())
    if tot == 0:
        return False
    hang_dom = c["hangul"] > 2 * (tot - c["hangul"])      # 한글이 나머지 글자의 2배 초과 (상호명 인용 정도로는 안 걸린다)
    if lang == "ja":
        return c["kana"] > 0 or not hang_dom
    if lang == "zh":
        return c["han"] > 0 and not hang_dom
    if lang == "ko":
        return c["hangul"] > 0
    if lang in ("en", "vi"):
        return c["latin"] * 2 >= tot and not hang_dom
    return True


def lang_of(qid):
    m = QID_RE.match(qid or "")
    return m.group(2) if m else None


def _ok(rec, search_validity):
    """검색 조건 답이 유효한가: searches>0, strict 이면 본문에 검색 한도·미실행 문구가 없고 질문 언어의 문자 체계일 것."""
    if (rec.get("searches") or 0) <= 0:
        return False
    if search_validity == "strict":
        ans = str(rec.get("answer", ""))
        if LIMIT_RE.search(ans):
            return False
        lg = lang_of(rec.get("qid", ""))
        if lg and not script_ok(lg, ans):
            return False
    return True


BAD_LINES = []   # (파일, 줄번호): 쓰는 도중인 파일의 잘린 줄 등. 건너뛰고 경고로 보고한다.


def _jsonl(path):
    out = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                BAD_LINES.append((str(path), i))
    return out


def load_sample():
    """정답표. 가게 단위 행."""
    rows = []
    with open(C.SAMPLE_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            st, kk, rg = r["stratum"].split("|")
            truth_open = r["영업상태명"].startswith("영업")
            truth_closed = r["영업상태명"].startswith("폐업")
            assert truth_open != truth_closed, r["item_id"]
            days = None
            if truth_closed and r["폐업일자"]:
                d0 = dt.date.fromisoformat(r["폐업일자"])
                d1 = dt.date.fromisoformat(r["측정일"] or C.MEASURE_DATE)
                days = (d1 - d0).days
            rows.append({
                "item_id": r["item_id"], "truth": "open" if truth_open else "closed",
                "kakao": "registered" if r["kakao"] == "있음" else "unregistered",
                "region": "metro" if rg == "광역" else "province",
                "days_since_close": days,
                "address": r["주소"], "sigungu": r["시군구"], "sido": r["시도"],
                "biz_type": r["업태구분명"], "name": r["사업장명"],
            })
    return rows


def subsample_ids():
    """검색 2조건 부표본 가게 100곳 (sampling/subsample_search_v1.csv, 시드 20261024). 결과 분석 전 결정."""
    with open(C.SUBSAMPLE_CSV, encoding="utf-8", newline="") as f:
        return {r["item_id"] for r in csv.DictReader(f)}


def expected_qids(system):
    """배치 파일(collect/batches/<접두어>_*.json)에 적힌 문항 = 시스템이 받아야 할 문항.
    메모리 조건은 800곳 x 5언어 = 4,000개. 검색 2조건(C.SUBSAMPLE_SYSTEMS)은 부표본 100곳 x 5언어 = 500개."""
    pref = C.SYSTEMS[system]["batch_prefix"]
    sub = subsample_ids() if system in C.SUBSAMPLE_SYSTEMS else None
    s = set()
    for f in sorted((C.COLLECT / "batches").glob(f"{pref}_*.json")):
        for it in json.loads(f.read_text(encoding="utf-8")):
            if sub is None or QID_RE.match(it["qid"]).group(1) in sub:
                s.add(it["qid"])
    return s


def load_answers(search_validity="strict"):
    """search_validity:
         'strict'        검색 조건 답은 searches>0 이고 본문이 검색 한도·미실행을 말하지 않는 것만 유효 (기본, 확인 필요).
         'searches_only' searches>0 이면 전부 유효 (HANDOFF 3절 문구 그대로).
       반환: (answers: list[dict], inventory: list[dict], warnings: list[str]).
    answers 의 각 행: system, qid, item_id, lang, answer, searches, stage('raw'|'retry'), limit_text(bool), lang_drift(bool)."""
    sample_ids = {r["item_id"] for r in load_sample()}
    sub_ids = subsample_ids()
    answers, inv, warns = [], [], []
    BAD_LINES.clear()
    for system, meta in C.SYSTEMS.items():
        exp = expected_qids(system)
        is_search = meta["cond"] == "search"
        raw_dir = C.COLLECT / "raw" / system
        raw = {}
        n_raw_files = 0
        n_pilot = n_dup = n_badqid = n_empty = n_unexpected = n_outsub = 0
        for f in sorted(raw_dir.glob("*.jsonl")) if raw_dir.exists() else []:
            n_raw_files += 1
            for rec in _jsonl(f):
                q = rec.get("qid", "")
                if q.startswith("P-"):
                    n_pilot += 1; continue
                m = QID_RE.match(q)
                if not m or m.group(1) not in sample_ids:
                    n_badqid += 1; continue
                if system in C.SUBSAMPLE_SYSTEMS and m.group(1) not in sub_ids:
                    n_outsub += 1; continue          # 부표본 밖 가게(결정 2026-10-24): 분석 제외
                if q not in exp:
                    n_unexpected += 1; continue
                if not str(rec.get("answer", "")).strip():
                    n_empty += 1; continue
                if q in raw:
                    n_dup += 1; continue          # 첫 기록을 쓴다
                raw[q] = rec
        retry = {}
        if is_search or system == "H-mem":
            rdir = C.COLLECT / "raw_retry" / system   # _partial 은 하위 폴더라 glob("*.jsonl") 에 안 걸린다
            for f in sorted(rdir.glob("*.jsonl")) if rdir.exists() else []:
                for rec in _jsonl(f):
                    q = rec.get("qid", "")
                    if (QID_RE.match(q) and q in exp and str(rec.get("answer", "")).strip()
                            and ((rec.get("searches") or 0) > 0 or not is_search)):
                        # 같은 qid 가 둘이면 뒤 것. 단 유효한 답(strict 에서는 한도 문구 없는 답)이 이미 있으면 무효 답으로 덮지 않는다.
                        old = retry.get(q)
                        if old is None or not _ok(old, search_validity) or _ok(rec, search_validity):
                            retry[q] = rec
        n_drift = n_drift_excluded = n_hmem_replaced = 0
        n_valid = n_raw_valid = n_retry_used = n_invalid_search0 = n_limit_text = n_limit_excluded = 0
        for q in sorted(exp):
            rec, stage = None, None
            r0 = raw.get(q)
            if is_search:
                # 원본 답이 유효하면 원본. 무효(searches==0, strict 에서는 한도 문구 포함)면 재수집 답을 우선한다.
                if r0 is not None and _ok(r0, search_validity):
                    rec, stage = r0, "raw"
                elif q in retry:
                    rec, stage = retry[q], "retry"
                elif r0 is not None and (r0.get("searches") or 0) > 0:
                    rec, stage = r0, "raw"       # 한도 문구 답뿐인 경우: 아래에서 strict 면 제외, 집계만 한다
                if r0 is not None and (r0.get("searches") or 0) == 0:
                    n_invalid_search0 += 1
            else:
                if r0 is not None:
                    rec, stage = r0, "raw"
                    if system == "H-mem" and q in retry:
                        # H-mem 언어 이탈(ja_001 전부 한글) 재수집: 원본이 이탈이고 재수집 답이 script_ok 면 재수집 답을 쓴다.
                        lg = QID_RE.match(q).group(2)
                        if not script_ok(lg, r0["answer"]) and script_ok(lg, retry[q]["answer"]):
                            rec, stage = retry[q], "retry"
                            n_hmem_replaced += 1
                    if (r0.get("searches") or 0) > 0:
                        warns.append(f"{system} {q}: 기억 조건인데 searches>0")
            if rec is None:
                continue
            lim = bool(is_search and LIMIT_RE.search(rec["answer"]))
            n_limit_text += lim
            if lim and search_validity == "strict":
                n_limit_excluded += 1
                continue
            drift = not script_ok(QID_RE.match(q).group(2), rec["answer"])
            n_drift += drift
            if drift and (is_search or system == "H-mem") and search_validity == "strict":
                n_drift_excluded += 1          # 언어 이탈 답은 무효: 재수집 대상 (collect/retry_prep.py)
                continue
            n_valid += 1
            n_raw_valid += stage == "raw"
            n_retry_used += stage == "retry"
            m = QID_RE.match(q)
            answers.append({"system": system, "qid": q, "item_id": m.group(1), "lang": m.group(2),
                            "answer": rec["answer"], "searches": rec.get("searches") or 0,
                            "stage": stage, "limit_text": lim, "lang_drift": bool(drift)})
        inv.append({"system": system, "expected": len(exp), "raw_files": n_raw_files,
                    "valid": n_valid, "valid_from_raw": n_raw_valid, "valid_from_retry": n_retry_used,
                    "missing": len(exp) - n_valid, "missing_rate": round((len(exp) - n_valid) / len(exp), 4),
                    "invalid_search0_in_raw": n_invalid_search0,
                    "searches_gt0_but_answer_mentions_search_limit": n_limit_text,
                    "excluded_for_search_limit_text": n_limit_excluded,
                    "lang_drift_flagged": n_drift, "excluded_for_lang_drift": n_drift_excluded, "hmem_drift_replaced_by_retry": n_hmem_replaced, "search_validity": search_validity,
                    "pilot_dropped": n_pilot, "dup_dropped": n_dup, "bad_qid": n_badqid,
                    "empty_dropped": n_empty, "unexpected_qid": n_unexpected,
                    "outside_subsample_dropped": n_outsub})
    for f, i in BAD_LINES:
        warns.append(f"unparseable JSONL line skipped: {f}:{i} (file may be mid-write)")
    for w in C.EXPLORATORY_ONLY:
        d = C.COLLECT / "raw" / w
        n = sum(len(_jsonl(f)) for f in d.glob("*.jsonl")) if d.exists() else 0
        inv.append({"system": w, "expected": None, "raw_files": None, "valid": 0,
                    "note": f"탐색 전용, 확증 분석 제외 (원본 {n}답)"})
    return answers, inv, warns


if __name__ == "__main__":
    a, inv, w = load_answers()
    for r in inv: print(r)
    print(len(a), "answers;", len(w), "warnings")
