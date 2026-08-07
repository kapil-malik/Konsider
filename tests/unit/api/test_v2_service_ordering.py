from konsider.api.v2_service import _criterion_sort_key


def test_criterion_sort_key_prefers_product_display_order_over_id() -> None:
    definitions = [
        {"id": "C01", "sortOrder": 20},
        {"id": "z_named_criterion", "sortOrder": 10},
    ]

    assert [item["id"] for item in sorted(definitions, key=_criterion_sort_key)] == [
        "z_named_criterion",
        "C01",
    ]


def test_criterion_sort_key_keeps_legacy_id_fallback_deterministic() -> None:
    definitions = [{"id": "N1"}, {"id": "L1"}]

    assert [item["id"] for item in sorted(definitions, key=_criterion_sort_key)] == ["L1", "N1"]
