import copy
import json
from pathlib import Path

import pytest

from konsider.contracts import ContractError, validate_contract

ROOT = Path(__file__).resolve().parents[2]


def test_published_score_and_observation_validate() -> None:
    release = ROOT / "data" / "releases" / "2026-07-21.1"
    score = json.loads((release / "scores.jsonl").read_text(encoding="utf-8").splitlines()[0])
    observation = json.loads(
        (release / "observations.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )

    validate_contract(score, "metric-score", context="score")
    validate_contract(observation, "metric-observation", context="observation")


@pytest.mark.parametrize(
    ("schema_name", "filename", "field", "value"),
    [
        ("metric-score", "scores.jsonl", "score", 11),
        ("metric-score", "scores.jsonl", "country_code", None),
        ("metric-observation", "observations.jsonl", "source_records", []),
    ],
)
def test_representative_contract_failures(schema_name, filename, field, value) -> None:
    path = ROOT / "data" / "releases" / "2026-07-21.1" / filename
    payload = copy.deepcopy(json.loads(path.read_text(encoding="utf-8").splitlines()[0]))
    if value is None:
        payload.pop(field)
    else:
        payload[field] = value

    with pytest.raises(ContractError):
        validate_contract(payload, schema_name, context=filename)
