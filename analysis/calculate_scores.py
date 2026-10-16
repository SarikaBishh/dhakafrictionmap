"""Transparent weighted scoring: Score_i = 100 * sum_j(w_j * n_ij), with missing-data renormalisation."""
import numpy as np
import pandas as pd
from analysis.config import SENSITIVE_RANK_RANGE


def validate_weights(weights, tol=1e-9):
    vals = list(weights.values())
    if any(pd.isna(v) for v in vals):
        raise ValueError("Weights must be numbers")
    if any(v < 0 for v in vals):
        raise ValueError("Weights must be non-negative")
    if abs(sum(vals) - 1) > tol:
        raise ValueError(f"Weights must sum to 1 (got {sum(vals)})")


def normalize(values, direction=1):
    """Min-max to [0,1]; direction=-1 flips. Identical values -> 0.5. NaN stays NaN."""
    s = pd.Series(values, dtype=float)
    mn, mx = s.min(), s.max()
    if s.notna().sum() == 0:
        return s
    n = pd.Series(0.5, index=s.index).where(s.notna()) if mx == mn else (s - mn) / (mx - mn)
    return n if direction > 0 else 1 - n


def priority_scores(wide, weights, directions):
    """Return wide with score, rank, complete, missing_indicators and contrib_* columns.

    Missing policy: an indicator with no value for a location is dropped for that
    location and the remaining (positive) weights are renormalised; the location is
    flagged incomplete. If nothing is usable the score is NaN.
    """
    validate_weights(weights)
    keys = list(weights)
    norm = pd.DataFrame({k: normalize(wide[k], directions[k]) for k in keys})
    res = wide.copy()
    scores, complete, missing = [], [], []
    contrib = {k: [] for k in keys}
    for i in norm.index:
        used = [k for k in keys if weights[k] > 0 and pd.notna(norm.at[i, k])]
        gaps = [k for k in keys if weights[k] > 0 and pd.isna(norm.at[i, k])]
        tw = sum(weights[k] for k in used)
        for k in keys:
            contrib[k].append(100 * weights[k] * norm.at[i, k] / tw if k in used and tw > 0 else 0.0)
        scores.append(100 * sum(weights[k] * norm.at[i, k] for k in used) / tw if tw > 0 else np.nan)
        complete.append(not gaps)
        missing.append(",".join(gaps))
    res["score"] = np.round(scores, 9)
    res["rank"] = res["score"].rank(method="min", ascending=False)  # ties share a rank; NaN unranked
    res["complete"] = complete
    res["missing_indicators"] = missing
    for k in keys:
        res[f"contrib_{k}"] = contrib[k]
    return res


def sensitivity(wide, scenarios, directions):
    """Ranks per scenario plus range; flags locations whose rank moves >= the cut-off."""
    ranks = pd.DataFrame({"location_id": wide["location_id"]})
    for name, w in scenarios.items():
        ranks[name] = priority_scores(wide, w, directions)["rank"].values
    cols = list(scenarios)
    ranks["rank_min"] = ranks[cols].min(axis=1)
    ranks["rank_max"] = ranks[cols].max(axis=1)
    ranks["rank_range"] = ranks["rank_max"] - ranks["rank_min"]
    ranks["sensitive"] = ranks["rank_range"] >= SENSITIVE_RANK_RANGE
    return ranks
