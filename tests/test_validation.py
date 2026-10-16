import unittest
import pandas as pd
from analysis.clean_data import load, clean, to_wide
from analysis.validate_data import validate, check_columns, ValidationError


def base():
    return load("data/synthetic/sample_observations.csv")


def codes(df, kind="errors"):
    return {c for c, _ in validate(df)[kind]}


class TestValidation(unittest.TestCase):
    def test_clean_sample_has_no_errors(self):
        self.assertEqual(validate(base())["errors"], [])

    def test_missing_column(self):
        with self.assertRaises(ValidationError):
            check_columns(base().drop(columns=["unit"]))

    def test_duplicate_records(self):
        df = pd.concat([base(), base().iloc[[0]]], ignore_index=True)
        self.assertIn("duplicates", codes(df))

    def test_invalid_coordinates(self):
        df = base(); df.loc[0, "latitude"] = "123.0"
        self.assertIn("invalid_coordinates", codes(df))
        df.loc[0, "latitude"] = "abc"
        self.assertIn("invalid_coordinates", codes(df))

    def test_outside_bangladesh_is_warning(self):
        df = base(); df["latitude"] = "40.0"
        self.assertIn("outside_bangladesh", codes(df, "warnings"))

    def test_invalid_and_reversed_dates(self):
        df = base(); df.loc[0, "observation_start"] = "not-a-date"
        self.assertIn("invalid_dates", codes(df))
        df = base(); df.loc[0, "observation_end"] = "2025-01-01"
        self.assertIn("date_order", codes(df))

    def test_bad_values(self):
        df = base(); df.loc[0, "indicator_value"] = "abc"
        self.assertIn("non_numeric_value", codes(df))
        df = base(); df.loc[0, "indicator_value"] = "-5"
        self.assertIn("negative_value", codes(df))

    def test_undeclared_blank_is_error(self):
        df = base(); df.loc[0, "indicator_value"] = ""
        self.assertIn("undeclared_missing", codes(df))

    def test_missing_stays_nan_not_zero(self):
        df, _ = clean(base())
        wide = to_wide(df)
        self.assertTrue(pd.isna(wide.loc[wide.location_id == "C", "signal_density"]).all())

    def test_outliers_flagged_not_removed(self):
        df = base()
        extra = df[df.indicator_name == "vehicle_count"].copy()
        extra["location_id"] = ["X1", "X2", "X3", "X4", "X5", "X6"]
        extra["indicator_value"] = ["1000", "1010", "990", "1005", "995", "90000"]
        df2 = pd.concat([df, extra], ignore_index=True)
        self.assertIn("outlier_flag", codes(df2, "warnings"))
        cleaned, _ = clean(df2)
        self.assertEqual(len(cleaned), len(df2))


if __name__ == "__main__":
    unittest.main()
