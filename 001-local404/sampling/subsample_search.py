"""검색 2조건(H-search, S-search)용 100곳 층화 무작위 부표본.

결정(2026-10-24, 결과 분석 전): 검색 한도 때문에 전수 수집이 35시간 이상 걸려 검색 2조건은 800곳 중 100곳 x 5언어로 줄인다.
- 입력: sampling/sample_v2.csv (읽기만 한다). 사전 등록 층 = 영업상태 x 카카오 등록 x 지역 (8층, 층마다 100곳).
- 배분: 층 비례 최대잉여법. 100/8 = 12.5 라 층마다 12곳 + 나머지 4곳을 더 배정한다. 영업 400 : 폐업 400 비율을 지키려고
  영업 4층에서 2곳, 폐업 4층에서 2곳에 나머지를 준다(동률은 시드로 가른다).
- 시드 20261024, 결정적: item_id 정렬 후 층별로 random.Random(seed)로 섞어 앞에서 n곳.
출력: sampling/subsample_search_v1.csv (item_id, stratum), sampling/subsample_search_v1.sha256
실행: python sampling/subsample_search.py   (파일이 이미 있으면 같은 결과인지 확인만 하고 덮어쓰지 않는다)
"""
import csv, hashlib, random, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SEED = 20261024
N = 100
SRC = HERE / "sample_v2.csv"
OUT = HERE / "subsample_search_v1.csv"
SHA = HERE / "subsample_search_v1.sha256"


def allocate(strata_sizes, n, rng):
    """strata_sizes: {stratum: 전체 곳 수}. 영업상태(층 이름 첫 칸)별로 나눠 최대잉여법. 반환 {stratum: 배정}."""
    total = sum(strata_sizes.values())
    groups = defaultdict(list)
    for s in sorted(strata_sizes):
        groups[s.split("|")[0]].append(s)
    alloc = {}
    quota_by_group = {}
    for g, ss in sorted(groups.items()):
        quota_by_group[g] = n * sum(strata_sizes[s] for s in ss) / total
    # 영업상태 그룹 몫이 정수가 아니면 그룹도 최대잉여법
    gfloor = {g: int(q) for g, q in quota_by_group.items()}
    left = n - sum(gfloor.values())
    order = sorted(quota_by_group, key=lambda g: (-(quota_by_group[g] - gfloor[g]), rng.random()))
    for g in order[:left]:
        gfloor[g] += 1
    for g, ss in sorted(groups.items()):
        gsize = sum(strata_sizes[s] for s in ss)
        q = {s: gfloor[g] * strata_sizes[s] / gsize for s in ss}
        fl = {s: int(q[s]) for s in ss}
        rest = gfloor[g] - sum(fl.values())
        tie = {s: rng.random() for s in ss}
        for s in sorted(ss, key=lambda s: (-(q[s] - fl[s]), tie[s]))[:rest]:
            fl[s] += 1
        alloc.update(fl)
    return alloc


def build():
    with open(SRC, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by = defaultdict(list)
    for r in rows:
        by[r["stratum"]].append(r["item_id"])
    rng = random.Random(SEED)
    alloc = allocate({s: len(v) for s, v in by.items()}, N, rng)
    chosen = []
    for s in sorted(by):
        ids = sorted(by[s])
        random.Random(f"{SEED}|{s}").shuffle(ids)
        chosen += [(i, s) for i in sorted(ids[:alloc[s]])]
    chosen.sort()
    assert len(chosen) == N and len({i for i, _ in chosen}) == N
    return rows, alloc, chosen


def render(chosen):
    return "item_id,stratum\n" + "".join(f"{i},{s}\n" for i, s in chosen)


def main():
    rows, alloc, chosen = build()
    text = render(chosen)
    if OUT.exists():
        if OUT.read_bytes() != text.encode("utf-8"):
            sys.exit("MISMATCH: existing subsample_search_v1.csv differs from the deterministic result")
        print("existing file reproduces exactly")
    else:
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        h = hashlib.sha256(OUT.read_bytes()).hexdigest()
        with open(SHA, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{h}  {OUT.name}\n")
    print("allocation:", alloc)
    ids = {i for i, _ in chosen}
    meta = {r["item_id"]: r for r in rows}
    for label, key in (("영업상태", lambda r: r["영업상태명"][:2]), ("업태(상위)", lambda r: r["업태구분명"]), ("시도", lambda r: r["시도"])):
        full, sub = Counter(key(r) for r in rows), Counter(key(meta[i]) for i in ids)
        print(label, {k: f"{sub.get(k,0)}/{v}" for k, v in full.most_common(8)})


if __name__ == "__main__":
    main()
