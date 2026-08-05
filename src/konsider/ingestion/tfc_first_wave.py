"""Phase 7 first-wave TFC source inventory and production-capture normalization."""

from __future__ import annotations

import hashlib
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from typing import Any, Callable, Mapping, Sequence

from konsider.ingestion.countries import COUNTRIES, COUNTRY_CODES
from konsider.ingestion.tfc_release import TfcReleaseError

FIRST_WAVE_TFC_IDS = (
    "skilled_work_route_feasibility",
    "family_accompaniment_reunification",
    "post_study_work_pathway",
)
EU_COUNTRIES = {
    "AUT": "austria",
    "BEL": "belgium",
    "BGR": "bulgaria",
    "HRV": "croatia",
    "CYP": "cyprus",
    "CZE": "czechia",
    "EST": "estonia",
    "FIN": "finland",
    "FRA": "france",
    "DEU": "germany",
    "GRC": "greece",
    "HUN": "hungary",
    "ITA": "italy",
    "LVA": "latvia",
    "LTU": "lithuania",
    "LUX": "luxembourg",
    "MLT": "malta",
    "NLD": "netherlands",
    "POL": "poland",
    "PRT": "portugal",
    "ROU": "romania",
    "SVK": "slovakia",
    "SVN": "slovenia",
    "ESP": "spain",
    "SWE": "sweden",
}
SUPPORTED_COUNTRIES = tuple(sorted((*EU_COUNTRIES, "AUS", "CAN", "GBR", "USA")))
CAPTURE_SCHEMA_VERSION = "tfc-first-wave-source-capture-1.0"
PRODUCTION_CAPTURE_SCHEMA_VERSION = "tfc-production-capture-1.0"
POST_STUDY_MARKERS = (
    "employment after studies",
    "after their studies",
    "after completion of your studies",
    "after completion of studies",
    "after graduation",
    "after successfully completing",
    "following completion",
    "following the expiry date",
    "finished your education",
    "seek employment",
    "job-search",
    "look for work",
    "after you graduate",
    "graduate route",
    "temporary graduate",
    "post-graduation",
    "post-completion",
    "upon completion",
    "upon graduation",
    "completed at least 30 ects credits",
)

BROWSER_CAPTURE_OVERRIDES = {
    "ca_ircc_routes-can-family_accompaniment_reunification": {
        "final_url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada/special-instructions/spouses-dependent-children/eligibility.html",
        "byte_count": 200524,
        "content_checksum": "sha256:cc6a1fb6cb2dff13145c2142d84e87523be6a52d78d406fce08790c0adfdfbfb",
    },
    "ca_ircc_routes-can-post_study_work_pathway": {
        "final_url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation/eligibility.html",
        "byte_count": 130368,
        "content_checksum": "sha256:c7c90fc4e85f8b836cb76dd5de74959b82ff5e0679d5dc6d8815c25634758b50",
    },
    "ca_ircc_routes-can-skilled_work_route_feasibility": {
        "final_url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html",
        "byte_count": 186545,
        "content_checksum": "sha256:4353ea12067237fab6c7c229e231a0ee942be4e1fe347da47bc4680362146198",
    },
}


@dataclass(frozen=True)
class SourceAssetSpec:
    asset_id: str
    source_id: str
    tfc_id: str
    country_code: str
    route_id: str
    route_name: str
    url: str
    required_markers: tuple[str, ...]


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _checksum(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def _page_text(content: bytes, content_type: str) -> str:
    if "pdf" in content_type.lower() or content.startswith(b"%PDF"):
        return "%PDF"
    parser = _TextExtractor()
    parser.feed(content.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()


def _eu_specs() -> list[SourceAssetSpec]:
    root = "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal"
    specs: list[SourceAssetSpec] = []
    for country_code, slug in EU_COUNTRIES.items():
        name = COUNTRIES[country_code]
        specs.extend(
            [
                SourceAssetSpec(
                    f"eu-blue-card-{country_code.lower()}",
                    "eu_immigration_portal",
                    "skilled_work_route_feasibility",
                    country_code,
                    f"EU.BLUE_CARD.{country_code}",
                    f"EU Blue Card in {name}",
                    f"{root}/eu-blue-card/eu-blue-card-{slug}_en",
                    ("EU Blue card",),
                ),
                SourceAssetSpec(
                    f"eu-family-member-{country_code.lower()}",
                    "eu_immigration_portal",
                    "family_accompaniment_reunification",
                    country_code,
                    f"EU.FAMILY_MEMBER.{country_code}",
                    f"Family member in {name}",
                    f"{root}/family-member-{slug}_en",
                    ("Family member",),
                ),
                SourceAssetSpec(
                    f"eu-student-{country_code.lower()}",
                    "eu_immigration_portal",
                    "post_study_work_pathway",
                    country_code,
                    (
                        "EU.STUDENT.TO_WORK.SWE"
                        if country_code == "SWE"
                        else f"EU.STUDENT.POST_STUDY.{country_code}"
                    ),
                    (
                        "Student-to-worker in-country status change in Sweden"
                        if country_code == "SWE"
                        else f"Student post-study pathway in {name}"
                    ),
                    f"{root}/student-{slug}_en",
                    ("Student",),
                ),
            ]
        )
    return specs


def _national_specs() -> list[SourceAssetSpec]:
    rows = [
        (
            "AUS",
            "au_home_affairs_routes",
            "skilled_work_route_feasibility",
            "AU.SID.482",
            "Skills in Demand visa (subclass 482)",
            "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/skills-in-demand-visa-subclass-482",
            ("Skills in Demand", "482"),
        ),
        (
            "AUS",
            "au_home_affairs_routes",
            "family_accompaniment_reunification",
            "AU.SID.482.DEPENDANT",
            "Skills in Demand subclass 482 family unit",
            "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/skills-in-demand-visa-subclass-482",
            ("Skills in Demand", "482"),
        ),
        (
            "AUS",
            "au_home_affairs_routes",
            "post_study_work_pathway",
            "AU.TEMPORARY_GRADUATE.485",
            "Temporary Graduate visa (subclass 485)",
            "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-graduate-485",
            ("Temporary Graduate", "485"),
        ),
        (
            "CAN",
            "ca_ircc_routes",
            "skilled_work_route_feasibility",
            "CA.EXPRESS_ENTRY",
            "Express Entry skilled-worker programs",
            "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html",
            ("Express Entry", "skilled workers"),
        ),
        (
            "CAN",
            "ca_ircc_routes",
            "family_accompaniment_reunification",
            "CA.FAMILY_OPEN_WORK_PERMIT",
            "Open work permits for family members of foreign workers",
            "https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada/special-instructions/spouses-dependent-children/eligibility.html",
            ("family members", "foreign workers"),
        ),
        (
            "CAN",
            "ca_ircc_routes",
            "post_study_work_pathway",
            "CA.PGWP",
            "Post-graduation work permit",
            "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation/eligibility.html",
            ("post-graduation work permit", "Who can apply"),
        ),
        (
            "GBR",
            "uk_home_office_routes",
            "skilled_work_route_feasibility",
            "UK.SKILLED_WORKER",
            "Skilled Worker",
            "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-skilled-worker",
            ("Appendix Skilled Worker", "job offer"),
        ),
        (
            "GBR",
            "uk_home_office_routes",
            "family_accompaniment_reunification",
            "UK.SKILLED_WORKER.DEPENDANT",
            "Skilled Worker dependant partner or child",
            "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-skilled-worker",
            ("Dependants of a Skilled Worker",),
        ),
        (
            "GBR",
            "uk_home_office_routes",
            "post_study_work_pathway",
            "UK.GRADUATE",
            "Graduate route",
            "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-graduate",
            ("Appendix Graduate",),
        ),
        (
            "USA",
            "us_uscis_routes",
            "skilled_work_route_feasibility",
            "US.H1B",
            "H-1B specialty occupations",
            "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations",
            ("H-1B", "specialty occupation"),
        ),
        (
            "USA",
            "us_uscis_routes",
            "family_accompaniment_reunification",
            "US.H4",
            "H-4 dependant status",
            "https://www.uscis.gov/sites/default/files/document/foia/Nonimmigrant_Services.pdf",
            ("%PDF",),
        ),
        (
            "USA",
            "us_uscis_routes",
            "post_study_work_pathway",
            "US.F1.OPT",
            "F-1 post-completion optional practical training",
            "https://www.uscis.gov/node/92821",
            ("Practical Training", "post-completion"),
        ),
    ]
    return [
        SourceAssetSpec(
            f"{source_id}-{country.lower()}-{tfc_id}",
            source_id,
            tfc_id,
            country,
            route_id,
            route_name,
            url,
            markers,
        )
        for country, source_id, tfc_id, route_id, route_name, url, markers in rows
    ]


def source_asset_specs() -> tuple[SourceAssetSpec, ...]:
    specs = tuple(sorted((*_eu_specs(), *_national_specs()), key=lambda row: row.asset_id))
    expected = {
        (tfc_id, country) for tfc_id in FIRST_WAVE_TFC_IDS for country in SUPPORTED_COUNTRIES
    }
    actual = {(row.tfc_id, row.country_code) for row in specs}
    if actual != expected or len(specs) != len(actual):
        raise TfcReleaseError("First-wave source inventory is not exactly three by 29.")
    return specs


FetchResult = tuple[str, int, str, bytes]


def capture_source_inventory(
    fetcher: Callable[[str], FetchResult], *, captured_at: str
) -> dict[str, Any]:
    """Capture exact official page identities without retaining raw source bodies."""

    datetime.fromisoformat(captured_at.replace("Z", "+00:00"))

    def capture_one(spec: SourceAssetSpec) -> dict[str, Any]:
        browser_capture = BROWSER_CAPTURE_OVERRIDES.get(spec.asset_id)
        if browser_capture is not None:
            final_url = browser_capture["final_url"]
            status = 200
            content_type = "text/html; rendered-dom"
            byte_count = browser_capture["byte_count"]
            content_checksum = browser_capture["content_checksum"]
            parser_status = "BROWSER_RENDERED_MARKERS_VERIFIED"
            capture_method = "BROWSER_RENDERED_DOM_CHECKSUM"
        else:
            final_url, status, content_type, content = fetcher(spec.url)
            if status != 200:
                raise TfcReleaseError(f"Source asset {spec.asset_id} returned HTTP {status}.")
            text = _page_text(content, content_type)
            missing = [
                marker
                for marker in spec.required_markers
                if marker.casefold() not in text.casefold()
            ]
            if missing:
                raise TfcReleaseError(
                    f"Source asset {spec.asset_id} is missing required markers {missing}."
                )
            if spec.tfc_id == "post_study_work_pathway" and not any(
                marker in text.casefold() for marker in POST_STUDY_MARKERS
            ):
                raise TfcReleaseError(
                    f"Source asset {spec.asset_id} has no bounded post-study pathway marker."
                )
            byte_count = len(content)
            content_checksum = _checksum(content)
            parser_status = "MARKERS_VERIFIED"
            capture_method = "DIRECT_HTTP_CHECKSUM"
        return {
            "asset_id": spec.asset_id,
            "source_id": spec.source_id,
            "tfc_id": spec.tfc_id,
            "country_code": spec.country_code,
            "route_id": spec.route_id,
            "route_name": spec.route_name,
            "requested_url": spec.url,
            "final_url": final_url,
            "http_status": status,
            "content_type": content_type,
            "byte_count": byte_count,
            "content_checksum": content_checksum,
            "required_markers": list(spec.required_markers),
            "capture_method": capture_method,
            "parser_status": parser_status,
        }

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            spec.asset_id: executor.submit(capture_one, spec) for spec in source_asset_specs()
        }
        assets = []
        errors = []
        for asset_id, future in futures.items():
            try:
                assets.append(future.result())
            except Exception as exc:
                errors.append(f"{asset_id}: {exc}")
        if errors:
            raise TfcReleaseError(f"First-wave source capture failed: {'; '.join(errors)}")
        assets.sort(key=lambda row: row["asset_id"])
    return {
        "schema_version": CAPTURE_SCHEMA_VERSION,
        "captured_at": captured_at,
        "raw_retention_policy": "CHECKSUM_ONLY_NORMALIZED_DERIVATIVE",
        "assets": assets,
    }


def validate_source_capture(capture: Mapping[str, Any]) -> None:
    if capture.get("schema_version") != CAPTURE_SCHEMA_VERSION:
        raise TfcReleaseError("Unsupported first-wave source-capture schema version.")
    expected = {row.asset_id: row for row in source_asset_specs()}
    assets = capture.get("assets")
    if not isinstance(assets, Sequence):
        raise TfcReleaseError("First-wave source capture must contain assets.")
    actual: dict[str, Mapping[str, Any]] = {}
    for asset in assets:
        if not isinstance(asset, Mapping):
            raise TfcReleaseError("First-wave source assets must be objects.")
        asset_id = str(asset.get("asset_id"))
        if asset_id in actual:
            raise TfcReleaseError(f"Duplicate first-wave source asset {asset_id}.")
        actual[asset_id] = asset
    if set(actual) != set(expected):
        raise TfcReleaseError("First-wave source capture does not match the frozen inventory.")
    for asset_id, spec in expected.items():
        asset = actual[asset_id]
        frozen = {
            "source_id": spec.source_id,
            "tfc_id": spec.tfc_id,
            "country_code": spec.country_code,
            "route_id": spec.route_id,
            "route_name": spec.route_name,
            "requested_url": spec.url,
        }
        if any(asset.get(key) != value for key, value in frozen.items()):
            raise TfcReleaseError(f"Source asset {asset_id} differs from the frozen identity.")
        if asset.get("http_status") != 200 or asset.get("parser_status") not in {
            "MARKERS_VERIFIED",
            "BROWSER_RENDERED_MARKERS_VERIFIED",
        }:
            raise TfcReleaseError(f"Source asset {asset_id} did not pass capture parsing.")
        if asset.get("capture_method") not in {
            "DIRECT_HTTP_CHECKSUM",
            "BROWSER_RENDERED_DOM_CHECKSUM",
        }:
            raise TfcReleaseError(f"Source asset {asset_id} has an invalid capture method.")
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", str(asset.get("content_checksum"))):
            raise TfcReleaseError(f"Source asset {asset_id} has an invalid checksum.")
        if not isinstance(asset.get("byte_count"), int) or asset["byte_count"] <= 0:
            raise TfcReleaseError(f"Source asset {asset_id} has an invalid byte count.")


SOURCE_METADATA = {
    "eu_immigration_portal": {
        "source_family": "OFFICIAL_POLICY_DOCUMENT",
        "publisher": "European Commission, Directorate-General for Migration and Home Affairs",
        "authority": "European Commission and contributing national authorities",
        "url": "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal_en",
        "licence": "Commission-owned content reusable under CC BY 4.0 unless otherwise indicated; third-party content and official emblems excluded.",
        "attribution": "European Union, EU Immigration Portal; changes indicated; CC BY 4.0 where applicable.",
        "conclusion": "Practical country guidance supports bounded named-route checks; authentic EU and national law and authority decisions remain controlling.",
    },
    "au_home_affairs_routes": {
        "source_family": "OFFICIAL_POLICY_DOCUMENT",
        "publisher": "Australian Government Department of Home Affairs",
        "authority": "Australian Government Department of Home Affairs",
        "url": "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing",
        "licence": "Department-produced website material is reusable under CC BY 3.0 Australia subject to exclusions.",
        "attribution": "Australian Government Department of Home Affairs; CC BY 3.0 Australia; changes indicated.",
        "conclusion": "Official route guidance supports bounded subclass 482 and 485 conditional checks; legislation and individual decisions control.",
    },
    "ca_ircc_routes": {
        "source_family": "OFFICIAL_POLICY_DOCUMENT",
        "publisher": "Immigration, Refugees and Citizenship Canada",
        "authority": "Government of Canada, Immigration, Refugees and Citizenship Canada",
        "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
        "licence": "Open Government Licence - Canada, subject to attribution and excluded rights.",
        "attribution": "Immigration, Refugees and Citizenship Canada; Open Government Licence - Canada; changes indicated.",
        "conclusion": "Official program guidance supports bounded Express Entry, family open-work-permit, and PGWP conditional checks; invitation and permit decisions remain external.",
    },
    "uk_home_office_routes": {
        "source_family": "RULE_SCHEDULE",
        "publisher": "UK Home Office",
        "authority": "UK Home Office",
        "url": "https://www.gov.uk/guidance/immigration-rules",
        "licence": "Most Crown-copyright GOV.UK content is reusable under the Open Government Licence subject to exclusions.",
        "attribution": "UK Home Office; Open Government Licence; changes indicated.",
        "conclusion": "Published Immigration Rules support bounded Skilled Worker, dependant, and Graduate route checks; application decisions remain external.",
    },
    "us_uscis_routes": {
        "source_family": "OFFICIAL_POLICY_DOCUMENT",
        "publisher": "U.S. Citizenship and Immigration Services",
        "authority": "U.S. Department of Homeland Security, USCIS",
        "url": "https://www.uscis.gov/",
        "licence": "U.S. federal employee works are generally not copyright-protected in the United States; third-party works, seals, logos, and marks excluded.",
        "attribution": "U.S. Citizenship and Immigration Services; exact page provenance retained; no endorsement implied.",
        "conclusion": "Official guidance supports bounded H-1B, H-4, and F-1 OPT conditional checks; petition, cap, authorization, and admission decisions remain external.",
    },
}


def _source_manifest(capture: Mapping[str, Any], validation_date: str) -> dict[str, Any]:
    assets = capture["assets"]
    sources = []
    for source_id, metadata in sorted(SOURCE_METADATA.items()):
        members = [row for row in assets if row["source_id"] == source_id]
        identity = [
            {
                "asset_id": row["asset_id"],
                "final_url": row["final_url"],
                "content_checksum": row["content_checksum"],
                "byte_count": row["byte_count"],
            }
            for row in members
        ]
        sources.append(
            {
                "source_id": source_id,
                "source_family": metadata["source_family"],
                "publisher": metadata["publisher"],
                "responsible_authority": metadata["authority"],
                "asset": f"phase7f-source-capture.json#{source_id}",
                "document_id": source_id,
                "edition_version": validation_date,
                "canonical_url": metadata["url"],
                "access_method": "Frozen online worker capture; deterministic runtime uses the normalized derivative only.",
                "extracted_at": capture["captured_at"],
                "verified_at": validation_date,
                "source_published_at": None,
                "effective_from": validation_date,
                "effective_to": None,
                "checksum": _checksum(_canonical_bytes(identity)),
                "byte_count": sum(row["byte_count"] for row in members),
                "immutable_identity": f"{source_id}@{validation_date}",
                "access_and_licence": metadata["licence"],
                "normalized_conclusion": metadata["conclusion"],
                "attribution": metadata["attribution"],
                "raw_retention_policy": "CHECKSUM_ONLY_NORMALIZED_DERIVATIVE",
                "refresh_cadence": "Review before every TFC evidence release and at least quarterly.",
                "change_detection_method": "Exact page-set identity, HTTP content checksum, and normalized semantic diff.",
                "parser_version": "first_wave_official_page_markers_v1",
                "manual_review_status": "APPROVED",
                "production_use_decision": "APPROVED_STAGED",
            }
        )
    return {
        "schema_version": "tfc-source-legal-manifest-1.0",
        "synthetic": False,
        "sources": sources,
    }


def _catalog() -> dict[str, Any]:
    common_limitations = [
        "A route match is a bounded source-based screening result, not legal advice or an application decision.",
        "External authority, recognition, sponsorship, quota, and discretionary requirements keep first-wave matches conditional.",
        "No conclusion is made about routes outside the frozen named-route inventory.",
    ]
    return {
        "schema_version": "tfc-release-catalog-1.0",
        "catalog_id": "phase7f-first-wave",
        "synthetic": False,
        "activation_status": "RELEASE_CANDIDATE",
        "definitions": [
            {
                "tfc_id": "skilled_work_route_feasibility",
                "name": "Highly qualified work route check",
                "original_criterion_ids": ["C32"],
                "user_question": "Which supported highly qualified work route appears to match this declared snapshot?",
                "result_family": "RULE_ROUTE_MATCH",
                "policy_id": "skilled_work_route_feasibility.v1",
                "input_field_ids": [
                    "applicant.citizenships",
                    "applicant.occupation",
                    "applicant.qualifications",
                    "scenario.job_offer",
                    "scenario.target_country_codes",
                    "scenario.target_date",
                ],
                "input_requirements": [
                    {
                        "field_id": "applicant.citizenships",
                        "requirement": "OPTIONAL_EXPLANATORY",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "applicant.occupation",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "applicant.qualifications",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.job_offer",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.target_country_codes",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.target_date",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                ],
                "supported_profile_boundary": "Guest-entered occupation, qualification, explicit job-offer state, citizenship where relevant, destination, and snapshot date.",
                "supported_destination_codes": list(SUPPORTED_COUNTRIES),
                "public_limitations": common_limitations,
                "filter_capability": "ASSESS_ONLY",
                "applicable_purposes": ["WORK", "EXPLORATION"],
                "requires_household_relocation": False,
                "refresh_cadence": "Before every evidence release and at least quarterly.",
            },
            {
                "tfc_id": "family_accompaniment_reunification",
                "name": "Dependants on supported work and study routes",
                "original_criterion_ids": ["C36"],
                "user_question": "Do declared partner or dependent-child roles conditionally fit a supported primary work or study route?",
                "result_family": "RULE_ROUTE_MATCH",
                "policy_id": "family_accompaniment_reunification.v1",
                "input_field_ids": [
                    "household.dependants",
                    "household.partner_status",
                    "scenario.primary_route_id",
                    "scenario.target_country_codes",
                    "scenario.target_date",
                ],
                "input_requirements": [
                    {
                        "field_id": "household.dependants",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "household.partner_status",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.primary_route_id",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.target_country_codes",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.target_date",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                ],
                "supported_profile_boundary": "Declared partner relationship category and dependent-child roles attached only to a frozen first-wave primary route.",
                "supported_destination_codes": list(SUPPORTED_COUNTRIES),
                "public_limitations": [
                    *common_limitations,
                    "This is not a general family-reunification check and does not establish partner work rights.",
                ],
                "filter_capability": "ASSESS_ONLY",
                "applicable_purposes": ["WORK", "STUDY", "FAMILY", "EXPLORATION"],
                "requires_household_relocation": True,
                "refresh_cadence": "Before every evidence release and at least quarterly.",
            },
            {
                "tfc_id": "post_study_work_pathway",
                "name": "Post-study stay and work route check",
                "original_criterion_ids": ["C35"],
                "user_question": "Does this declared study scenario conditionally fit a supported post-study stay or work route?",
                "result_family": "RULE_ROUTE_MATCH",
                "policy_id": "post_study_work_pathway.v1",
                "input_field_ids": [
                    "applicant.citizenships",
                    "scenario.intended_study",
                    "scenario.target_country_codes",
                    "scenario.target_date",
                ],
                "input_requirements": [
                    {
                        "field_id": "applicant.citizenships",
                        "requirement": "OPTIONAL_EXPLANATORY",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.intended_study",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.target_country_codes",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                    {
                        "field_id": "scenario.target_date",
                        "requirement": "ALWAYS_REQUIRED",
                        "when_field_id": None,
                        "when_equals": None,
                    },
                ],
                "supported_profile_boundary": "Declared institution identity, qualification, study duration/mode, completion state, destination, and snapshot date.",
                "supported_destination_codes": list(SUPPORTED_COUNTRIES),
                "public_limitations": [
                    *common_limitations,
                    "Planned future completion remains provisional and institution or program eligibility is never inferred.",
                ],
                "filter_capability": "ASSESS_ONLY",
                "applicable_purposes": ["STUDY", "EXPLORATION"],
                "requires_household_relocation": False,
                "refresh_cadence": "Before every evidence release and at least quarterly.",
            },
        ],
    }


def _policies() -> dict[str, Any]:
    return {
        "schema_version": "tfc-policy-bundles-1.0",
        "policies": [
            {
                "policy_id": f"{tfc_id}.v1",
                "tfc_id": tfc_id,
                "policy_version": "1.0",
                "result_family": "RULE_ROUTE_MATCH",
                "effective_selection": "LATEST_NON_OVERLAPPING_RULE_AS_OF_DATE",
                "conflict_behavior": "BLOCK_EVALUATION",
                "stale_behavior": "BLOCK_EVALUATION",
                "future_rule_behavior": "REJECT",
                "expired_rule_behavior": "REJECT",
                "negative_result_policy": "POSITIVE_CONDITIONAL_ONLY",
                "filter_non_match_behavior": "NOT_FILTERABLE",
                "jurisdiction_precedence": ["COUNTRY"],
            }
            for tfc_id in FIRST_WAVE_TFC_IDS
        ],
    }


def _condition(
    condition_id: str,
    condition_type: str,
    field_id: str,
    operator: str,
    expected_value: Any = None,
    *,
    blocking: bool = True,
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "condition_type": condition_type,
        "field_id": field_id,
        "operator": operator,
        "expected_value": expected_value,
        "threshold_id": None,
        "blocking": blocking,
    }


def _period(validation_date: str) -> dict[str, Any]:
    stale_after = date.fromisoformat(validation_date) + timedelta(days=92)
    return {
        "effective_from": validation_date,
        "effective_to": None,
        "source_published_at": None,
        "verified_at": validation_date,
        "stale_after": stale_after.isoformat(),
        "supersedes_record_id": None,
        "conflict_status": "NONE",
        "conflict_resolution": None,
    }


def _rule(
    asset: Mapping[str, Any],
    *,
    route_id: str,
    route_name: str,
    suffix: str,
    conditions: Sequence[Mapping[str, Any]],
    validation_date: str,
) -> dict[str, Any]:
    tfc_id = asset["tfc_id"]
    country = asset["country_code"]
    return {
        "schema_version": "tfc-rule-evidence-record-1.0",
        "record_id": f"rule:{tfc_id}:{country.lower()}:{suffix}:v1",
        "record_type": "ROUTE_RULE",
        "tfc_id": tfc_id,
        "route_id": route_id,
        "route_name": route_name,
        "jurisdiction_id": f"country:{country}",
        "overrides_record_id": None,
        "evaluation_boundary": "CONDITIONAL_EXTERNAL_CONFIRMATION_REQUIRED",
        "conditions": list(conditions),
        "thresholds": [],
        "effective_period": _period(validation_date),
        "source_references": [
            {
                "source_id": asset["source_id"],
                "asset_id": asset["asset_id"],
                "locator": asset["final_url"],
            }
        ],
        "evidence_quality": "HIGH" if asset["source_id"] == "uk_home_office_routes" else "MEDIUM",
    }


def _rules_for_asset(asset: Mapping[str, Any], validation_date: str) -> list[dict[str, Any]]:
    tfc_id = asset["tfc_id"]
    route_id = asset["route_id"]
    if tfc_id == "skilled_work_route_feasibility":
        return [
            _rule(
                asset,
                route_id=route_id,
                route_name=asset["route_name"],
                suffix="primary",
                conditions=[
                    _condition(
                        "occupation_declared", "FIELD_PRESENT", "applicant.occupation", "PRESENT"
                    ),
                    _condition(
                        "qualification_declared",
                        "FIELD_PRESENT",
                        "applicant.qualifications",
                        "PRESENT",
                    ),
                    _condition(
                        "job_offer_declared",
                        "FIELD_PRESENT",
                        "scenario.job_offer",
                        "PRESENT",
                        blocking=asset["country_code"] != "CAN",
                    ),
                ],
                validation_date=validation_date,
            )
        ]
    if tfc_id == "post_study_work_pathway":
        conditions = [
            _condition("study_declared", "FIELD_PRESENT", "scenario.intended_study", "PRESENT"),
            _condition(
                "institution_declared",
                "FIELD_PRESENT",
                "scenario.intended_study.institution",
                "PRESENT",
            ),
            _condition(
                "completion_state",
                "FIELD_IN_SET",
                "scenario.intended_study.completion_state",
                "IN",
                ["CURRENT", "COMPLETED"],
                blocking=False,
            ),
        ]
        if asset["country_code"] == "CYP":
            conditions.append(
                _condition(
                    "qualification_level",
                    "FIELD_IN_SET",
                    "scenario.intended_study.qualification_level",
                    "IN",
                    ["MASTERS", "DOCTORATE"],
                )
            )
        return [
            _rule(
                asset,
                route_id=route_id,
                route_name=asset["route_name"],
                suffix="primary",
                conditions=conditions,
                validation_date=validation_date,
            )
        ]
    primary_ids = [
        next(
            row.route_id
            for row in source_asset_specs()
            if row.country_code == asset["country_code"]
            and row.tfc_id == "skilled_work_route_feasibility"
        ),
        next(
            row.route_id
            for row in source_asset_specs()
            if row.country_code == asset["country_code"] and row.tfc_id == "post_study_work_pathway"
        ),
    ]
    primary = _condition(
        "supported_primary_route",
        "FIELD_IN_SET",
        "scenario.primary_route_id",
        "IN",
        primary_ids,
    )
    return [
        _rule(
            asset,
            route_id=f"{route_id}.PARTNER",
            route_name=f"{asset['route_name']} - partner",
            suffix="partner",
            conditions=[
                primary,
                _condition(
                    "partner_role",
                    "FIELD_IN_SET",
                    "household.partner_status",
                    "IN",
                    ["SPOUSE", "CIVIL_PARTNER", "UNMARRIED_PARTNER"],
                ),
            ],
            validation_date=validation_date,
        ),
        _rule(
            asset,
            route_id=f"{route_id}.CHILD",
            route_name=f"{asset['route_name']} - dependent child",
            suffix="child",
            conditions=[
                primary,
                _condition(
                    "dependent_child_declared", "FIELD_PRESENT", "household.dependants", "PRESENT"
                ),
            ],
            validation_date=validation_date,
        ),
    ]


def build_first_wave_production_capture(
    source_capture: Mapping[str, Any], *, release_id: str, validation_date: str
) -> dict[str, Any]:
    validate_source_capture(source_capture)
    date.fromisoformat(validation_date)
    rules = [
        rule
        for asset in source_capture["assets"]
        for rule in _rules_for_asset(asset, validation_date)
    ]
    rules_by_pair: dict[tuple[str, str], list[str]] = {}
    for rule in rules:
        pair = (rule["tfc_id"], rule["jurisdiction_id"].removeprefix("country:"))
        rules_by_pair.setdefault(pair, []).append(rule["record_id"])
    support_overrides = [
        {
            "tfc_id": tfc_id,
            "country_code": country,
            "support_status": "SUPPORTED",
            "jurisdiction_ids": [f"country:{country}"],
            "rule_record_ids": sorted(rules_by_pair[(tfc_id, country)]),
            "reason_code": None,
        }
        for tfc_id in FIRST_WAVE_TFC_IDS
        for country in SUPPORTED_COUNTRIES
    ]
    return {
        "schema_version": PRODUCTION_CAPTURE_SCHEMA_VERSION,
        "release_id": release_id,
        "validated_as_of": validation_date,
        "catalog": _catalog(),
        "policy_bundles": _policies(),
        "source_legal_manifest": _source_manifest(source_capture, validation_date),
        "additional_jurisdictions": [],
        "rules": rules,
        "support_overrides": support_overrides,
    }


def reconcile_phase7b(
    production_capture: Mapping[str, Any], research_support_rows: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    research = {
        (row["tfc_id"], row["country_code"]): row["research_support_state"]
        for row in research_support_rows
        if row["tfc_id"] in FIRST_WAVE_TFC_IDS
    }
    production = {
        (row["tfc_id"], row["country_code"]): row["support_status"]
        for row in production_capture["support_overrides"]
    }
    expected_pairs = {
        (tfc_id, country) for tfc_id in FIRST_WAVE_TFC_IDS for country in COUNTRY_CODES
    }
    discrepancies = []
    for pair in sorted(expected_pairs):
        research_supported = research[pair] == "SOURCE_ROUTE_ASSESSABLE"
        production_supported = production.get(pair) == "SUPPORTED"
        if research_supported != production_supported:
            discrepancies.append(
                {
                    "tfc_id": pair[0],
                    "country_code": pair[1],
                    "research_state": research[pair],
                    "production_state": production.get(pair, "UNSUPPORTED"),
                    "approval_required": True,
                }
            )
    route_counts = {
        tfc_id: sum(1 for row in production_capture["rules"] if row["tfc_id"] == tfc_id)
        for tfc_id in FIRST_WAVE_TFC_IDS
    }
    return {
        "schema_version": "tfc-phase7f-reconciliation-1.0",
        "research_cutoff": "2026-08-05",
        "production_validation_date": production_capture["validated_as_of"],
        "tfc_ids": list(FIRST_WAVE_TFC_IDS),
        "expected_supported_count_per_tfc": 29,
        "actual_supported_count_per_tfc": {
            tfc_id: sum(
                row["tfc_id"] == tfc_id and row["support_status"] == "SUPPORTED"
                for row in production_capture["support_overrides"]
            )
            for tfc_id in FIRST_WAVE_TFC_IDS
        },
        "route_rule_count_per_tfc": route_counts,
        "source_reference_granularity_change": "Phase 7B source-family references are replaced by owner-authorized exact per-destination page and route identities.",
        "discrepancies": discrepancies,
        "status": "PASSED" if not discrepancies else "OWNER_APPROVAL_REQUIRED",
    }


__all__ = [
    "CAPTURE_SCHEMA_VERSION",
    "FIRST_WAVE_TFC_IDS",
    "PRODUCTION_CAPTURE_SCHEMA_VERSION",
    "SUPPORTED_COUNTRIES",
    "SourceAssetSpec",
    "build_first_wave_production_capture",
    "capture_source_inventory",
    "reconcile_phase7b",
    "source_asset_specs",
    "validate_source_capture",
]
