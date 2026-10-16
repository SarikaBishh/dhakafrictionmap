# Data dictionary

Input: long-format CSV, one row per location x indicator x observation window.

| Column | Type | Meaning |
|---|---|---|
| location_id | text | Stable identifier |
| location_name | text | Display name |
| latitude, longitude | decimal degrees | WGS84; validated to -90..90 / -180..180 (warning outside Bangladesh) |
| indicator_name | text | One of: vehicle_count, nonmotor_share, lane_count, signal_density |
| indicator_value | number or blank | Blank only if data_quality_status = missing |
| unit | text | veh/hr, %, lanes, per km |
| observation_start, observation_end | date | end >= start |
| source_name, source_url | text | Provenance (synthetic rows say so) |
| sample_size | number or blank | Optional |
| data_quality_status | ok / missing / flagged | |
| record_type | observed / derived / synthetic | Never mix without labelling |

Duplicate key: (location_id, indicator_name, observation_start, observation_end).

Processed outputs (`data/processed/`): `dataset.json` (frontend input), `scores.csv`, `cleaning_report.md`.
