"""Shared configuration: schema, indicators, weighting scenarios.

Weights are fractions that sum to 1. They are user-selected assumptions,
not empirically derived values.
"""
REQUIRED_COLUMNS = [
    "location_id", "location_name", "latitude", "longitude", "indicator_name",
    "indicator_value", "unit", "observation_start", "observation_end",
    "source_name", "source_url", "sample_size", "data_quality_status", "record_type",
]
RECORD_TYPES = {"observed", "derived", "synthetic"}
QUALITY_STATUSES = {"ok", "missing", "flagged"}
# Rough bounding box of Bangladesh, used for a plausibility warning only.
BD_BBOX = {"lat": (20.5, 26.7), "lon": (88.0, 92.7)}

# direction: +1 = higher value -> higher priority; -1 = lower value -> higher priority.
INDICATORS = [
    {"key": "vehicle_count", "label": "Vehicle count", "unit": "veh/hr", "direction": 1,
     "default_weight": 0.35, "note": "short-duration count; more traffic is not automatically worse"},
    {"key": "nonmotor_share", "label": "Non-motorised share", "unit": "%", "direction": 1,
     "default_weight": 0.25, "note": "higher share = more mixed traffic"},
    {"key": "lane_count", "label": "Lane count", "unit": "lanes", "direction": -1,
     "default_weight": 0.20, "note": "fewer lanes = less capacity"},
    {"key": "signal_density", "label": "Signal density", "unit": "per km", "direction": -1,
     "default_weight": 0.20, "note": "fewer signals = less control"},
]
DIRECTIONS = {i["key"]: i["direction"] for i in INDICATORS}
DEFAULT_WEIGHTS = {i["key"]: i["default_weight"] for i in INDICATORS}
SCENARIOS = {
    "Default": DEFAULT_WEIGHTS,
    "Equal": {k: 0.25 for k in DEFAULT_WEIGHTS},
    "Traffic-heavy": {"vehicle_count": 0.6, "nonmotor_share": 0.2, "lane_count": 0.1, "signal_density": 0.1},
    "Infrastructure-heavy": {"vehicle_count": 0.1, "nonmotor_share": 0.2, "lane_count": 0.35, "signal_density": 0.35},
}
SENSITIVE_RANK_RANGE = 2  # arbitrary, documented cut-off
