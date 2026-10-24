"""(c) 통계 도구. numpy/scipy 만 쓴다 (statsmodels 없이).

- 군집(가게 단위) 로버스트 표준오차: 비율/평균의 비(ratio) 추정량 + CR1 소표본 보정 G/(G-1).
- 두 독립 군집 표본 비율 차이, 짝 차이, Wilson·Clopper-Pearson 구간.
- Holm 보정.
- 임의절편 로지스틱(혼합효과 로지스틱): Gauss-Hermite 구적 최대우도. 가게 = 군집.
"""
import math
from dataclasses import dataclass

import numpy as np
from scipy import optimize, stats
from scipy.special import expit, logsumexp


# ------------------------------------------------------------------ 군집 로버스트 평균
@dataclass
class ClusterMean:
    mean: float
    se: float
    n: int
    g: int


def cluster_mean(y, cluster):
    """평균 y.mean() 의 군집 로버스트 SE. 군집이 1개면 se=nan."""
    y = np.asarray(y, float)
    cl = np.asarray(cluster)
    n = len(y)
    if n == 0:
        return ClusterMean(float("nan"), float("nan"), 0, 0)
    m = y.mean()
    _, inv = np.unique(cl, return_inverse=True)
    g = inv.max() + 1
    s = np.bincount(inv, weights=y - m, minlength=g)
    if g < 2:
        return ClusterMean(m, float("nan"), n, g)
    var = (g / (g - 1)) * np.sum(s ** 2) / n ** 2
    return ClusterMean(m, math.sqrt(var), n, g)


def _norm_p(z):
    return float(2 * stats.norm.sf(abs(z)))


def diff_independent(yA, clA, yB, clB, alpha=0.05):
    """A 평균 - B 평균 (서로 다른 군집 집합). 정규근사. 반환 dict.
    p_two: 양측, p_greater: H1(A>B) 방향 단측."""
    a, b = cluster_mean(yA, clA), cluster_mean(yB, clB)
    d = a.mean - b.mean
    se = math.sqrt(a.se ** 2 + b.se ** 2) if not (math.isnan(a.se) or math.isnan(b.se)) else float("nan")
    return _wald(d, se, alpha, extra={"mean_a": a.mean, "n_a": a.n, "g_a": a.g, "se_a": a.se,
                                      "mean_b": b.mean, "n_b": b.n, "g_b": b.g, "se_b": b.se})


def mean_with_ci(y, cluster, alpha=0.05):
    r = cluster_mean(y, cluster)
    z = stats.norm.ppf(1 - alpha / 2)
    lo = max(0.0, r.mean - z * r.se) if not math.isnan(r.se) else float("nan")
    hi = min(1.0, r.mean + z * r.se) if not math.isnan(r.se) else float("nan")
    return {"mean": r.mean, "se": r.se, "ci_lo": lo, "ci_hi": hi, "n": r.n, "g": r.g}


def paired_cluster_diff(d, cluster, alpha=0.05):
    """짝 차이 d 의 평균과 군집 로버스트 CI. 기대 방향 검정용 p_less/p_greater 포함."""
    r = cluster_mean(d, cluster)
    return _wald(r.mean, r.se, alpha, extra={"n": r.n, "g": r.g})


def _wald(est, se, alpha, extra=None):
    out = dict(extra or {})
    z = stats.norm.ppf(1 - alpha / 2)
    out.update(est=est, se=se)
    if se is None or math.isnan(se) or se == 0:
        # 분산 0 이면(예: 두 칸 모두 0%) 검정 불가로 표시한다. 지어내지 않는다.
        out.update(ci_lo=float("nan") if se is None or math.isnan(se) else est, ci_hi=float("nan") if se is None or math.isnan(se) else est,
                   z=float("nan"), p_two=float("nan"), p_greater=float("nan"), p_less=float("nan"),
                   note="se=0 or undefined: test not computed")
        return out
    zs = est / se
    out.update(ci_lo=est - z * se, ci_hi=est + z * se, z=zs, p_two=_norm_p(zs),
               p_greater=float(stats.norm.sf(zs)), p_less=float(stats.norm.cdf(zs)))
    return out


# ------------------------------------------------------------------ 이항 구간
def wilson(k, n, alpha=0.05):
    if n == 0:
        return float("nan"), float("nan")
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return float("nan"), float("nan")
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def clopper_pearson_lower_onesided(k, n, alpha=0.05):
    if n == 0 or k == 0:
        return 0.0
    return float(stats.beta.ppf(alpha, k, n - k + 1))


# ------------------------------------------------------------------ Holm
def holm(pvals):
    """Holm-Bonferroni 보정 p. nan 은 그대로 nan 으로 두고 순위에서 뺀다."""
    p = np.asarray(pvals, float)
    out = np.full_like(p, np.nan)
    idx = [i for i in range(len(p)) if not np.isnan(p[i])]
    order = sorted(idx, key=lambda i: p[i])
    m = len(order)
    run = 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, (m - rank) * p[i])
        run = max(run, adj)
        out[i] = run
    return out


# ------------------------------------------------------------------ 임의절편 로지스틱 (Gauss-Hermite ML)
@dataclass
class GLMMResult:
    ok: bool
    names: list
    beta: np.ndarray
    se: np.ndarray
    sigma: float
    loglik: float
    n: int
    g: int
    events: int
    note: str = ""
    converged: bool = False

    def table(self, alpha=0.05):
        z = stats.norm.ppf(1 - alpha / 2)
        rows = []
        ex = lambda v: float(math.exp(max(min(v, 700.0), -700.0)))
        for nm, b, s in zip(self.names, self.beta, self.se):
            zz = b / s if (s and not math.isnan(s) and not math.isnan(b)) else float("nan")
            rows.append({"term": nm, "coef": float(b), "se": float(s), "z": float(zz),
                         "p_two": _norm_p(zz) if not math.isnan(zz) else float("nan"),
                         "p_less": float(stats.norm.cdf(zz)) if not math.isnan(zz) else float("nan"),
                         "odds_ratio": ex(b),
                         "or_ci_lo": ex(b - z * s) if not math.isnan(s) else float("nan"),
                         "or_ci_hi": ex(b + z * s) if not math.isnan(s) else float("nan")})
        return rows


def _negll(theta, X, y, inv, g, nodes, logw):
    p = X.shape[1]
    beta, log_s = theta[:p], theta[p]
    s = math.exp(log_s)
    eta = X @ beta
    # 각 노드에서 행별 로그우도 -> 군집별 합
    eta_k = eta[:, None] + s * nodes[None, :]
    ll = y[:, None] * eta_k - np.logaddexp(0.0, eta_k)
    ll_g = np.zeros((g, len(nodes)))
    np.add.at(ll_g, inv, ll)
    return -float(np.sum(logsumexp(ll_g + logw[None, :], axis=1)))


def _num_hess(f, x, eps=1e-4):
    k = len(x)
    H = np.zeros((k, k))
    f0 = f(x)
    for i in range(k):
        for j in range(i, k):
            ei = np.zeros(k); ej = np.zeros(k)
            ei[i] = eps; ej[j] = eps
            v = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * eps * eps)
            H[i, j] = H[j, i] = v
    return H


def fit_glmm_logit(X, y, cluster, names, n_nodes=25):
    """y ~ X (절편 열 포함) + (1 | cluster). ML 은 Gauss-Hermite 구적(비적응형, n_nodes개).
    추정 불가(사건 0건·전부 사건·열 부족)면 ok=False 와 이유를 돌려준다."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n = len(y)
    _, inv = np.unique(np.asarray(cluster), return_inverse=True)
    g = int(inv.max() + 1) if n else 0
    ev = int(y.sum()) if n else 0
    names = list(names)
    nan = np.full(len(names), np.nan)
    if n == 0 or ev == 0 or ev == n:
        return GLMMResult(False, names, nan, nan, float("nan"), float("nan"), n, g, ev, "no variation in outcome (events=%d of %d)" % (ev, n))
    # 상수 열(절편 제외)·완전 공선 열 제거
    keep = [0] if names[0].lower() in ("intercept", "const") else []
    for j in range(len(names)):
        if j in keep:
            continue
        if np.ptp(X[:, j]) == 0:
            continue
        trial = X[:, keep + [j]]
        if np.linalg.matrix_rank(trial) == len(keep) + 1:
            keep.append(j)
    dropped = [names[j] for j in range(len(names)) if j not in keep]
    Xk = X[:, keep]
    kn = [names[j] for j in keep]
    nodes, w = np.polynomial.hermite_e.hermegauss(n_nodes)   # weight exp(-x^2/2)
    logw = np.log(w / math.sqrt(2 * math.pi))
    p = Xk.shape[1]
    f = lambda th: _negll(th, Xk, y, inv, g, nodes, logw)
    best = None
    for s0 in (0.5, 1.5):
        th0 = np.zeros(p + 1)
        th0[0] = math.log(max(ev, 1) / max(n - ev, 1))
        th0[p] = math.log(s0)
        res = optimize.minimize(f, th0, method="L-BFGS-B",
                                bounds=[(-30, 30)] * p + [(-6.0, 3.0)])
        if best is None or res.fun < best.fun:
            best = res
    th = best.x
    note = ""
    if dropped:
        note += "dropped constant/collinear columns: %s. " % dropped
    if th[p] <= -5.9:
        note += "random-intercept variance at lower bound (sigma~0). "
    if np.max(np.abs(th[:p])) > 15:
        note += "very large coefficient: possible (quasi-)separation. "
    try:
        H = _num_hess(f, th)
        cov = np.linalg.inv(H)
        dg = np.diag(cov)
        if not np.all(np.isfinite(dg)) or np.any(dg <= 0):
            raise np.linalg.LinAlgError("non-PD")
        se = np.sqrt(dg)[:p]
    except np.linalg.LinAlgError:
        # sigma 가 경계에 붙은 경우: 고정효과 부분만 따로 헤시안
        try:
            f2 = lambda b: f(np.append(b, th[p]))
            H2 = _num_hess(f2, th[:p])
            dg2 = np.diag(np.linalg.inv(H2))
            if not np.all(np.isfinite(dg2)) or np.any(dg2 <= 0):
                raise np.linalg.LinAlgError("non-PD")
            se = np.sqrt(dg2)
            note += "SE from fixed-effects block only. "
        except Exception:
            se = np.full(p, np.nan)
            note += "SE not computable (likely separation / too few events). "
    beta_full = np.full(len(names), np.nan); se_full = np.full(len(names), np.nan)
    for a, j in enumerate(keep):
        beta_full[j] = th[a]; se_full[j] = se[a]
    return GLMMResult(True, names, beta_full, se_full, float(math.exp(th[p])), float(-best.fun), n, g, ev,
                      note.strip(), bool(best.success))
