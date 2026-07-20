import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from konsider.ingestion.registry import SOURCES
from konsider.ingestion.worker import _fetch_registration
from konsider.repositories.raw_artifact_repository import RawArtifactRepository


class WorkerPaginationTests(TestCase):
    def test_odata_pagination_stops_on_empty_without_capturing_empty_page(self):
        calls = []
        full_page = {"value": [{"SpatialDim": "IND", "TimeDim": 2023}] * 1000}

        def fetcher(url):
            calls.append(url)
            payload = full_page if "%24skip=0" in url else {"value": []}
            return json.dumps(payload).encode(), url, "application/json", {"http_status": 200}

        with TemporaryDirectory() as directory:
            registration = replace(
                SOURCES["world_bank_pm25"], pagination="odata_skip_until_empty",
                download_urls=("https://example.test/api?%24top=1000&%24skip=0",),
            )
            artifacts, bodies = _fetch_registration(
                registration, RawArtifactRepository(Path(directory)), fetcher,
                "2026-07-18T00:00:00+00:00",
            )
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(len(bodies), 1)
        self.assertIn("%24skip=1000", calls[1])

    def test_odata_pagination_prefers_documented_next_link(self):
        calls = []
        continuation = "https://example.test/api?token=next"

        def fetcher(url):
            calls.append(url)
            payload = {"value": [{"SpatialDim": "IND"}], "@odata.nextLink": continuation} if len(calls) == 1 else {"value": []}
            return json.dumps(payload).encode(), url, "application/json", {"http_status": 200}

        with TemporaryDirectory() as directory:
            registration = replace(
                SOURCES["world_bank_pm25"], pagination="odata_skip_until_empty",
                download_urls=("https://example.test/api?%24top=1000&%24skip=0",),
            )
            artifacts, _ = _fetch_registration(
                registration, RawArtifactRepository(Path(directory)), fetcher,
                "2026-07-20T00:00:00+00:00",
            )

        self.assertEqual(calls, [registration.download_urls[0], continuation])
        self.assertEqual(len(artifacts), 1)
