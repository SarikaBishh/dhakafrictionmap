"""End-to-end: synthetic CSV -> validate -> clean -> score -> data/processed/*."""
import json
import sys
from pathlib import Path
import pandas as pd
from analysis.config import INDICATORS, DIRECTIONS, DEFAULT_WEIGHTS, SCENARIOS
from analysis.clean_data import load, clean, to_wide
from analysis.calculate_scores import priority_scores, sensitivity


def run(src="data/synthetic/sample_observations.csv", out="data/processed"):
    df, report = clean(load(src))
    wide = to_wide(df)
    scored = priority_scores(wide, DEFAULT_WEIGHTS, DIRECTIONS)
    sens = sensitivity(wide, SCENARIOS, DIRECTIONS)
    meta = df.drop_duplicates("location_id").set_index("location_id")
    sites = []
    for _, r in scored.iterrows():
        m = meta.loc[r["location_id"]]
        sites.append({
            "id": r["location_id"], "name": r["location_name"], "lat": r["latitude"], "lon": r["longitude"],
            "record_type": r["record_type"], "period": f'{m["observation_start"]} to {m["observation_end"]}',
            "source": m["source_name"],
            "values": {i["key"]: (None if pd.isna(r[i["key"]]) else float(r[i["key"]])) for i in INDICATORS},
            "default_score": None if pd.isna(r["score"]) else float(r["score"]),
            "default_rank": None if pd.isna(r["rank"]) else int(r["rank"]),
        })
    dataset = {"indicators": INDICATORS, "scenarios": SCENARIOS, "sites": sites,
               "quality": {"errors": report["errors"], "warnings": report["warnings"]},
               "sensitivity": json.loads(sens.to_json(orient="records"))}
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / "dataset.json").write_text(json.dumps(dataset, indent=2))
    scored.to_csv(Path(out) / "scores.csv", index=False)
    desc = df.groupby("indicator_name")["indicator_value"].describe().to_string()
    (Path(out) / "cleaning_report.md").write_text(
        "# Cleaning report\n\nSource: `%s` (record_type: %s)\n\nRows: %d | Errors: %d | Warnings: %d\n\n"
        "## Warnings\n%s\n\n## Descriptive statistics\n```\n%s\n```\n" % (
            src, ", ".join(sorted(df["record_type"].unique())), len(df), len(report["errors"]),
            len(report["warnings"]), "\n".join(f"- {c}: {m}" for c, m in report["warnings"]) or "none", desc))
    return dataset


if __name__ == "__main__":
    d = run(*sys.argv[1:])
    print(f"processed {len(d['sites'])} locations")
