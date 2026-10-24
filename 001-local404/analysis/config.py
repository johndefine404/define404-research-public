"""경로·상수. 사전 등록(prereg.md)과 판정 규칙(judge/rules.md)에서 온 값은 출처를 적는다."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # 저장소에 __pycache__ 를 남기지 않는다

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # 001-local404/
COLLECT = ROOT / "collect"
SAMPLE_CSV = ROOT / "sampling" / "sample_v2.csv"   # prereg 3절
RULES_MD = ROOT / "judge" / "rules.md"

LANGS = ["ko", "en", "ja", "zh", "vi"]            # prereg 4절
# 분석 대상 시스템. 키 = 분석 코드, 값 = (조건, 원본 배치 접두어)
#   S-search / H-search / H-mem: prereg 5절.
#   L-mem: prereg 의 W-mem 을 같은 모델 가중치의 로컬 Ollama 실행으로 바꾼 것 (HANDOFF 7절 1번, 확인 필요).
SYSTEMS = {
    "S-search": {"cond": "search", "batch_prefix": "S-search"},
    "H-search": {"cond": "search", "batch_prefix": "H-search"},
    "H-mem":    {"cond": "mem",    "batch_prefix": "H-mem"},
    "L-mem":    {"cond": "mem",    "batch_prefix": "W-mem"},   # L-mem 문항 배치는 W-mem 배치 파일을 그대로 쓴다 (run_lmem.py)
}
EXPLORATORY_ONLY = ["W-mem"]   # HANDOFF 7절·3절: Workers AI 답은 탐색 비교용. 확증 분석에서 제외.

MEASURE_DATE = "2026-10-21"    # sample_v2.csv 측정일
SEED = 20261021                # prereg 3절 시드, judge/rules.md 5절 사람 판정 표본 시드
HUMAN_SAMPLE_N = 200           # judge/rules.md 5절
MIN_CELL_N = 40                # prereg 7절: 표본 40 미만 칸은 해석하지 않는다
ALPHA = 0.05

# 검색 2조건 부표본 (HANDOFF 7절 5번, DEVIATIONS.md): 결과 분석 전 결정(2026-10-24).
# 검색 한도로 전수 수집이 35시간 이상 걸려 H-search·S-search 는 100곳 x 5언어(층화 무작위, 시드 20261024)만 받는다.
# 이 시스템들의 기대 문항·확증 분석은 부표본 가게로 한정한다. H-mem·L-mem 은 800곳 전부.
SUBSAMPLE_CSV = ROOT / "sampling" / "subsample_search_v1.csv"
SUBSAMPLE_SYSTEMS = ["H-search", "S-search"]
