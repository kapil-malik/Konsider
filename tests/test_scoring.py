from unittest import TestCase

from konsider.data_loader import load_project_data
from konsider.models import CountryMetric
from konsider.profiles import get_default_profile
from konsider.scoring import (
    ScoringError,
    build_ranking_table,
    get_country_breakdown,
    normalize_weights,
    rank_countries,
)


class ScoringTests(TestCase):
    def test_normalize_weights_sums_to_one(self):
        weights = normalize_weights({"tech_jobs": 3, "female_safety": 1})

        self.assertEqual(weights, {"female_safety": 0.25, "tech_jobs": 0.75})
        self.assertAlmostEqual(sum(weights.values()), 1.0)

    def test_normalize_weights_uses_equal_weights_when_all_zero(self):
        weights = normalize_weights({"tech_jobs": 0}, ["tech_jobs", "finance_jobs"])

        self.assertEqual(weights, {"finance_jobs": 0.5, "tech_jobs": 0.5})

    def test_rank_countries_orders_by_weighted_score(self):
        metrics = [
            CountryMetric("alpha", "tech_jobs", 9.0, "test", "2026-01-01", "test"),
            CountryMetric("alpha", "cost_of_living", 4.0, "test", "2026-01-01", "test"),
            CountryMetric("beta", "tech_jobs", 6.0, "test", "2026-01-01", "test"),
            CountryMetric("beta", "cost_of_living", 9.0, "test", "2026-01-01", "test"),
        ]

        rankings = rank_countries(metrics, {"tech_jobs": 3, "cost_of_living": 1})

        self.assertEqual([ranking.country_id for ranking in rankings], ["alpha", "beta"])
        self.assertAlmostEqual(rankings[0].total_score, 7.75)
        self.assertAlmostEqual(sum(item.contribution for item in rankings[0].contributions), 7.75)

    def test_rank_countries_rejects_unknown_weights(self):
        metrics = [CountryMetric("alpha", "tech_jobs", 9.0, "test", "2026-01-01", "test")]

        with self.assertRaisesRegex(ScoringError, "Unknown weight"):
            rank_countries(metrics, {"unknown": 1})

    def test_rank_real_dataset_with_default_style_profile(self):
        data = load_project_data()
        profile = get_default_profile("indian_tech_professional_with_teenage_child")
        rankings = rank_countries(data.metrics, profile.weights)

        self.assertEqual(len(rankings), 10)
        self.assertGreaterEqual(rankings[0].total_score, rankings[-1].total_score)
        self.assertTrue(all(ranking.contributions for ranking in rankings))

    def test_country_breakdown_orders_contributions_descending(self):
        metrics = [
            CountryMetric("alpha", "tech_jobs", 8.0, "test", "2026-01-01", "test"),
            CountryMetric("alpha", "cost_of_living", 4.0, "test", "2026-01-01", "test"),
            CountryMetric("beta", "tech_jobs", 1.0, "test", "2026-01-01", "test"),
            CountryMetric("beta", "cost_of_living", 1.0, "test", "2026-01-01", "test"),
        ]

        ranking = rank_countries(metrics, {"tech_jobs": 1, "cost_of_living": 1})[0]
        breakdown = get_country_breakdown(ranking)

        self.assertEqual([item.parameter_id for item in breakdown], ["tech_jobs", "cost_of_living"])
        self.assertGreaterEqual(breakdown[0].contribution, breakdown[1].contribution)

    def test_build_ranking_table_adds_country_names_and_signals(self):
        data = load_project_data()
        profile = get_default_profile("student_planning_higher_education")
        rankings = rank_countries(data.metrics, profile.weights)

        table = build_ranking_table(rankings, data.countries, signal_count=2)

        self.assertEqual(len(table), 10)
        self.assertEqual(table[0].rank, 1)
        self.assertTrue(table[0].country_name)
        self.assertEqual(len(table[0].top_strengths), 2)
        self.assertEqual(len(table[0].top_tradeoffs), 2)
