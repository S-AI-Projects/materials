"""Unit tests for consuming-apis-python/github.py focusing on create_oauth_link repeatability and isolation.

Precondition Anchors:
- Lines 19-24:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "user",
        "response_type": "code",
    }
- Line 51:
    headers = {"Accept": "application/json"}
"""

import pathlib
import sys
import unittest
from unittest.mock import MagicMock
from urllib.parse import urlencode

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import github


class MockResponse:
    def __init__(self, url):
        self.url = url


class MockSession:
    def __init__(self):
        self.call_history = []

    def get(self, endpoint, params=None):
        query_string = urlencode(params or {})
        full_url = f"{endpoint}?{query_string}"
        self.call_history.append((endpoint, params, full_url))
        return MockResponse(full_url)


class TestCreateOAuthLinkRepeatability(unittest.TestCase):
    def test_precondition_anchors_and_defaults(self):
        """Line 19-24 precondition: default parameters preserve module constants."""
        mock_session = MockSession()
        url = github.create_oauth_link(session=mock_session)
        endpoint, params, full_url = mock_session.call_history[0]
        self.assertEqual(endpoint, "https://github.com/login/oauth/authorize")
        self.assertEqual(params["client_id"], github.CLIENT_ID)
        self.assertEqual(params["redirect_uri"], github.REDIRECT_URI)
        self.assertEqual(params["scope"], "user")
        self.assertEqual(params["response_type"], "code")
        self.assertEqual(url, full_url)

    def test_smallest_valid_input(self):
        """Smallest valid input boundary: empty strings for client_id, redirect_uri, scope, and response_type."""
        mock_session = MockSession()
        expected = "https://github.com/login/oauth/authorize?client_id=&redirect_uri=&scope=&response_type="
        actual = github.create_oauth_link(
            client_id="",
            redirect_uri="",
            scope="",
            response_type="",
            session=mock_session,
        )
        self.assertEqual(actual, expected)

    def test_ordinary_fixture_input(self):
        """Ordinary fixture input: standard OAuth client configuration."""
        mock_session = MockSession()
        client_id = "test-client-987"
        redirect_uri = "https://myapp.local/oauth/callback"
        expected = (
            "https://github.com/login/oauth/authorize?"
            "client_id=test-client-987&redirect_uri=https%3A%2F%2Fmyapp.local%2Foauth%2Fcallback&scope=user&response_type=code"
        )
        actual = github.create_oauth_link(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope="user",
            response_type="code",
            session=mock_session,
        )
        self.assertEqual(actual, expected)

    def test_repeatability_and_state_isolation(self):
        """Repeatability: running the same fixture twice in isolated states and once after another input yields identical outputs."""
        session1 = MockSession()
        session2 = MockSession()

        # Run 1: initial run in fresh state
        res1 = github.create_oauth_link(
            client_id="rep-client",
            redirect_uri="https://rep.org/cb",
            session=session1,
        )

        # Run 2: intermediate run with completely different inputs
        res_inter = github.create_oauth_link(
            client_id="other-client",
            redirect_uri="https://other.org/cb",
            scope="repo",
            session=session1,
        )
        self.assertNotEqual(res1, res_inter)

        # Run 3: repeating input on session1 (after intermediate run)
        res3 = github.create_oauth_link(
            client_id="rep-client",
            redirect_uri="https://rep.org/cb",
            session=session1,
        )
        self.assertEqual(res1, res3, "Intermediate run must not alter subsequent results on same session")

        # Run 4: repeating input in a fresh isolated session2
        res4 = github.create_oauth_link(
            client_id="rep-client",
            redirect_uri="https://rep.org/cb",
            session=session2,
        )
        self.assertEqual(res1, res4, "Fresh session execution must be strictly repeatable")


if __name__ == "__main__":
    unittest.main()
