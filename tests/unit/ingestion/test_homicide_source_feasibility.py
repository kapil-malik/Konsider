import io
import json
from datetime import UTC, datetime

from openpyxl import Workbook

from konsider.ingestion.homicide_source_feasibility import (
    DIRECT_UNODC_METADATA_URL,
    DIRECT_UNODC_WORKBOOK_URL,
    EUROSTAT_DATA_URL,
    OECD_DATAFLOW_URL,
    UNSD_DATA_URL,
    UNSD_SERIES_URL,
    assess_oecd_dataflow,
    audit_homicide_sources,
    coverage_status,
    is_fresh,
    parse_direct_unodc,
    parse_unsd,
    reconcile_values,
    should_evaluate_fallbacks,
)
from konsider.ingestion.registry import SOURCES
from konsider.repositories.raw_artifact_repository import RawArtifactRepository


def _unodc_workbook(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "data_cts_intentional_homicide"
    sheet.append(["UNODC"])
    sheet.append(["2026-07-12"])
    sheet.append(
        [
            "Iso3_code",
            "Country",
            "Region",
            "Subregion",
            "Indicator",
            "Dimension",
            "Category",
            "Sex",
            "Age",
            "Year",
            "Unit of measurement",
            "VALUE",
            "Source",
        ]
    )
    for row in rows:
        sheet.append(row)
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def _direct_row(code, year, value, *, source="CTS", sex="Total"):
    return [
        code,
        code,
        "Region",
        "Subregion",
        "Victims of intentional homicide",
        "Total",
        "Total",
        sex,
        "Total",
        year,
        "Rate per 100,000 population",
        value,
        source,
    ]


def _unsd_catalogue():
    return json.dumps(
        [
            {
                "code": "16.1.1",
                "series": [
                    {
                        "code": "VC_IHR_PSRC",
                        "release": "2026.Q2.G.01",
                    }
                ],
            }
        ]
    ).encode()


def _unsd_payload(rows):
    return json.dumps(
        {
            "totalElements": len(rows),
            "data": rows,
        }
    ).encode()


def _unsd_row(m49, year, value, *, nature="C", sex="BOTHSEX", reporting="G"):
    return {
        "series": "VC_IHR_PSRC",
        "geoAreaCode": m49,
        "timePeriodStart": float(year),
        "value": str(value),
        "source": "National Statistical Office",
        "footnotes": [""],
        "attributes": {
            "Nature": nature,
            "Units": "PER_100000_POP",
        },
        "dimensions": {
            "Sex": sex,
            "Reporting Type": reporting,
        },
    }


def test_direct_unodc_selection_is_exact_and_conflicts_are_rejected():
    body = _unodc_workbook(
        [
            _direct_row("AAA", 2024, 1.2),
            _direct_row("AAA", 2024, 1.3, source="NSO"),
            _direct_row("BBB", 2024, 2.5),
            _direct_row("BBB", 2025, 2.4, sex="Male"),
        ]
    )

    records = parse_direct_unodc(body, {"AAA", "BBB"})

    assert [(row["country_code"], row["year"], row["value"]) for row in records] == [
        ("BBB", 2024, 2.5)
    ]
    assert records[0]["dimensions"] == {
        "geography": "national",
        "sex": "both_sexes",
        "age": "all_ages",
        "category": "total",
    }


def test_unsd_selection_maps_m49_and_rejects_aggregates_modelled_and_wrong_dimensions():
    rows = [
        _unsd_row("004", 2024, 2.0),
        _unsd_row("008", 2024, 3.0, nature="M"),
        _unsd_row("008", 2024, 3.0, sex="MALE"),
        _unsd_row("002", 2024, 4.0),
    ]

    records, metadata = parse_unsd(
        _unsd_catalogue(),
        _unsd_payload(rows),
        {"4": "AFG", "8": "ALB"},
    )

    assert [(row["country_code"], row["year"], row["value"]) for row in records] == [
        ("AFG", 2024, 2.0)
    ]
    assert metadata["release"] == "2026.Q2.G.01"
    assert metadata["unresolved_geo_area_codes"] == ["2"]
    assert metadata["rejected_record_counts"]["modelled_or_non_country_nature"] == 1
    assert metadata["rejected_record_counts"]["not_both_sexes"] == 1


def test_freshness_uses_observation_year_and_reconciliation_is_deterministic():
    assert is_fresh(2021, 2026)
    assert not is_fresh(2020, 2026)
    assert reconcile_values(1.0, 2024, 1.0, 2024)["classification"] == "exact_match"
    assert reconcile_values(1.004, 2024, 1.0, 2024)["classification"] == "rounding_only"
    assert reconcile_values(1.2, 2024, 1.0, 2024)["classification"] == "material_revision"
    assert reconcile_values(1.0, 2024, 1.0, 2023)["classification"] == "different_reference_year"


def test_fallback_decision_requires_both_primaries_to_fail():
    assert should_evaluate_fallbacks(99, 98, 100)
    assert not should_evaluate_fallbacks(100, 98, 100)
    assert not should_evaluate_fallbacks(99, 100, 100)
    assert coverage_status(99, 100) == "FAIL"
    assert coverage_status(100, 100) == "PASS"


def test_oecd_regional_dataflow_is_not_semantically_equivalent():
    body = b"""<?xml version="1.0"?>
    <Structure xmlns="urn:test">
      <Dataflow id="DSD_REG_SOC@DF_SAFETY" agencyID="OECD.CFE.EDS" version="2.4">
        <Description xml:lang="en">This dataset provides homicide rates in regions.</Description>
      </Dataflow>
    </Structure>
    """
    result = assess_oecd_dataflow(body)
    assert result["semantic_equivalence"] is False
    assert result["description_mentions_regions"] is True
    json_result = assess_oecd_dataflow(
        json.dumps(
            {
                "references": {
                    "urn:Dataflow=OECD.CFE.EDS:DSD_REG_SOC@DF_SAFETY(2.4)": {
                        "id": "DSD_REG_SOC@DF_SAFETY",
                        "name": "Safety - Regions",
                        "description": "Homicide rates in regions.",
                    }
                }
            }
        ).encode()
    )
    assert json_result["semantic_equivalence"] is False
    assert json_result["description_mentions_regions"] is True


def _write_coverage_fixture(root, raw_root):
    root.mkdir()
    raw_repository = RawArtifactRepository(raw_root)
    wdi_body = json.dumps(
        [
            {},
            [
                {
                    "countryiso3code": "AAA",
                    "date": "2020",
                    "value": 1.0,
                    "indicator": {"id": "VC.IHR.PSRC.P5"},
                },
                {
                    "countryiso3code": "BBB",
                    "date": "2020",
                    "value": 2.0,
                    "indicator": {"id": "VC.IHR.PSRC.P5"},
                },
            ],
        ]
    ).encode()
    wdi_artifact = raw_repository.capture(
        SOURCES["unodc_homicide"],
        wdi_body,
        requested_url=SOURCES["unodc_homicide"].download_urls[0],
        final_url=SOURCES["unodc_homicide"].download_urls[0],
        retrieved_at="2026-07-23T00:00:00+00:00",
        media_type="application/json",
    )
    (root / "summary.json").write_text(
        json.dumps(
            {
                "audit_id": "coverage-fixture",
                "complete_publishable_country_count": 97,
                "minimum_required_country_count": 100,
            }
        ),
        encoding="utf-8",
    )
    criteria = {
        "ambient_pm25_population_weighted": {"status": "available"},
        "intentional_homicide_rate": {"status": "stale"},
        "household_consumption_price_level_us_100": {"status": "available"},
        "women_legal_economic_equality": {"status": "available"},
        "infrastructure_readiness_composite": {"status": "available"},
    }
    (root / "country-coverage.jsonl").write_text(
        "\n".join(
            json.dumps(
                {
                    "code": code,
                    "display_name": code,
                    "criteria": criteria,
                }
            )
            for code in ("AAA", "BBB")
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "country-registry.json").write_text(
        json.dumps(
            [
                {"code": "AAA", "un_m49": "004", "display_name": "Alpha", "aliases": []},
                {"code": "BBB", "un_m49": "008", "display_name": "Beta", "aliases": []},
            ]
        ),
        encoding="utf-8",
    )
    (root / "raw-artifacts.json").write_text(
        json.dumps([wdi_artifact.to_dict()]),
        encoding="utf-8",
    )


def test_online_and_replay_match_and_leave_active_pointer_unchanged(tmp_path):
    raw_root = tmp_path / "raw"
    coverage = tmp_path / "coverage"
    _write_coverage_fixture(coverage, raw_root)
    release_root = tmp_path / "releases"
    release_root.mkdir()
    active = release_root / "active.json"
    active.write_text('{"release_id":"before"}\n', encoding="utf-8")

    bodies = {
        DIRECT_UNODC_WORKBOOK_URL: _unodc_workbook([_direct_row("AAA", 2024, 1.1)]),
        DIRECT_UNODC_METADATA_URL: b"%PDF fixture",
        UNSD_SERIES_URL: _unsd_catalogue(),
        UNSD_DATA_URL: _unsd_payload([_unsd_row("008", 2024, 2.1)]),
        EUROSTAT_DATA_URL: json.dumps(
            {
                "id": ["freq", "iccs", "leg_stat", "sex", "unit", "geo", "time"],
                "size": [1, 1, 1, 1, 1, 1, 1],
                "dimension": {
                    key: {
                        "category": {
                            "index": [value],
                            "label": {value: "Georgia" if key == "geo" else value},
                        }
                    }
                    for key, value in {
                        "freq": "A",
                        "iccs": "ICCS0101",
                        "leg_stat": "PER_VICT",
                        "sex": "T",
                        "unit": "P_HTHAB",
                        "geo": "GE",
                        "time": "2024",
                    }.items()
                },
                "value": {},
            }
        ).encode(),
        OECD_DATAFLOW_URL: b"""<Structure xmlns="urn:test"><Dataflow
            id="DSD_REG_SOC@DF_SAFETY" agencyID="OECD.CFE.EDS" version="2.4">
            <Description>Homicide rates in regions.</Description>
            </Dataflow></Structure>""",
    }

    def fetcher(url):
        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if url == DIRECT_UNODC_WORKBOOK_URL
            else "application/json"
        )
        return bodies[url], url, media_type, {"http_status": 200}

    online_path, online = audit_homicide_sources(
        coverage,
        "online",
        mode="online",
        output_root=tmp_path / "reports",
        raw_root=raw_root,
        release_root=release_root,
        fetcher=fetcher,
        clock=lambda: datetime(2026, 7, 23, tzinfo=UTC),
    )
    replay_path, replay = audit_homicide_sources(
        coverage,
        "replay",
        mode="replay",
        output_root=tmp_path / "reports",
        raw_root=raw_root,
        release_root=release_root,
        artifact_manifest=online_path / "raw-artifacts.json",
    )

    ignored = {"study_id", "mode"}
    assert {key: value for key, value in online.items() if key not in ignored} == {
        key: value for key, value in replay.items() if key not in ignored
    }
    for name in ("source-comparison.json", "country-comparison.jsonl", "discrepancies.jsonl"):
        assert (online_path / name).read_bytes() == (replay_path / name).read_bytes()
    assert online["fallback_evaluation_triggered"] is True
    assert online["status"] == "FAIL"
    assert online["mixed_source_adoption_allowed"] is False
    assert active.read_text(encoding="utf-8") == '{"release_id":"before"}\n'
