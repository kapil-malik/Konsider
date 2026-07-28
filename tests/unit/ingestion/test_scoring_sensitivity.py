from unittest import TestCase

from konsider.ingestion.models import (
    MetricObservation,
    ObservationComponent,
    SourceRecordReference,
)
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
    def test_job_market_scoring_preserves_composite_and_reports_weight_sensitivity(self):
        rows = []
        for index, country in enumerate(("ALB", "CAN", "IND"), start=1):
            reference = SourceRecordReference("sha256:a", f"Sheet!{country}", f"{country}|2025")
            rows.append(
                MetricObservation(
                    f"obs-job-{country}",
                    country,
                    "overall_job_market_opportunity",
                    float(index * 2),
                    "equal_component_percentile_index_1_10",
                    "2025-01-01",
                    "2025-12-31",
                    "ilostat_job_market_opportunity",
                    ("sha256:a",),
                    (reference,),
                    "derived_composite_of_modelled_national_estimates",
                    "national",
                    "ilostat_job_market_opportunity_v1",
                    "ilostat_job_market_equal_component_percentiles_v1",
                    components=(
                        ObservationComponent(
                            "employment_to_population_ratio",
                            40 + index * 5,
                            "percent",
                            2025,
                            reference,
                        ),
                        ObservationComponent(
                            "labour_force_participation_rate",
                            50 + index * 6,
                            "percent",
                            2025,
                            reference,
                        ),
                        ObservationComponent(
                            "unemployment_rate",
                            12 - index * 2,
                            "percent",
                            2025,
                            reference,
                        ),
                    ),
                )
            )

        scores = score_observations(rows)
        report = sensitivity_experiments(rows)
        experiment = report["criteria"]["overall_job_market_opportunity"]["component_experiment"]

        self.assertEqual([item.score for item in scores], [2.0, 4.0, 6.0])
        self.assertTrue(
            all(
                item.method_version == "job_market_equal_component_percentiles_v1"
                for item in scores
            )
        )
        self.assertEqual(
            set(experiment["weight_sensitivity"]),
            {"equal_weight", "employment_heavy", "unemployment_heavy"},
        )
        self.assertEqual(len(experiment["component_removal_sensitivity"]), 3)

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
