import io
import json
from importlib.util import find_spec
from unittest import TestCase, skipUnless

from konsider.research.probe_adapters import (
    HciPlusStataAdapter,
    WorldBankMultiIndicatorJsonAdapter,
)
from konsider.research.probe_models import ArtifactInput


def _world_bank_artifact(artifact_id, url, indicator, observations):
    rows = [
        {
            "indicator": {"id": indicator, "value": indicator},
            "country": {"id": code, "value": name},
            "countryiso3code": code,
            "date": str(year),
            "value": value,
        }
        for code, name, year, value in observations
    ]
    return ArtifactInput(
        artifact_id=artifact_id,
        requested_url=url,
        body=json.dumps([{"page": 1}, rows]).encode(),
    )


class WorldBankMultiIndicatorJsonAdapterTests(TestCase):
    def test_combines_components_and_uses_oldest_latest_year_for_freshness(self):
        artifacts = (
            _world_bank_artifact(
                "a",
                "https://example.test/inflation",
                "INFLATION",
                [
                    ("AAA", "Alpha", 2024, 4.0),
                    ("AAA", "Alpha", 2023, 3.0),
                    ("AAA", "Alpha", 2022, 2.0),
                ],
            ),
            _world_bank_artifact(
                "b",
                "https://example.test/fx",
                "FX",
                [
                    ("AAA", "Alpha", 2023, 1.2),
                    ("AAA", "Alpha", 2022, 1.1),
                    ("AAA", "Alpha", 2021, 1.0),
                ],
            ),
        )
        parsed = WorldBankMultiIndicatorJsonAdapter().parse(
            artifacts,
            {
                "indicator_components": {"INFLATION": "inflation", "FX": "fx"},
                "minimum_observations": {"inflation": 3, "fx": 3},
            },
        )
        self.assertEqual(len(parsed.records), 1)
        record = parsed.records[0]
        self.assertEqual(record.reference_start, "2021")
        self.assertEqual(record.reference_end, "2023")
        self.assertEqual(record.values["inflation"], 4.0)
        self.assertEqual(record.values["fx"], 1.2)
        self.assertEqual(record.values["inflation_observation_count"], 3.0)
        self.assertEqual(record.values["fx_observation_count"], 3.0)

    def test_omits_component_when_minimum_observation_count_is_not_met(self):
        artifacts = (
            _world_bank_artifact(
                "a",
                "https://example.test/inflation",
                "INFLATION",
                [("AAA", "Alpha", 2024, 4.0)],
            ),
            _world_bank_artifact(
                "b",
                "https://example.test/fx",
                "FX",
                [
                    ("AAA", "Alpha", 2024, 1.2),
                    ("AAA", "Alpha", 2023, 1.1),
                    ("AAA", "Alpha", 2022, 1.0),
                ],
            ),
        )
        record = (
            WorldBankMultiIndicatorJsonAdapter()
            .parse(
                artifacts,
                {
                    "indicator_components": {"INFLATION": "inflation", "FX": "fx"},
                    "minimum_observations": {"inflation": 3, "fx": 3},
                },
            )
            .records[0]
        )
        self.assertNotIn("inflation", record.values)
        self.assertEqual(record.values["fx"], 1.2)


@skipUnless(find_spec("pandas"), "pandas is required for the HCI+ research adapter")
class HciPlusStataAdapterTests(TestCase):
    def test_selects_latest_country_row_and_preserves_missing_components(self):
        import pandas as pd

        frame = pd.DataFrame(
            [
                {
                    "iso3c": "AAA",
                    "wbcountryname": "Alpha",
                    "year": 2020.0,
                    "hlo_mf": 400.0,
                    "lays_mf": 8.0,
                    "hcip_schooling_component_mf": 75.0,
                },
                {
                    "iso3c": "AAA",
                    "wbcountryname": "Alpha",
                    "year": 2025.0,
                    "hlo_mf": 420.0,
                    "lays_mf": 8.5,
                    "hcip_schooling_component_mf": None,
                },
            ]
        )
        body = io.BytesIO()
        frame.to_stata(body, write_index=False)
        artifact = ArtifactInput(
            artifact_id="hci",
            requested_url="https://example.test/hci.dta",
            body=body.getvalue(),
        )
        record = (
            HciPlusStataAdapter()
            .parse(
                (artifact,),
                {
                    "field_components": {
                        "hlo_mf": "hlo",
                        "lays_mf": "lays",
                        "hcip_schooling_component_mf": "schooling",
                    }
                },
            )
            .records[0]
        )
        self.assertEqual(record.reference_end, "2025")
        self.assertEqual(record.values, {"hlo": 420.0, "lays": 8.5})
