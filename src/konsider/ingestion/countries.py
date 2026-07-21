"""Stable 20-country experiment scope."""

COUNTRIES = {
    "IND": "India",
    "SGP": "Singapore",
    "CAN": "Canada",
    "AUS": "Australia",
    "DEU": "Germany",
    "NLD": "Netherlands",
    "CHE": "Switzerland",
    "USA": "United States",
    "GBR": "United Kingdom",
    "ARE": "United Arab Emirates",
    "FRA": "France",
    "SWE": "Sweden",
    "DNK": "Denmark",
    "NOR": "Norway",
    "IRL": "Ireland",
    "NZL": "New Zealand",
    "JPN": "Japan",
    "KOR": "South Korea",
    "ESP": "Spain",
    "PRT": "Portugal",
}

COUNTRY_ALIASES = {
    "Korea, Rep.": "KOR",
    "South Korea": "KOR",
    "Republic of Korea": "KOR",
    "United States of America": "USA",
    "United Kingdom": "GBR",
    "United Arab Emirates": "ARE",
    "Netherlands": "NLD",
}
COUNTRY_ALIASES.update({name: code for code, name in COUNTRIES.items()})

COUNTRY_CODES = tuple(COUNTRIES)
