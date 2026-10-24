"""(b) 판정 단계. judge/rules.md v1.0 의 결정적(deterministic) 부분 + LLM 보조 분류 인터페이스(스텁).

원칙
  - 이 파일은 모델·검색·네트워크를 호출하지 않는다.
  - 확신할 수 있는 답만 다국어 표현 사전으로 판정하고, 애매한 답은 'review' 로 남겨 review 큐에 쓴다.
    판정을 지어내지 않는다. review 는 (1) LLM 보조 분류 결과 파일이 있으면 그것으로, (2) 없으면 미해결로 둔다.
  - rules.md 5절: 보조 분류는 규칙 원문만 보고 답 하나씩 분류하며 정답을 보지 않는다. 정답 대조는 코드(이 파일)가 한다.
    그래서 큐(review_queue.jsonl)에는 정답 정보를 넣지 않는다.
  - 사전 규칙이 모호한 곳은 review 로 보내는 쪽으로 보수적으로 짰다. 이 사전은 사전 등록 이후 작성되었으므로
    사람 200답 검증(human_sample.py)으로 일치율을 보고해야 한다.

판정 값
  status : open | closed | unknown | review      (review = 사전으로 확정 못 함, 보조 분류/사람 필요)
  address: match | wrong | none | review | na    (na = 정답 주소 없음)
  type   : match | wrong | none | review | na    (na = 정답 업태가 '기타' -> rules.md 3절: 업종 판정에서 뺀다)
  correct_lenient : True/False/None   (None = 모름 또는 review)   -- 모름은 맞음도 틀림도 아님 (rules.md 1절)
  correct_strict  : True/False/None
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import config as C

_I = re.I

# ---------------------------------------------------------------- 영업 상태 사전 (rules.md 1절)
UNKNOWN_CORE = re.compile("|".join([
    # ko
    r"확인(?:할 수 없|하지 못|되지 않|이 어렵|이 불가|할 길)", r"알 수 없", r"알지 못", r"찾지 못", r"찾을 수 없", r"정보가 없",
    r"근거(?:도|가) 없", r"단정(?:할|해) 수 없", r"알려 ?드릴 수 없", r"확인되지", r"판단(?:할|하기) (?:수 )?없", r"실시간.{0,12}(?:없|못|않)", r"접근할 수 없",
    # en
    r"\b(?:cannot|can't|can not|could not|couldn't|unable to|not able to|do not|don't|did not|didn't|will not|won't)\s+"
    r"(?:\w+\s+){0,4}?(?:confirm|verify|determine|find|say|tell|know|establish|check|identify)",
    r"\bno (?:reliable |verified |current |live )?(?:information|data|record|listing|results?)\b",
    r"\bnot (?:verified|confirmed|found)\b", r"\bunverified\b", r"\bunable to\b",
    r"\b(?:cannot|can't|could not|couldn't|will not|won't)\s+(?:\w+\s+){0,2}?(?:give|provide|offer|share|access|browse|look up|search)",
    r"\b(?:don't|do not|doesn't|have no|no)\s+(?:have\s+)?(?:\w+\s+){0,2}?(?:access|real-time|live)\b", r"large language model",
    r"\bI (?:am|'m) not (?:sure|able)\b", r"\blimited access\b",
    # ja
    r"確認(?:でき|が取れ)", r"わかりません", r"分かりません", r"見つかりません", r"見つけられ", r"不明",
    r"お答えできません", r"特定でき", r"情報(?:が|は)(?:ありません|得られ)", r"でき(?:ません|なかった|ず)", r"判断(?:でき|が)", r"リアルタイム",
    # zh
    r"无法", r"不能(?:确认|确定)", r"未能", r"找不到", r"没有找到", r"未找到", r"不确定", r"实时",
    # vi
    r"(?:không|chưa)\s+(?:thể\s+)?(?:xác nhận|xác minh|biết|tìm thấy|tìm được|kiểm chứng|chắc|khẳng định)",
    r"không rõ", r"chưa rõ", r"không có thông tin", r"không có .{0,25}xác nhận", r"không thể nói chắc", r"thời gian thực",
]), _I)

# 영업 여부를 묻거나 간접 의문으로 되풀이하는 문장 -> 결론 아님
INTERROG = re.compile("|".join([
    r"영업(?:을)?\s*(?:하는지|중인지|하고 있는지)", r"영업\s*(?:중\s*)?여부", r"폐업\s*여부", r"(?:열었|닫았)는지",
    r"\bwhether\b", r"\bif (?:it|the|this)\b", r"\bor not\b", r"\bis it (?:still )?open\b",
    r"かどうか", r"でしょうか", r"是否", r"有没有", r"是不是", r"(?:có|còn).{0,12}hay không", r"liệu",
]), _I)

OPEN_PAT = re.compile("|".join([
    r"영업\s*중(?!\s*(?:인지|여부|인가))", r"영업하고 있", r"영업을 하고 있", r"정상\s*영업", r"운영\s*중(?!\s*(?:인지|여부))", r"영업합니다",
    r"\b(?:is|are|remains?|appears? to be|seems? to be|looks? to be|currently|still)\s+(?:currently\s+|still\s+)?"
    r"(?:open|operating|operational|in business|running)\b",
    r"\bopen for business\b",
    r"営業中", r"営業しています", r"営業しております", r"現在も営業", r"通常営業",
    r"(?:仍在|仍然在|还在|依然在|正在|目前在|目前仍在|现在在)营业", r"营业中", r"正常营业", r"仍营业",
    r"(?:đang|vẫn)\s+(?:hoạt động|mở cửa|kinh doanh)", r"còn mở cửa(?!\s+hay)", r"vẫn còn hoạt động",
]), _I)

CLOSED_PAT = re.compile("|".join([
    r"폐업(?:했|한|하였|됐|된|상태|이라|으로|입니다|함|처리|신고)", r"문을 닫", r"영업을?\s*종료", r"영업\s*종료",
    r"운영(?:을)?\s*(?:하지 않|중단|종료)", r"영구\s*휴업", r"영업(?:을)?\s*하지 않",
    r"\b(?:permanently|has|have|had|is|are|was|been|now|already|appears? to be|seems? to be)\s+(?:permanently\s+)?"
    r"(?:closed|shut down|defunct)\b(?!\s+(?:on|for|at|until|from|during|between))",
    r"closed down", r"\b(?:out of|went out of) business\b", r"no longer (?:open|operating|in business|operational|exist)",
    r"ceased operations?", r"permanently closed", r"\bnot (?:currently |still )?(?:open|operating)\b",
    r"閉店", r"廃業", r"閉業", r"営業していません", r"営業しておりません", r"営業を終了", r"営業終了",
    r"已(?:经)?(?:关闭|停业|歇业|倒闭|关门|结业|闭店|永久关闭|永久停业)", r"关门", r"歇业", r"停止营业", r"不再营业", r"永久关闭", r"永久停业",
    r"(?:đã|đang)\s+(?:đóng cửa|ngừng hoạt động|ngừng kinh doanh|dừng hoạt động)",
    r"không còn (?:hoạt động|mở cửa|kinh doanh)", r"đóng cửa vĩnh viễn",
]), _I)

HEDGE = re.compile("|".join([
    r"\b(?:may|might|possibly|could have|likely|probably|perhaps|appears?|seems?|looks? like|reportedly)\b",
    r"것으로 보|보입니다|가능성|추정|듯|수 있", r"可能性|思われ|でしょう|かもしれ|ようです|らしい", r"可能|似乎|或许|大概|应该|看起来",
    r"có thể|dường như|có lẽ|khả năng",
]), _I)

OTHER_ENTITY = re.compile("|".join([
    r"다른 (?:가게|곳|지점|매장|식당|브랜드)", r"동명", r"\b(?:different|another|other|similarly named|same name)\b",
    r"別の", r"同名", r"另一", r"其他", r"khác\b", r"cùng tên",
]), _I)

NEG = re.compile(r"\b(?:not|no|never|none|nor|without)\b|n't\b|없|않|못|아니|ない|ません|ずに|没有|无法|未能|不|không|chưa|chẳng", _I)

STATUS_WORD = re.compile(r"영업|폐업|운영|open|clos|operat|business|営業|閉店|营业|关门|歇业|hoạt động|mở cửa|đóng cửa|상태|status", _I)

# 소문자로 이어지면 같은 문장. 한글 바로 뒤의 '!' 는 상호의 일부로 보고 자르지 않는다.
SENT_SPLIT = re.compile(r"(?:(?<=[.?。！？])|(?<=[A-Za-z0-9)\]'\"]!))\s+(?![a-z])|(?<=[。！？])|\n+")
_ABBR = re.compile(r"\b(Co|Ltd|Inc|Corp|St|Mt|No|Dr|Jr|Sr|vs|etc)\.", re.I)


def split_sentences(text):
    t = _ABBR.sub(lambda m: m.group(1) + "․", text)     # 약어의 점을 임시로 바꿔 문장 분리를 막는다
    return [x.replace("․", ".").strip() for x in SENT_SPLIT.split(t) if x and x.strip()]


def _norm(t):
    return unicodedata.normalize("NFKC", t).strip()


def classify_status(answer):
    """-> (label, reason).  label in open|closed|unknown|review."""
    text = _norm(answer)
    sents = split_sentences(text)
    dec = []         # (polarity, hedged, other_entity)
    status_unknown = False
    any_unknown = bool(UNKNOWN_CORE.search(text))
    for s in sents:
        unk = bool(UNKNOWN_CORE.search(s))
        neutral = unk or bool(INTERROG.search(s))
        if neutral:
            if STATUS_WORD.search(s):
                status_unknown = True
            continue
        o, c = bool(OPEN_PAT.search(s)), bool(CLOSED_PAT.search(s))
        if o and c:
            return "review", "same sentence has open and closed cues"
        if o and NEG.search(s):
            return "review", "open cue with negation in the same sentence"
        if o or c:
            dec.append(("open" if o else "closed", bool(HEDGE.search(s)), bool(OTHER_ENTITY.search(s))))
    if not dec:
        if status_unknown or any_unknown:
            return "unknown", "no status conclusion; cannot-confirm wording"
        return "review", "no recognizable status wording"
    pols = {d[0] for d in dec}
    if len(pols) > 1:
        return "review", "both open and closed conclusions"
    if status_unknown:
        return "review", "conclusion plus status-unknown sentence"
    if any(d[1] for d in dec):
        return "review", "hedged conclusion"
    if any(d[2] for d in dec) or (len(dec) > 1 and OTHER_ENTITY.search(text)):
        return "review", "possible other-entity statement"
    return pols.pop(), "single unhedged conclusion"


# ---------------------------------------------------------------- 주소 (rules.md 2절)
_ROAD = re.compile(r"([가-힣A-Za-z0-9]+(?:대로|로|길)(?:\d+번?길)?)")
_DONG = re.compile(r"\(([가-힣0-9]+(?:동|읍|면|가|리))(?:[,)\s]|$)")
_ANY_KO_ADDR = re.compile(r"[가-힣0-9]+(?:대로|로|길)\s?\d|[가-힣0-9]+(?:동|읍|면|리)\s?\d+(?:-\d+)?")
_ROMAN_ADDR = re.compile(r"\b[A-Za-z0-9\-]+(?:-ro|-gil|-daero)\s*\d|\b\d{1,4}(?:-\d{1,4})?,?\s+[A-Za-z0-9\- ]{0,30}(?:-ro|-gil|-daero|-dong)\b", _I)


def truth_address_tokens(addr):
    """정답 주소에서 도로명(길 이름까지)과 괄호 안 법정동·읍면 토큰."""
    a = _norm(addr)
    head = re.sub(r"\(.*?\)", "", a)
    roads = []
    for m in _ROAD.finditer(head):
        tok = m.group(1)
        if re.search(r"(?:로|길)$", tok) and len(tok) >= 3:
            roads.append(tok)
    dongs = [m.group(1) for m in _DONG.finditer(a)]
    return roads[:1], dongs


def judge_address(answer, truth_addr):
    if not truth_addr:
        return "na"
    text = _norm(answer)
    roads, dongs = truth_address_tokens(truth_addr)
    compact = re.sub(r"\s+", "", text)
    for r in roads:
        if r in compact:
            return "match"
    for d in dongs:
        if d in compact:
            return "match"
    if _ANY_KO_ADDR.search(text) or _ROMAN_ADDR.search(text):
        return "review"          # 다른 주소를 말했는지, 다른 가게 주소인지 사전으로 못 가른다
    return "none"


# ---------------------------------------------------------------- 업종 (rules.md 3절)
BUNDLE_MAP = {  # 업태구분명 -> 묶음 (rules.md 3절 대응표)
    "한식": "한식", "중국식": "중식", "일식": "일식",
    "경양식": "양식", "외국음식전문점(인도,태국등)": "양식", "패밀리레스토랑": "양식",
    "패밀리레스트랑": "양식",      # 표본 파일의 실제 표기(철자 다름). rules.md 는 '패밀리레스토랑'. 확인 필요(README)
    "분식": "분식",
    "호프/통닭": "치킨호프주점", "통닭(치킨)": "치킨호프주점", "정종/대포집/소주방": "치킨호프주점", "감성주점": "치킨호프주점",
    "까페": "카페디저트", "전통찻집": "카페디저트", "키즈카페": "카페디저트",
}


def truth_bundle(biz_type):
    return BUNDLE_MAP.get(biz_type, "기타")


_KW_SRC = {
    "한식": r"한식|김치찌개|된장|순두부|국밥|설렁탕|갈비|삼겹살|불고기|냉면|비빔밥|곰탕|해장국|백반|족발|보쌈|감자탕|칼국수|한정식|삼계탕|추어탕|"
          r"korean (?:restaurant|food|cuisine|bbq)|kimchi|bibimbap|galbi|samgyeopsal|naengmyeon|韓国料理|韓食|韩餐|韩式|韓式|món hàn|nhà hàng hàn quốc",
    "중식": r"중식|중국집|짜장|짬뽕|탕수육|chinese (?:restaurant|food|cuisine)|中華|中餐|中国料理|中式|món hoa|đồ ăn trung",
    "일식": r"일식|초밥|스시|라멘|우동|japanese (?:restaurant|food|cuisine)|sushi|ramen|udon|日本料理|寿司|ラーメン|日料|拉面|món nhật",
    "양식": r"양식|경양식|파스타|피자|스테이크|햄버거|버거|이탈리안|western|pizza|pasta|steak|burger|italian|ステーキ|ピザ|パスタ|西餐|披萨|món âu",
    "분식": r"분식|떡볶이|김밥|tteokbokki|gimbap|kimbap|トッポッキ|キンパ|年糕|紫菜包饭|bánh gạo cay",
    "치킨호프주점": r"치킨|통닭|호프|주점|술집|포차|이자카야|소주방|chicken|\bpub\b|\bbar\b|hof\b|soju|izakaya|居酒屋|炸鸡|酒馆|酒吧|quán nhậu|quán rượu|gà rán",
    "카페디저트": r"카페|커피|디저트|베이커리|찻집|\bcafe\b|café|coffee|dessert|bakery|カフェ|コーヒー|咖啡|quán cà phê|tiệm bánh",
}
_KW = {k: re.compile(v, _I) for k, v in _KW_SRC.items()}
CANNOT_ONLY = re.compile(
    r"확인(?:할 수 없|하지 못)|알 수 없|\b(?:cannot|can't|could not|couldn't|unable to)\b|無法|无法|できません|không (?:thể|xác định)|chưa rõ|không rõ", _I)


def judge_type(answer, biz_type):
    tb = truth_bundle(biz_type)
    if tb == "기타":
        return "na"
    text = _norm(answer)
    found = set()
    for s in split_sentences(text):
        if CANNOT_ONLY.search(s):
            continue
        for b, rx in _KW.items():
            if rx.search(s):
                found.add(b)
    if not found:
        return "none"
    if found == {tb}:
        return "match"
    return "review"      # 다른 묶음이 보이거나 여러 묶음 -> 사전으로 못 가름


# ---------------------------------------------------------------- 점수 (rules.md 4절)
def score(status, address, typ, truth):
    """느슨한·엄격한. 모름/미해결은 None. 엄격한: 영업 상태 맞음 + 말한 주소·업종이 있다면 모두 맞음."""
    if status in ("open", "closed"):
        lenient = (status == truth)
    else:
        lenient = None
    if lenient is None:
        strict = None
    elif lenient is False:
        strict = False
    else:
        parts = [address, typ]
        if "wrong" in parts:
            strict = False
        elif "review" in parts:
            strict = None
        else:
            strict = True
    return lenient, strict


# ---------------------------------------------------------------- LLM 보조 분류 인터페이스 (스텁: 호출하지 않는다)
LLM_LABEL_SCHEMA = {
    "key": "<system>|<qid>",
    "status": "open | closed | unknown",
    "stated_address": "답이 '대상 가게' 주소로 제시한 문자열, 없으면 null (다른 가게 주소만 있으면 null)",
    "stated_type": "한식|중식|일식|양식|분식|치킨호프주점|카페디저트|기타 중 하나, 업종을 말하지 않으면 null",
}


def build_llm_prompt(answer_text):
    """rules.md 1~3절 원문 + 답 하나. 정답은 넣지 않는다. 호출은 하지 않고 문자열만 만든다."""
    rules = C.RULES_MD.read_text(encoding="utf-8")
    sec = rules.split("## 4.")[0]
    return (sec + "\n\n---\n아래 답 하나만 위 규칙대로 분류하라. 정답은 모른다. JSON 한 줄로만 출력:\n"
            + json.dumps({k: v for k, v in LLM_LABEL_SCHEMA.items() if k != "key"}, ensure_ascii=False)
            + "\n\n답:\n" + answer_text)


def write_review_queue(rows, path):
    """review 가 하나라도 있는 답을 JSONL 로 쓴다. 정답 열은 일부러 넣지 않는다."""
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            need = [k for k in ("status", "address", "type") if r[k] == "review"]
            if need:
                f.write(json.dumps({"key": f'{r["system"]}|{r["qid"]}', "answer": r["_answer"], "need": need},
                                   ensure_ascii=False) + "\n")
                n += 1
    return n


def load_llm_labels(path):
    """LLM 보조 분류 결과 파일(JSONL, LLM_LABEL_SCHEMA). 없으면 {}."""
    p = Path(path)
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            out[d["key"]] = d
    return out


def _addr_from_stated(stated, truth_addr):
    if not stated:
        return "none"
    j = judge_address(stated, truth_addr)
    return "match" if j == "match" else "wrong"


STALE_LLM = []   # 답 해시가 달라 버린 LLM 라벨 키 (run_analysis 가 보고)


def judge_all(answers, store_by_id, llm_labels=None):
    """answers(load_data) -> 판정 행 list. llm_labels 가 있으면 review 항목에만 적용한다."""
    llm_labels = llm_labels or {}
    STALE_LLM.clear()
    rows = []
    for a in answers:
        st = store_by_id[a["item_id"]]
        status, why = classify_status(a["answer"])
        addr = judge_address(a["answer"], st["address"])
        typ = judge_type(a["answer"], st["biz_type"])
        src = "dict"
        lab = llm_labels.get(f'{a["system"]}|{a["qid"]}')
        if lab and lab.get("answer_sha1") and lab["answer_sha1"] != hashlib.sha1(a["answer"].encode("utf-8")).hexdigest():
            STALE_LLM.append(f'{a["system"]}|{a["qid"]}')      # 답이 재수집으로 바뀜: 낡은 라벨은 쓰지 않는다
            lab = None
        if lab:
            if status == "review" and lab.get("status") in ("open", "closed", "unknown"):
                status, src = lab["status"], "llm"
            if addr == "review":
                addr, src = _addr_from_stated(lab.get("stated_address"), st["address"]), "llm"
            if typ == "review":
                sb, tb = lab.get("stated_type"), truth_bundle(st["biz_type"])
                typ, src = ("none" if not sb else ("match" if sb == tb else "wrong")), "llm"
        lenient, strict = score(status, addr, typ, st["truth"])
        rows.append({"system": a["system"], "qid": a["qid"], "item_id": a["item_id"], "lang": a["lang"],
                     "status": status, "status_reason": why, "address": addr, "type": typ,
                     "judge_source": src, "correct_lenient": lenient, "correct_strict": strict,
                     "_answer": a["answer"]})
    return rows
