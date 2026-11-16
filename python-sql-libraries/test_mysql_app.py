#!/usr/bin/env python3
"""Repeatability and input-isolation tests for create_server_connection.

Task ID: R32-T055
Target: python-sql-libraries/mysql_app.py
Target function: create_server_connection

Preconditions established by source:
    Line 5: HOST_NAME = "localhost" establishes standard host name.
    Line 6: USER_NAME = "root" establishes standard database user.
    Line 7: USER_PASSWORD = "" establishes standard password and confirms
            empty string is a valid credential parameter.
    Line 8: DB_NAME = "sm_app" establishes default application database.
    Line 11: def create_server_connection(host_name, user_name, user_password,
             connector=None): establishes public interface.
    Line 14-18: connection = connect(host=host_name, user=user_name,
                passwd=user_password) establishes driver parameter mapping.
    Line 19: print("Connection to MySQL DB successful") establishes success
             stdout.
    Line 20-21: except Error as e: print(f"The error '{e}' occurred")
                establishes error stdout.
    Line 23: return connection establishes return value contract.
    Line 74: connection = create_server_connection(HOST_NAME, USER_NAME,
             USER_PASSWORD) establishes ordinary call site.
    Line 195: val = [(4, 5), (3, 4)] establishes data anchor verifying
              source fixture identity.
"""

import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "python-sql-libraries"
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import mysql_app  # noqa: E402


class MockMySQLConnection:
    """Deterministic in-memory mock MySQL connection object."""

    def __init__(self, host, user, passwd, connection_id=1):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.connection_id = connection_id
        self._connected = True

    def is_connected(self):
        """Return connection status."""
        return self._connected

    def close(self):
        """Close connection."""
        self._connected = False


class MockMySQLConnector:
    """Deterministic mock connector providing connect() and Error."""

    class Error(Exception):
        """Connector exception matching mysql.connector.Error interface."""

        pass

    def __init__(self, fail_hosts=None, fail_error=None):
        self.calls = []
        self.fail_hosts = set(fail_hosts or [])
        self.fail_error = (
            fail_error
            if fail_error is not None
            else self.Error("Connection refused: mock server unavailable")
        )
        self._counter = 0

    def connect(self, host, user, passwd):
        """Record parameters and return MockMySQLConnection or raise Error."""
        self._counter += 1
        record = {
            "call_index": self._counter,
            "host": host,
            "user": user,
            "passwd": passwd,
        }
        self.calls.append(record)
        if host in self.fail_hosts:
            raise self.fail_error
        return MockMySQLConnection(
            host=host,
            user=user,
            passwd=passwd,
            connection_id=self._counter,
        )


class TestPreconditionsAndAnchors(unittest.TestCase):
    """Verify preconditions and source anchors established in mysql_app.py."""

    def test_precondition_constants_and_data_anchor(self):
        """Verify module constants and line 195 anchor val = [(4, 5), (3, 4)]."""
        self.assertEqual(mysql_app.HOST_NAME, "localhost")
        self.assertEqual(mysql_app.USER_NAME, "root")
        self.assertEqual(mysql_app.USER_PASSWORD, "")
        self.assertEqual(mysql_app.DB_NAME, "sm_app")

        # Source anchor verification
        source_path = MODULE_DIR / "mysql_app.py"
        source_text = source_path.read_text(encoding="utf-8")
        expected_anchor = "val = [(4, 5), (3, 4)]"
        self.assertIn(
            expected_anchor,
            source_text,
            f"Expected anchor '{expected_anchor}' not found in mysql_app.py",
        )


class TestSmallestAndOrdinaryInputs(unittest.TestCase):
    """Verify smallest valid input and ordinary valid input."""

    def test_smallest_valid_input(self):
        """Verify smallest valid input: empty strings ('', '', '')."""
        connector = MockMySQLConnector()
        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            conn = mysql_app.create_server_connection(
                "", "", "", connector=connector
            )

        self.assertIsNotNone(conn)
        self.assertEqual(conn.host, "")
        self.assertEqual(conn.user, "")
        self.assertEqual(conn.passwd, "")
        self.assertTrue(conn.is_connected())
        self.assertEqual(
            stdout_buf.getvalue(),
            "Connection to MySQL DB successful\n",
        )
        self.assertEqual(len(connector.calls), 1)
        self.assertEqual(
            connector.calls[0],
            {"call_index": 1, "host": "", "user": "", "passwd": ""},
        )

    def test_ordinary_valid_input(self):
        """Verify ordinary valid input from lines 5-7: ('localhost', 'root', '')."""
        connector = MockMySQLConnector()
        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            conn = mysql_app.create_server_connection(
                "localhost", "root", "", connector=connector
            )

        self.assertIsNotNone(conn)
        self.assertEqual(conn.host, "localhost")
        self.assertEqual(conn.user, "root")
        self.assertEqual(conn.passwd, "")
        self.assertTrue(conn.is_connected())
        self.assertEqual(
            stdout_buf.getvalue(),
            "Connection to MySQL DB successful\n",
        )
        self.assertEqual(len(connector.calls), 1)
        self.assertEqual(
            connector.calls[0],
            {
                "call_index": 1,
                "host": "localhost",
                "user": "root",
                "passwd": "",
            },
        )


class TestRepeatabilityFreshState(unittest.TestCase):
    """Verify repeatability when running identical fixture in fresh isolated state."""

    def test_repeatable_in_fresh_isolated_state(self):
        """Verify running fixture twice in fresh isolated state produces equivalent results."""
        # Execution 1 in fresh isolated state 1
        connector_1 = MockMySQLConnector()
        stdout_1 = io.StringIO()
        with contextlib.redirect_stdout(stdout_1):
            conn_1 = mysql_app.create_server_connection(
                "localhost", "root", "", connector=connector_1
            )

        # Execution 2 in fresh isolated state 2
        connector_2 = MockMySQLConnector()
        stdout_2 = io.StringIO()
        with contextlib.redirect_stdout(stdout_2):
            conn_2 = mysql_app.create_server_connection(
                "localhost", "root", "", connector=connector_2
            )

        # Assert equivalent connection attributes and outputs
        self.assertIsNotNone(conn_1)
        self.assertIsNotNone(conn_2)
        self.assertEqual(conn_1.host, conn_2.host)
        self.assertEqual(conn_1.user, conn_2.user)
        self.assertEqual(conn_1.passwd, conn_2.passwd)
        self.assertEqual(conn_1.is_connected(), conn_2.is_connected())
        self.assertEqual(stdout_1.getvalue(), stdout_2.getvalue())
        self.assertEqual(
            stdout_1.getvalue(), "Connection to MySQL DB successful\n"
        )
        self.assertEqual(connector_1.calls, connector_2.calls)


class TestSequenceIndependence(unittest.TestCase):
    """Verify earlier executions cannot alter subsequent results."""

    def test_fixture_after_another_valid_input(self):
        """Verify earlier execution with different input cannot alter subsequent fixture call."""
        connector = MockMySQLConnector()

        # Step 1: Execute with distinct earlier input
        stdout_earlier = io.StringIO()
        with contextlib.redirect_stdout(stdout_earlier):
            conn_earlier = mysql_app.create_server_connection(
                "remote.database.org",
                "service_user",
                "s3cr3t_p@ss",
                connector=connector,
            )

        self.assertIsNotNone(conn_earlier)
        self.assertEqual(conn_earlier.host, "remote.database.org")
        self.assertEqual(conn_earlier.user, "service_user")
        self.assertEqual(conn_earlier.passwd, "s3cr3t_p@ss")

        # Step 2: Execute standard fixture after the earlier call on same connector
        stdout_later = io.StringIO()
        with contextlib.redirect_stdout(stdout_later):
            conn_later = mysql_app.create_server_connection(
                "localhost", "root", "", connector=connector
            )

        # Assert that later call produces exact expected fixture result without state bleed
        self.assertIsNotNone(conn_later)
        self.assertEqual(conn_later.host, "localhost")
        self.assertEqual(conn_later.user, "root")
        self.assertEqual(conn_later.passwd, "")
        self.assertEqual(
            stdout_later.getvalue(), "Connection to MySQL DB successful\n"
        )
        self.assertEqual(
            connector.calls[1],
            {
                "call_index": 2,
                "host": "localhost",
                "user": "root",
                "passwd": "",
            },
        )


class TestInputIsolationAndNonMutation(unittest.TestCase):
    """Verify input isolation and that inputs are not mutated."""

    def test_inputs_not_mutated(self):
        """Verify string input parameters are not modified."""
        host = "localhost"
        user = "root"
        passwd = ""
        connector = MockMySQLConnector()

        with contextlib.redirect_stdout(io.StringIO()):
            conn = mysql_app.create_server_connection(
                host, user, passwd, connector=connector
            )

        self.assertIsNotNone(conn)
        self.assertEqual(host, "localhost")
        self.assertEqual(user, "root")
        self.assertEqual(passwd, "")

    def test_caller_mutation_isolation(self):
        """Verify subsequent modifications to caller variables do not alter connection."""
        host_var = "localhost"
        user_var = "root"
        passwd_var = ""
        connector = MockMySQLConnector()

        with contextlib.redirect_stdout(io.StringIO()):
            conn = mysql_app.create_server_connection(
                host_var, user_var, passwd_var, connector=connector
            )

        # Mutate caller variables
        host_var = "mutated_host"
        user_var = "mutated_user"
        passwd_var = "mutated_pass"

        self.assertEqual(conn.host, "localhost")
        self.assertEqual(conn.user, "root")
        self.assertEqual(conn.passwd, "")

    def test_cross_connection_isolation(self):
        """Verify distinct connections remain isolated without cross-talk."""
        connector = MockMySQLConnector()
        with contextlib.redirect_stdout(io.StringIO()):
            conn_a = mysql_app.create_server_connection(
                "host_a", "user_a", "pass_a", connector=connector
            )
            conn_b = mysql_app.create_server_connection(
                "host_b", "user_b", "pass_b", connector=connector
            )

        self.assertNotEqual(conn_a.host, conn_b.host)
        self.assertNotEqual(conn_a.user, conn_b.user)
        self.assertNotEqual(conn_a.passwd, conn_b.passwd)
        self.assertNotEqual(conn_a.connection_id, conn_b.connection_id)


class TestRepeatedCallBehavior(unittest.TestCase):
    """Verify behavior under repeated consecutive calls."""

    def test_repeated_identical_calls(self):
        """Verify N consecutive calls produce identical deterministic outputs."""
        connector = MockMySQLConnector()
        results = []

        for _ in range(10):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                conn = mysql_app.create_server_connection(
                    "localhost", "root", "", connector=connector
                )
            results.append((conn, buf.getvalue()))

        self.assertEqual(len(results), 10)
        self.assertEqual(len(connector.calls), 10)

        for i, (conn, out) in enumerate(results, start=1):
            self.assertIsNotNone(conn)
            self.assertEqual(conn.host, "localhost")
            self.assertEqual(conn.user, "root")
            self.assertEqual(conn.passwd, "")
            self.assertEqual(conn.connection_id, i)
            self.assertEqual(out, "Connection to MySQL DB successful\n")

    def test_alternating_inputs(self):
        """Verify alternating smallest and ordinary inputs remain strictly isolated."""
        connector = MockMySQLConnector()
        inputs = [
            ("", "", ""),
            ("localhost", "root", ""),
            ("", "", ""),
            ("localhost", "root", ""),
        ]

        for host, user, passwd in inputs:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                conn = mysql_app.create_server_connection(
                    host, user, passwd, connector=connector
                )
            self.assertIsNotNone(conn)
            self.assertEqual(conn.host, host)
            self.assertEqual(conn.user, user)
            self.assertEqual(conn.passwd, passwd)
            self.assertEqual(
                buf.getvalue(), "Connection to MySQL DB successful\n"
            )


class TestExternalDependencyControl(unittest.TestCase):
    """Verify external dependency control, mocking, and caller backward compatibility."""

    def test_dependency_injection_with_callable(self):
        """Verify dependency injection using a callable factory function."""
        recorded = []

        def custom_factory(host, user, passwd):
            recorded.append({"h": host, "u": user, "p": passwd})
            return MockMySQLConnection(host, user, passwd, connection_id=99)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            conn = mysql_app.create_server_connection(
                "custom.host",
                "custom_user",
                "custom_pass",
                connector=custom_factory,
            )

        self.assertIsNotNone(conn)
        self.assertEqual(conn.connection_id, 99)
        self.assertEqual(len(recorded), 1)
        self.assertEqual(
            recorded[0],
            {"h": "custom.host", "u": "custom_user", "p": "custom_pass"},
        )
        self.assertEqual(buf.getvalue(), "Connection to MySQL DB successful\n")

    def test_default_connector_backward_compatibility(self):
        """Verify callers passing 3 positional arguments use default connector."""
        mock_connect = MagicMock(
            return_value=MockMySQLConnection("localhost", "root", "", 101)
        )
        with patch.object(mysql_app.mysql.connector, "connect", mock_connect):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                # Standard 3-argument call as on line 74
                conn = mysql_app.create_server_connection(
                    "localhost", "root", ""
                )

        self.assertIsNotNone(conn)
        self.assertEqual(conn.connection_id, 101)
        mock_connect.assert_called_once_with(
            host="localhost",
            user="root",
            passwd="",
        )
        self.assertEqual(buf.getvalue(), "Connection to MySQL DB successful\n")


class TestErrorHandlingRepeatability(unittest.TestCase):
    """Verify error handling, resilience, and isolation on failures."""

    def test_connection_error_handling(self):
        """Verify caught Error prints message and returns None."""
        connector = MockMySQLConnector(
            fail_hosts=["failing.host"],
            fail_error=MockMySQLConnector.Error(
                "Access denied for user 'root'@'localhost'"
            ),
        )

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            conn = mysql_app.create_server_connection(
                "failing.host", "root", "wrong_pass", connector=connector
            )

        self.assertIsNone(conn)
        expected_msg = (
            "The error 'Access denied for user 'root'@'localhost'' occurred\n"
        )
        self.assertEqual(buf.getvalue(), expected_msg)

    def test_error_followed_by_success_isolation(self):
        """Verify a failed connection does not corrupt subsequent successful connections."""
        connector = MockMySQLConnector(fail_hosts=["bad.host"])

        # Call 1 fails
        buf_fail = io.StringIO()
        with contextlib.redirect_stdout(buf_fail):
            conn_fail = mysql_app.create_server_connection(
                "bad.host", "root", "", connector=connector
            )
        self.assertIsNone(conn_fail)

        # Call 2 succeeds
        buf_success = io.StringIO()
        with contextlib.redirect_stdout(buf_success):
            conn_success = mysql_app.create_server_connection(
                "localhost", "root", "", connector=connector
            )

        self.assertIsNotNone(conn_success)
        self.assertEqual(conn_success.host, "localhost")
        self.assertEqual(
            buf_success.getvalue(), "Connection to MySQL DB successful\n"
        )


if __name__ == "__main__":
    unittest.main()
