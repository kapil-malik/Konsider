from io import BytesIO

import pandas as pd
from openpyxl import Workbook

from konsider.ingestion.models import RawArtifact
from konsider.ingestion.parsers import (
    classify_hci_plus_schooling_outcomes,
    parse_wipo_innovation_outputs,
    parse_world_bank_hci_plus_schooling,
)


def _artifact(source_id: str, parser_version: str) -> RawArtifact:
    return RawArtifact(
        artifact_id="sha256:test",
        source_id=source_id,
        requested_url="https://example.test/source",
        final_url="https://example.test/source",
        retrieved_at="2026-07-28T00:00:00+00:00",
        media_type="application/octet-stream",
        byte_length=1,
        sha256="test",
        dataset_version="fixture",
        parser_version=parser_version,
        path="unused",
    )


def test_hci_plus_parser_freezes_lays_and_classifies_stale_and_missing():
    frame = pd.DataFrame(
        [
            {"iso3c": "ALB", "year": 2025, "hlo_mf": 450.0, "lays_mf": 9.0},
            {"iso3c": "GUY", "year": 2020, "hlo_mf": 420.0, "lays_mf": 7.5},
            {"iso3c": "GUY", "year": 2025, "hlo_mf": None, "lays_mf": None},
            {"iso3c": "ATG", "year": 2025, "hlo_mf": 410.0, "lays_mf": 8.1},
        ]
    )
    body = BytesIO()
    frame.to_stata(body, write_index=False)
    artifact = _artifact("world_bank_hci_plus_schooling", "world_bank_hci_plus_schooling_v1")

    observations = parse_world_bank_hci_plus_schooling([artifact], [body.getvalue()])
    outcomes = classify_hci_plus_schooling_outcomes([artifact], [body.getvalue()])

    assert [(item.country_code, item.value) for item in observations] == [
        ("ALB", 9.0),
        ("ATG", 8.1),
    ]
    assert outcomes["ALB"] == ("valid", ())
    assert outcomes["ATG"] == ("valid", ())
    assert outcomes["GUY"] == ("stale", ("FRS_STALE",))
    assert outcomes["BHS"] == ("missing", ("COV_SOURCE_RECORD_MISSING",))


def test_wipo_parser_uses_only_published_innovation_outputs():
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Data"
    sheet.append(["ISO3", "ECONOMY_NAME", "NAME", "SCORE", "RANK"])
    sheet.append(["ALB", "Albania", "Global Innovation Index", 30.0, 60])
    sheet.append(["ALB", "Albania", "Innovation inputs", 40.0, 50])
    sheet.append(["ALB", "Albania", "Innovation outputs", 20.0, 70])
    sheet.append(["ZZZ", "Outside universe", "Innovation outputs", 50.0, 10])
    body = BytesIO()
    workbook.save(body)
    artifact = _artifact("wipo_innovation_outputs", "wipo_innovation_outputs_v1")

    observations = parse_wipo_innovation_outputs([artifact], [body.getvalue()])

    assert len(observations) == 1
    assert observations[0].country_code == "ALB"
    assert observations[0].value == 20.0
    assert observations[0].metric_id == "research_innovation_ecosystem"
