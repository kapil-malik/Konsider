import json
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
            artifacts, bodies = _fetch_registration(
                SOURCES["who_air_quality"], RawArtifactRepository(Path(directory)), fetcher,
                "2026-07-18T00:00:00+00:00",
            )
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(len(bodies), 1)
        self.assertIn("%24skip=1000", calls[1])

