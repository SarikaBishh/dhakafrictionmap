"""Load, validate and reshape observations. Processed data is regenerable from raw."""
import pandas as pd
from analysis.config import INDICATORS
from analysis.validate_data import assert_valid


def load(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def clean(df):
    """Validate (raises on errors), then coerce types. Blank values become NaN, never 0."""
    report = assert_valid(df)
    out = df.copy()
    for c in ("latitude", "longitude"):
        out[c] = pd.to_numeric(out[c])
    out["indicator_value"] = pd.to_numeric(out["indicator_value"].replace("", pd.NA), errors="coerce")
    return out, report


def to_wide(df):
    """One row per location, one column per indicator (NaN where missing)."""
    idx = ["location_id", "location_name", "latitude", "longitude", "record_type"]
    wide = df.pivot(index=idx, columns="indicator_name", values="indicator_value")
    for i in INDICATORS:
        if i["key"] not in wide.columns:
            wide[i["key"]] = float("nan")
    return wide[[i["key"] for i in INDICATORS]].reset_index()
