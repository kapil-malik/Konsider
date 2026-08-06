from konsider.api.app import create_app


def test_v3_openapi_uses_uniform_display_properties() -> None:
    document = create_app().openapi()
    assert "/api/v3/catalog" in document["paths"]
    assert "/api/v3/opportunity-filters" in document["paths"]
    assert "/api/v3/tfcs" in document["paths"]
    schemas = document["components"]["schemas"]
    for name in (
        "CatalogCriterionV3Response",
        "OpportunityFilterDefinitionV3Response",
        "TfcDefinitionV3Response",
    ):
        properties = schemas[name]["properties"]
        assert {
            "id",
            "displayName",
            "compactName",
            "sectionId",
            "sectionName",
            "sortOrder",
        } <= properties.keys()
    contribution = schemas["ContributionV3Response"]["properties"]
    comparison = schemas["ComparisonCriterionRowV3Response"]["properties"]
    assert "displayName" in contribution and "criterion_name" not in contribution
    assert "displayName" in comparison and "criterion_name" not in comparison
