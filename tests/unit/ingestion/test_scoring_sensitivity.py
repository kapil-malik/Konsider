from unittest import TestCase

from konsider.ingestion.models import MetricObservation, SourceRecordReference
from konsider.ingestion.scoring import score_observations, sensitivity_experiments


def observation(country, value):
    return MetricObservation(
        f"obs-{country}",
        country,
        "women_peace_security_index",
        value,
        "index_0_1",
        "2025-01-01",
        "2025-12-31",
        "wps_index",
        ("sha256:a",),
        (SourceRecordReference("sha256:a", f"Sheet!{country}"),),
        "composite",
        "national",
        "wps_index_v2",
        "wps_index_observation_v2",
        ("mixed_reference_years", "independent_composite", "possible_underlying_imputation"),
    )


class ScoringSensitivityTests(TestCase):
    def test_fixed_thresholds_do_not_exaggerate_tight_cluster(self):
        scores = score_observations([observation("IND", 0.800), observation("CAN", 0.801)])
        self.assertLess(
            max(item.score for item in scores) - min(item.score for item in scores), 0.1
        )

    def test_experiment_compares_all_three_methods(self):
        report = sensitivity_experiments([observation("IND", 0.7), observation("CAN", 0.8)])
        result = report["criteria"]["women_peace_security_index"]
        self.assertEqual(
            set(result["score_ranges"]), {"winsorized_minmax", "percentile_rank", "threshold"}
        )
        self.assertIn("tight_cluster_test_score_spread", result)
        self.assertEqual(
            result["country_set_test"]["scenario"],
            "remove one minimum and one maximum raw observation",
        )
