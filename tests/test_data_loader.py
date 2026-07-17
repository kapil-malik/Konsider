from pathlib import Path
from unittest import TestCase

from konsider.data_loader import DataValidationError, load_project_data


class DataLoaderTests(TestCase):
    def test_load_project_data_validates_complete_phase_1_dataset(self):
        data = load_project_data()

        self.assertEqual(len(data.countries), 10)
        self.assertEqual(len(data.parameters), 10)
        self.assertEqual(len(data.metrics), 100)
        self.assertEqual(set(data.evidence), set(data.countries))

    def test_metric_scores_are_normalized_to_one_to_ten(self):
        data = load_project_data()

        self.assertTrue(all(1 <= metric.score <= 10 for metric in data.metrics))

    def test_loader_rejects_missing_evidence(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)
            (data_dir / "countries.yml").write_text(
                '[{"id": "test_country", "name": "Test Country", "region": "Test"}]',
                encoding="utf-8",
            )
            (data_dir / "parameter_definitions.yml").write_text(
                """
    [
      {
        "id": "test_parameter",
        "name": "Test parameter",
        "category": "Test",
        "description": "Test parameter.",
        "higher_is_better": true
      }
    ]
    """.strip(),
                encoding="utf-8",
            )
            (data_dir / "country_metrics.csv").write_text(
                "\n".join(
                    [
                        "country_id,parameter_id,score,source,last_updated,notes",
                        "test_country,test_parameter,5,MVP-estimate,2026-01-01,Test notes",
                    ]
                ),
                encoding="utf-8",
            )
            (data_dir / "evidence").mkdir()

            with self.assertRaisesRegex(DataValidationError, "Missing evidence"):
                load_project_data(data_dir)
