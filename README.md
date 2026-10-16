# Dhaka Friction Map

A decision-support prototype for exploring which selected locations in Dhaka might be investigated first for mobility improvements, using a transparent weighted score.

> **Status: prototype on SYNTHETIC data.** Nothing here is a finding about real roads. See `docs/sources.md` and `docs/limitations.md`.

**Research question:** if resources were limited, which locations should be investigated first, and what evidence supports that decision?

## Features
Overview, schematic map with detail panel, 2-4 location comparison (sortable table + Chart.js), Decision Lab (adjustable weights, live ranking, before/after rank, per-indicator contributions, sensitivity analysis, weight validation, reset), methodology page, CSV text export.

## Architecture
```
data/synthetic/*.csv -> analysis/validate_data -> clean_data -> calculate_scores -> data/processed/dataset.json -> frontend (ES modules)
```
Layout: `analysis/` (Python), `data/` (raw, synthetic, processed, dictionary), `frontend/` (index.html, css/, js/), `tests/` and `frontend/tests/`, `docs/`.

## Run
```
pip install -r requirements.txt
python -m analysis.generate_sample      # writes the synthetic CSV
python -m analysis.run_pipeline         # writes data/processed/
python -m http.server                   # then open http://localhost:8000/frontend/
```
Chart.js is loaded from a CDN (the table still works offline).

## Tests
```
python -m unittest discover -s tests -t .   # or: pytest
npm test                                    # Node >= 18, no dependencies
```
Last run in the build environment: 22 Python tests OK, 7 JS tests OK.

## Scoring
`PriorityScore_i = 100 * sum_j(w_j * n_ij)`; min-max normalisation with documented direction; missing indicators dropped and weights renormalised; ties share rank. Details: `docs/methodology.md`.

## Data
Observed, derived and synthetic records are distinguished by `record_type`. Candidate real sources and their status: `docs/sources.md`. Schema: `data/data_dictionary.md`.

## Future work
Real-data ingestion, Leaflet basemap when self-hosted, PDF/CSV download, Playwright tests, deployment (a `netlify.toml` is included but untested).
