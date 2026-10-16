"""Write the clearly labelled SYNTHETIC sample used for development and demos."""
import csv
from pathlib import Path

SITES = [  # id, name, lat, lon, vehicle_count, nonmotor_share, lane_count, signal_density
    ("A", "Site A", 23.7509, 90.3935, 1850, 32, 2, 0.8),
    ("B", "Site B", 23.7808, 90.4167, 2400, 18, 4, 1.5),
    ("C", "Site C", 23.7104, 90.4074, 1200, 41, 2, None),
    ("D", "Site D", 23.8103, 90.4125, 3100, 12, 6, 2.2),
    ("E", "Site E", 23.7461, 90.3742, 900, 25, 2, 0.4),
    ("F", "Site F", 23.7925, 90.3680, 2000, 36, 4, 1.1),
]
UNITS = {"vehicle_count": "veh/hr", "nonmotor_share": "%", "lane_count": "lanes", "signal_density": "per km"}
COLS = ["location_id", "location_name", "latitude", "longitude", "indicator_name", "indicator_value", "unit",
        "observation_start", "observation_end", "source_name", "source_url", "sample_size",
        "data_quality_status", "record_type"]


def main(out="data/synthetic/sample_observations.csv"):
    rows = []
    for sid, name, lat, lon, *vals in SITES:
        for ind, v in zip(UNITS, vals):
            rows.append([sid, name, lat, lon, ind, "" if v is None else v, UNITS[ind],
                         "2026-01-01", "2026-01-07", "SYNTHETIC SAMPLE (invented)", "", "",
                         "missing" if v is None else "ok", "synthetic"])
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    print(f"wrote {main()} synthetic rows")
