"""Validation of long-format observation data. Reports problems; never deletes rows."""
import pandas as pd
from analysis.config import REQUIRED_COLUMNS, RECORD_TYPES, QUALITY_STATUSES, BD_BBOX

KEY = ["location_id", "indicator_name", "observation_start", "observation_end"]


class ValidationError(Exception):
    pass


def check_columns(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValidationError(f"Missing required columns: {missing}")


def validate(df):
    """Return {'errors': [...], 'warnings': [...]} of (code, message) tuples."""
    check_columns(df)
    errors, warnings = [], []
    if df.empty:
        errors.append(("empty", "Dataset has no rows"))
        return {"errors": errors, "warnings": warnings}

    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    bad = df[lat.isna() | lon.isna() | ~lat.between(-90, 90) | ~lon.between(-180, 180)]
    if len(bad):
        errors.append(("invalid_coordinates", f"{len(bad)} row(s) with invalid coordinates"))
    out = ~lat.between(*BD_BBOX["lat"]) | ~lon.between(*BD_BBOX["lon"])
    if (out & ~df.index.isin(bad.index)).any():
        warnings.append(("outside_bangladesh", "Some coordinates fall outside Bangladesh's bounding box"))

    start = pd.to_datetime(df["observation_start"], errors="coerce")
    end = pd.to_datetime(df["observation_end"], errors="coerce")
    if (start.isna() | end.isna()).any():
        errors.append(("invalid_dates", "Unparseable observation dates"))
    elif (end < start).any():
        errors.append(("date_order", "observation_end precedes observation_start"))

    val_str = df["indicator_value"].astype(str).str.strip()
    blank = val_str.isin(["", "nan", "None"])
    num = pd.to_numeric(val_str.where(~blank), errors="coerce")
    if (num.isna() & ~blank).any():
        errors.append(("non_numeric_value", "Non-numeric indicator_value present"))
    if (num < 0).any():
        errors.append(("negative_value", "Negative indicator_value present"))
    pct = df["unit"].astype(str).str.strip() == "%"
    if (num[pct] > 100).any():
        errors.append(("percent_over_100", "Percentage value above 100"))
    undeclared = blank & (df["data_quality_status"] != "missing")
    if undeclared.any():
        errors.append(("undeclared_missing", "Blank value not marked data_quality_status='missing'"))

    if df.duplicated(subset=KEY).any():
        errors.append(("duplicates", f"{int(df.duplicated(subset=KEY).sum())} duplicate record(s)"))
    if not df["record_type"].isin(RECORD_TYPES).all():
        errors.append(("invalid_record_type", f"record_type must be one of {sorted(RECORD_TYPES)}"))
    if not df["data_quality_status"].isin(QUALITY_STATUSES).all():
        errors.append(("invalid_quality_status", f"data_quality_status must be one of {sorted(QUALITY_STATUSES)}"))
    if blank.any():
        warnings.append(("missing_values", f"{int(blank.sum())} missing value(s); never treated as zero"))
    warnings.extend(flag_outliers(df.assign(_v=num)))
    return {"errors": errors, "warnings": warnings}


def flag_outliers(df, k=1.5):
    """IQR-based flags per indicator. Flags only; nothing is removed."""
    out = []
    for name, g in df.groupby("indicator_name"):
        v = g["_v"].dropna()
        if len(v) < 4:
            continue
        q1, q3 = v.quantile([.25, .75])
        iqr = q3 - q1
        n = int(((v < q1 - k * iqr) | (v > q3 + k * iqr)).sum())
        if n:
            out.append(("outlier_flag", f"{name}: {n} value(s) outside {k}*IQR (flagged, retained)"))
    return out


def assert_valid(df):
    r = validate(df)
    if r["errors"]:
        raise ValidationError("; ".join(m for _, m in r["errors"]))
    return r
