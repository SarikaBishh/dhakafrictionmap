import unittest
import numpy as np
import pandas as pd
from analysis.config import DIRECTIONS, DEFAULT_WEIGHTS, SCENARIOS
from analysis.calculate_scores import validate_weights, normalize, priority_scores, sensitivity


def wide(rows):
    return pd.DataFrame(rows, columns=["location_id", "vehicle_count", "nonmotor_share", "lane_count", "signal_density"])


class TestScores(unittest.TestCase):
    def test_negative_weight(self):
        with self.assertRaises(ValueError):
            validate_weights({"a": -0.1, "b": 1.1})

    def test_weights_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            validate_weights({"a": 0.5, "b": 0.4})
        validate_weights({"a": 0.5, "b": 0.5})

    def test_normalize_known_example(self):
        self.assertEqual(normalize([0, 5, 10], 1).tolist(), [0.0, 0.5, 1.0])
        self.assertEqual(normalize([0, 5, 10], -1).tolist(), [1.0, 0.5, 0.0])

    def test_identical_values(self):
        self.assertEqual(normalize([7, 7, 7], 1).tolist(), [0.5, 0.5, 0.5])

    def test_nan_preserved(self):
        self.assertTrue(np.isnan(normalize([1, np.nan, 3], 1)[1]))

    def test_manual_score(self):
        w = wide([["A", 0, 0, 2, 0], ["B", 10, 100, 6, 2]])
        r = priority_scores(w, DEFAULT_WEIGHTS, DIRECTIONS).set_index("location_id")
        # B: traffic 1, nonmotor 1, lanes(6 high -> 0), signals(high -> 0) => 100*(.35+.25)=60
        self.assertAlmostEqual(r.loc["B", "score"], 60.0)
        # A: only lanes and signals contribute fully => 100*(.20+.20)=40
        self.assertAlmostEqual(r.loc["A", "score"], 40.0)

    def test_score_bounds_and_contributions(self):
        w = wide([["A", 1, 5, 2, 0.1], ["B", 9, 1, 6, 2], ["C", 4, 4, 3, 1]])
        r = priority_scores(w, DEFAULT_WEIGHTS, DIRECTIONS)
        self.assertTrue(r.score.between(0, 100).all())
        contrib = r[[c for c in r.columns if c.startswith("contrib_")]].sum(axis=1)
        np.testing.assert_allclose(contrib, r.score, atol=1e-6)

    def test_missing_indicator_renormalises_and_flags(self):
        w = wide([["A", 0, 0, 2, 0], ["B", 10, 100, 6, np.nan], ["C", 5, 50, 4, 1]])
        r = priority_scores(w, DEFAULT_WEIGHTS, DIRECTIONS).set_index("location_id")
        self.assertFalse(r.loc["B", "complete"])
        self.assertEqual(r.loc["B", "missing_indicators"], "signal_density")
        self.assertAlmostEqual(r.loc["B", "score"], 100 * (.35 + .25) / .8)  # signal weight dropped
        self.assertTrue(r.loc["A", "complete"])

    def test_all_missing_gives_nan_not_zero(self):
        w = wide([["A", np.nan, np.nan, np.nan, np.nan], ["B", 1, 1, 1, 1], ["C", 2, 2, 2, 2]])
        r = priority_scores(w, DEFAULT_WEIGHTS, DIRECTIONS).set_index("location_id")
        self.assertTrue(np.isnan(r.loc["A", "score"]))
        self.assertTrue(np.isnan(r.loc["A", "rank"]))

    def test_tied_rankings_share_rank(self):
        w = wide([["A", 1, 1, 1, 1], ["B", 1, 1, 1, 1], ["C", 9, 9, 1, 1]])
        r = priority_scores(w, DEFAULT_WEIGHTS, DIRECTIONS).set_index("location_id")
        self.assertEqual(r.loc["A", "rank"], r.loc["B", "rank"])
        self.assertEqual(r.loc["C", "rank"], 1)
        self.assertEqual(r.loc["A", "rank"], 2)

    def test_sensitivity_range_and_flag(self):
        w = wide([["A", 10, 90, 6, 2], ["B", 0, 0, 2, 0], ["C", 5, 50, 4, 1], ["D", 3, 80, 2, 2]])
        s = sensitivity(w, SCENARIOS, DIRECTIONS)
        self.assertTrue((s.rank_range == s.rank_max - s.rank_min).all())
        self.assertTrue((s.sensitive == (s.rank_range >= 2)).all())

    def test_sensitivity_reproducible(self):
        w = wide([["A", 10, 90, 6, 2], ["B", 0, 0, 2, 0], ["C", 5, 50, 4, 1]])
        pd.testing.assert_frame_equal(sensitivity(w, SCENARIOS, DIRECTIONS), sensitivity(w, SCENARIOS, DIRECTIONS))


if __name__ == "__main__":
    unittest.main()
