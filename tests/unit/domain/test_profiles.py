from unittest import TestCase

from konsider.domain.profiles import DEFAULT_PROFILES, get_default_profile
from konsider.domain.scoring import normalize_weights
from konsider.repositories.fixture_repository import load_project_data


class DefaultProfileTests(TestCase):
    def test_default_profiles_cover_project_parameters(self):
        data = load_project_data()

        self.assertEqual(len(DEFAULT_PROFILES), 3)
        for profile in DEFAULT_PROFILES.values():
            self.assertEqual(set(profile.weights), set(data.parameters))

    def test_default_profile_weights_can_be_normalized(self):
        data = load_project_data()
        profile = get_default_profile("finance_professional")

        weights = normalize_weights(profile.weights, data.parameters)

        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertGreater(weights["finance_jobs"], weights["university_quality"])

    def test_unknown_default_profile_raises_key_error(self):
        with self.assertRaisesRegex(KeyError, "Unknown default profile"):
            get_default_profile("missing")
