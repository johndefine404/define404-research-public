"""통계 도구 자체 점검. 모델·검색을 부르지 않는다. 실행: python analysis/tests/test_stats_lib.py
결과 데이터가 아니라 '알려진 답이 있는 장난감 입력'만 쓴다 (분석 결과에 섞이지 않는다)."""
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

import stats_lib as S
import human_sample as H


def test_holm():
    # 교과서 예: p = .01, .04, .03, .005 (m=4) -> 정렬 .005,.01,.03,.04 -> 보정 .02,.03,.06,.06
    adj = S.holm([0.01, 0.04, 0.03, 0.005])
    assert np.allclose(adj, [0.03, 0.06, 0.06, 0.02]), adj
    assert math.isnan(S.holm([0.01, float("nan")])[1])


def test_cluster_mean_matches_simple_when_singletons():
    y = np.array([1, 0, 1, 1, 0, 0, 1, 0], float)
    r = S.cluster_mean(y, np.arange(8))
    n = len(y)
    assert abs(r.mean - 0.5) < 1e-12
    # 군집 크기 1이면 CR1 = (n/(n-1)) * p(1-p)/n
    want = math.sqrt(n / (n - 1) * 0.25 / n)
    assert abs(r.se - want) < 1e-12, (r.se, want)


def test_cluster_inflates_se():
    # 가게마다 두 답이 완전히 같으면 군집 SE 가 독립 가정보다 커야 한다
    base = np.array([1, 0, 1, 0, 1, 0, 0, 0, 1, 1], float)
    y = np.repeat(base, 2)
    cl = np.repeat(np.arange(10), 2)
    se_c = S.cluster_mean(y, cl).se
    se_i = S.cluster_mean(y, np.arange(20)).se
    assert se_c > 1.3 * se_i


def test_wilson_cp():
    lo, hi = S.wilson(0, 10)
    assert lo == 0 and 0.25 < hi < 0.31          # 알려진 값 약 0.278
    lo, hi = S.clopper_pearson(5, 10)
    assert abs(lo - 0.1871) < 1e-3 and abs(hi - 0.8129) < 1e-3
    from scipy import optimize, stats as st
    root = optimize.brentq(lambda q: st.binom.sf(2, 20, q) - 0.05, 1e-6, 0.5)   # P(X>=3 | q)=.05
    assert abs(S.clopper_pearson_lower_onesided(3, 20) - root) < 1e-6


def test_diff_independent():
    rng = np.random.default_rng(1)
    a = (rng.random(400) < 0.30).astype(float)
    b = (rng.random(400) < 0.10).astype(float)
    r = S.diff_independent(a, np.arange(400), b, np.arange(400, 800))
    assert 0.12 < r["est"] < 0.28 and r["p_two"] < 1e-6 and r["ci_lo"] > 0


def test_glmm_recovers_parameters():
    rng = np.random.default_rng(7)
    G, m = 600, 4
    sig, b0, b1 = 1.0, -0.5, 0.8
    cl = np.repeat(np.arange(G), m)
    x = rng.normal(size=G * m)
    u = rng.normal(0, sig, G)[cl]
    y = (rng.random(G * m) < S.expit(b0 + b1 * x + u)).astype(float)
    X = np.column_stack([np.ones_like(x), x])
    r = S.fit_glmm_logit(X, y, cl, ["Intercept", "x"])
    assert r.ok and r.converged
    assert abs(r.beta[0] - b0) < 0.2 and abs(r.beta[1] - b1) < 0.2, r.beta
    assert abs(r.sigma - sig) < 0.25, r.sigma
    assert all(np.isfinite(r.se)) and r.se[1] < 0.1


def test_glmm_degenerate():
    X = np.ones((10, 1))
    r = S.fit_glmm_logit(X, np.zeros(10), np.arange(10), ["Intercept"])
    assert not r.ok and "no variation" in r.note


def test_glmm_vs_statsmodels_optional():
    try:
        import statsmodels.api as sm
    except Exception:
        print("  (statsmodels 없음: 교차 검증 건너뜀)")
        return
    rng = np.random.default_rng(3)
    n = 3000
    x = rng.normal(size=n)
    y = (rng.random(n) < S.expit(-0.3 + 0.7 * x)).astype(float)
    X = np.column_stack([np.ones(n), x])
    r = S.fit_glmm_logit(X, y, np.arange(n), ["Intercept", "x"])   # 군집 크기 1 -> 임의절편은 거의 0
    m = sm.Logit(y, X).fit(disp=0)
    assert np.allclose(r.beta, m.params, atol=0.08), (r.beta, m.params)


def test_kappa():
    # 완전 일치 -> 1, 우연 수준 -> 0 근처, 알려진 예
    assert H.cohen_kappa(list("aabb"), list("aabb")) == 1.0
    a = ["y"] * 20 + ["y"] * 5 + ["n"] * 10 + ["n"] * 15
    b = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15
    k = H.cohen_kappa(a, b)            # po=.7, pe=.5*.5+.5*.5=.5 -> .4
    assert abs(k - 0.4) < 1e-9, k
    assert math.isnan(H.cohen_kappa(list("aaaa"), list("aaaa")))   # 한 범주뿐이면 정의 안 됨


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok ", name)
    print("all passed")
