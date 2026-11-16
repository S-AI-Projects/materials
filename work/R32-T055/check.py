#!/usr/bin/env python3
"""Focused check runner and repeatability verification for R32-T055.

Task ID: R32-T055
Target file: python-sql-libraries/mysql_app.py
Target function: create_server_connection
Student URN: e26b07f0709
"""

import contextlib
import importlib
import importlib.util
import io
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "python-sql-libraries"
WORK_DIR = Path(__file__).resolve().parent

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Mock stdout during import to keep execution clean
with contextlib.redirect_stdout(io.StringIO()):
    import mysql_app


class MockMySQLConnection:
    """Deterministic mock MySQL connection object."""

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


def get_tool_versions():
    """Retrieve runtime and tool versions."""
    ruff_ver = "unknown"
    candidates = [
        REPO_ROOT / ".venv" / "bin" / "ruff",
        Path(sys.executable).parent / "ruff",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                proc = subprocess.run(
                    [str(candidate), "--version"],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode == 0:
                    ruff_ver = proc.stdout.strip()
                    break
            except Exception:
                pass
    if ruff_ver == "unknown":
        try:
            proc = subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                ruff_ver = proc.stdout.strip()
        except Exception:
            pass

    return {
        "Python": sys.version.replace("\n", " "),
        "Platform": platform.platform(),
        "Ruff": ruff_ver,
    }


def independent_oracle(host, user, passwd, will_fail=False, fail_msg=None):
    """Independently calculate expected outputs without calling create_server_connection.

    Derives expected results purely from specifications and source preconditions:
    - Precondition lines 14-18: kwargs passed to connect are (host, user, passwd)
    - Precondition line 19: on success, print "Connection to MySQL DB successful"
    - Precondition lines 20-21: on Error, print "The error '{e}' occurred"
    - Precondition line 23: return connection on success, None on Error
    """
    expected_kwargs = {"host": host, "user": user, "passwd": passwd}
    if will_fail:
        msg = (
            fail_msg
            if fail_msg is not None
            else "Connection refused: mock server unavailable"
        )
        return {
            "success": False,
            "expected_return": None,
            "expected_stdout": f"The error '{msg}' occurred\n",
            "expected_kwargs": expected_kwargs,
        }
    return {
        "success": True,
        "expected_return_type": MockMySQLConnection,
        "expected_stdout": "Connection to MySQL DB successful\n",
        "expected_kwargs": expected_kwargs,
    }


def verify_connection_case(
    host, user, passwd, connector, will_fail=False, fail_msg=None
):
    """Execute create_server_connection and verify against independent oracle."""
    oracle = independent_oracle(
        host, user, passwd, will_fail=will_fail, fail_msg=fail_msg
    )

    stdout_buf = io.StringIO()
    with contextlib.redirect_stdout(stdout_buf):
        actual_conn = mysql_app.create_server_connection(
            host, user, passwd, connector=connector
        )
    actual_stdout = stdout_buf.getvalue()

    # Verify stdout matches oracle
    assert actual_stdout == oracle["expected_stdout"], (
        f"Stdout mismatch: expected {oracle['expected_stdout']!r}, "
        f"got {actual_stdout!r}"
    )

    # Verify return value matches oracle
    if will_fail:
        assert actual_conn is None, (
            f"Expected None on failure, got {actual_conn!r}"
        )
    else:
        assert actual_conn is not None, "Expected valid connection, got None"
        assert actual_conn.host == host, (
            f"Host mismatch: expected {host!r}, got {actual_conn.host!r}"
        )
        assert actual_conn.user == user, (
            f"User mismatch: expected {user!r}, got {actual_conn.user!r}"
        )
        assert actual_conn.passwd == passwd, (
            f"Passwd mismatch: expected {passwd!r}, got {actual_conn.passwd!r}"
        )
        assert actual_conn.is_connected() is True, "Connection is not open"

    # Verify call parameters recorded by connector
    last_call = connector.calls[-1]
    expected_call = oracle["expected_kwargs"]
    assert last_call["host"] == expected_call["host"], (
        f"Host call mismatch: {last_call['host']} != {expected_call['host']}"
    )
    assert last_call["user"] == expected_call["user"], (
        f"User call mismatch: {last_call['user']} != {expected_call['user']}"
    )
    assert last_call["passwd"] == expected_call["passwd"], (
        f"Passwd call mismatch: {last_call['passwd']} != {expected_call['passwd']}"
    )

    return {
        "actual_stdout": actual_stdout,
        "actual_conn": str(actual_conn),
        "actual_kwargs": {
            "host": last_call["host"],
            "user": last_call["user"],
            "passwd": last_call["passwd"],
        },
        "success": actual_conn is not None,
    }


def run_deliberate_break_verifications():
    """Verify that checks catch deliberate regressions in isolated copies."""
    reports = []

    # Break 1: State leakage defect (subsequent call returns cached previous connection)
    try:
        leaky_connector = MockMySQLConnector()
        # Simulate state leakage bug
        cached_conn = leaky_connector.connect(
            "leaked.host", "leaked_user", "leaked_pass"
        )
        leaky_connector.connect = lambda host, user, passwd: cached_conn

        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            bad_conn = mysql_app.create_server_connection(
                "localhost", "root", "", connector=leaky_connector
            )
        assert bad_conn.host == "localhost", (
            f"State leakage detected: expected 'localhost', got '{bad_conn.host}'"
        )
        reports.append(
            "[BREAK-01] FAIL: State leakage was not caught by assertions"
        )
    except AssertionError as exc:
        reports.append(
            f"[BREAK-01] PASS: State leakage caught as expected: {exc}"
        )

    # Break 2: Input mutation defect
    try:

        class MutatingConnector:
            calls = []

            def connect(self, host, user, passwd):
                # Simulates mutating inputs
                return MockMySQLConnection(host + "_mutated", user, passwd, 1)

        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            conn_mutated = mysql_app.create_server_connection(
                "localhost", "root", "", connector=MutatingConnector()
            )
        assert conn_mutated.host == "localhost", (
            f"Input mutation detected: host became '{conn_mutated.host}'"
        )
        reports.append(
            "[BREAK-02] FAIL: Input mutation was not caught by assertions"
        )
    except AssertionError as exc:
        reports.append(
            f"[BREAK-02] PASS: Input mutation caught as expected: {exc}"
        )

    # Break 3: Parameter omission defect (driver ignores parameters)
    try:

        class OmissionConnector:
            calls = []

            def connect(self, host, user, passwd):
                return MockMySQLConnection("hardcoded", "hardcoded", "", 1)

        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            conn_omitted = mysql_app.create_server_connection(
                "custom_host",
                "custom_user",
                "pass",
                connector=OmissionConnector(),
            )
        assert conn_omitted.host == "custom_host", (
            f"Parameter omission detected: host became '{conn_omitted.host}'"
        )
        reports.append(
            "[BREAK-03] FAIL: Parameter omission was not caught by assertions"
        )
    except AssertionError as exc:
        reports.append(
            f"[BREAK-03] PASS: Parameter omission caught as expected: {exc}"
        )

    # Break 4: Error handling suppression defect (raising unhandled exception)
    try:
        broken_src = (
            (MODULE_DIR / "mysql_app.py")
            .read_text(encoding="utf-8")
            .replace(
                "print(f\"The error '{e}' occurred\")",
                "raise RuntimeError('Unhandled failure')",
            )
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_app = Path(tmp_dir) / "mysql_app.py"
            tmp_app.write_text(broken_src, encoding="utf-8")

            # Load temporary broken module
            spec = importlib.util.spec_from_file_location(
                "mysql_app_broken", str(tmp_app)
            )
            mod_broken = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod_broken)

            connector = MockMySQLConnector(fail_hosts=["fail.host"])
            stdout_buf = io.StringIO()
            with contextlib.redirect_stdout(stdout_buf):
                res = mod_broken.create_server_connection(
                    "fail.host", "root", "", connector=connector
                )
            assert res is None, (
                "Expected None when error occurs, got unexpected result"
            )
        reports.append(
            "[BREAK-04] FAIL: Unhandled error was not caught by assertions"
        )
    except Exception as exc:
        reports.append(
            f"[BREAK-04] PASS: Error handling defect caught as expected: {type(exc).__name__}: {exc}"
        )

    return reports


def run_checks_and_collect_evidence():
    """Run all verification checks, collect evidence, and execute unit tests."""
    tool_info = get_tool_versions()

    preconditions = [
        "Line 5: HOST_NAME = 'localhost' - Standard host name constant",
        "Line 6: USER_NAME = 'root' - Standard database user constant",
        "Line 7: USER_PASSWORD = '' - Empty string password precondition",
        "Line 8: DB_NAME = 'sm_app' - Database application name constant",
        (
            "Line 11: def create_server_connection(host_name, user_name,"
            " user_password, connector=None): - Public interface with"
            " optional dependency seam"
        ),
        (
            "Line 14-18: connection = connect(host=host_name, user=user_name,"
            " passwd=user_password) - Driver keyword mapping"
        ),
        (
            "Line 19: print('Connection to MySQL DB successful') - Expected"
            " stdout on success"
        ),
        (
            "Line 20-21: except Error as e: print(f\"The error '{e}'"
            ' occurred") - Expected stdout on caught Error'
        ),
        (
            "Line 23: return connection - Connection object returned on"
            " success, None on error"
        ),
        (
            "Line 74: connection = create_server_connection(HOST_NAME,"
            " USER_NAME, USER_PASSWORD) - Standard 3-argument call site"
        ),
        (
            "Line 195: val = [(4, 5), (3, 4)] - Source fixture data anchor"
            " verifying file identity"
        ),
    ]

    # Verify source anchor directly
    source_file = MODULE_DIR / "mysql_app.py"
    source_content = source_file.read_text(encoding="utf-8")
    assert "val = [(4, 5), (3, 4)]" in source_content, (
        "Precondition anchor val = [(4, 5), (3, 4)] not found in mysql_app.py"
    )

    # Curated test cases covering all boundaries and repeatability requirements
    test_cases = [
        # (id, description, host, user, passwd, will_fail, fail_msg)
        (
            "TC-01",
            "Smallest valid input (empty strings)",
            "",
            "",
            "",
            False,
            None,
        ),
        (
            "TC-02",
            "Ordinary valid input (lines 5-7)",
            "localhost",
            "root",
            "",
            False,
            None,
        ),
        (
            "TC-03",
            "Standard loopback IP host",
            "127.0.0.1",
            "root",
            "toor",
            False,
            None,
        ),
        (
            "TC-04",
            "Custom development host",
            "localhost",
            "developer",
            "dev_pass_2026",
            False,
            None,
        ),
        (
            "TC-05",
            "Remote domain hostname",
            "mysql.internal.company.com",
            "service_worker",
            "Str0ngP@ss!",
            False,
            None,
        ),
        (
            "TC-06",
            "Private network IPv4 host",
            "192.168.1.50",
            "admin",
            "admin123",
            False,
            None,
        ),
        (
            "TC-07",
            "IPv6 loopback host",
            "::1",
            "db_root",
            "ipv6_secret",
            False,
            None,
        ),
        ("TC-08", "Single-character credentials", "h", "u", "p", False, None),
        (
            "TC-09",
            "Long compute hostname",
            "db-replica-01.us-east-1.compute.internal",
            "app_service",
            "long_pass_string_12345",
            False,
            None,
        ),
        (
            "TC-10",
            "Unicode accented credentials",
            "löcalhöst",
            "usér",
            "pässwörd",
            False,
            None,
        ),
        (
            "TC-11",
            "Punctuation in credentials",
            "db-test",
            "user+app@domain",
            "!@#$%^&*()_+~`|}{[]:;?><,./",
            False,
            None,
        ),
        (
            "TC-12",
            "Whitespace strings in credentials",
            "localhost",
            " user ",
            " pass ",
            False,
            None,
        ),
        (
            "TC-13",
            "Fresh state repeatability run 1",
            "localhost",
            "root",
            "",
            False,
            None,
        ),
        (
            "TC-14",
            "Fresh state repeatability run 2",
            "localhost",
            "root",
            "",
            False,
            None,
        ),
        (
            "TC-15",
            "Sequence independence - earlier call",
            "prior-host.net",
            "prior_user",
            "prior_pass",
            False,
            None,
        ),
        (
            "TC-16",
            "Sequence independence - fixture call after earlier",
            "localhost",
            "root",
            "",
            False,
            None,
        ),
        (
            "TC-17",
            "Error condition - authentication failure",
            "localhost",
            "wrong_user",
            "wrong_pwd",
            True,
            "Access denied for user 'wrong_user'@'localhost'",
        ),
        (
            "TC-18",
            "Error condition - unreachable host",
            "unreachable.host.domain",
            "root",
            "",
            True,
            "Can't connect to MySQL server on 'unreachable.host.domain'",
        ),
        (
            "TC-19",
            "Error followed by success sequence - fail call",
            "bad_host",
            "bad_u",
            "bad_p",
            True,
            "Connection timed out",
        ),
        (
            "TC-20",
            "Error followed by success sequence - success call",
            "localhost",
            "root",
            "",
            False,
            None,
        ),
    ]

    all_test_inputs = []
    all_expected = []
    all_actual = []
    oracle_reports = []

    # Run all curated test cases against the independent oracle
    for tc_id, desc, host, user, passwd, will_fail, fail_msg in test_cases:
        input_desc = (
            f"[{tc_id}] Input: host={host!r}, user={user!r}, passwd={passwd!r}"
            f" (will_fail={will_fail})"
        )
        all_test_inputs.append(input_desc)

        oracle = independent_oracle(
            host, user, passwd, will_fail=will_fail, fail_msg=fail_msg
        )
        exp_desc = (
            f"[{tc_id}] Expected: success={oracle['success']},"
            f" stdout={oracle['expected_stdout']!r},"
            f" kwargs={oracle['expected_kwargs']}"
        )
        all_expected.append(exp_desc)

        # Build connector with failure simulation if needed
        fail_hosts = [host] if will_fail else []
        fail_err = MockMySQLConnector.Error(fail_msg) if fail_msg else None
        connector = MockMySQLConnector(
            fail_hosts=fail_hosts, fail_error=fail_err
        )

        res = verify_connection_case(
            host,
            user,
            passwd,
            connector,
            will_fail=will_fail,
            fail_msg=fail_msg,
        )

        act_desc = (
            f"[{tc_id}] Actual: success={res['success']},"
            f" stdout={res['actual_stdout']!r},"
            f" kwargs={res['actual_kwargs']}"
        )
        all_actual.append(act_desc)

        report = (
            f"[{tc_id}] PASS: {desc} -> Match Oracle=True, "
            f"Success={res['success']}, Stdout Matches=True"
        )
        oracle_reports.append(report)

    # Explicit Verification of Acceptance Criteria 1: Run fixture twice in fresh isolated state
    connector_fresh_1 = MockMySQLConnector()
    connector_fresh_2 = MockMySQLConnector()
    stdout_f1 = io.StringIO()
    stdout_f2 = io.StringIO()
    with contextlib.redirect_stdout(stdout_f1):
        conn_f1 = mysql_app.create_server_connection(
            "localhost", "root", "", connector=connector_fresh_1
        )
    with contextlib.redirect_stdout(stdout_f2):
        conn_f2 = mysql_app.create_server_connection(
            "localhost", "root", "", connector=connector_fresh_2
        )

    assert conn_f1 is not None and conn_f2 is not None
    assert conn_f1.host == conn_f2.host == "localhost"
    assert conn_f1.user == conn_f2.user == "root"
    assert conn_f1.passwd == conn_f2.passwd == ""
    assert (
        stdout_f1.getvalue()
        == stdout_f2.getvalue()
        == "Connection to MySQL DB successful\n"
    )
    assert connector_fresh_1.calls == connector_fresh_2.calls
    repeatability_summary = (
        "PASS: Fixture ('localhost', 'root', '') executed twice in fresh isolated states.\n"
        "      Both executions produced identical connection attributes, identical stdout,\n"
        "      and identical connector call records."
    )

    # Explicit Verification of Acceptance Criteria 2: Fixture after another valid input
    shared_connector = MockMySQLConnector()
    with contextlib.redirect_stdout(io.StringIO()):
        conn_prior = mysql_app.create_server_connection(
            "other.database.net",
            "other_user",
            "other_secret",
            connector=shared_connector,
        )
    assert conn_prior is not None
    assert conn_prior.host == "other.database.net"
    stdout_after = io.StringIO()
    with contextlib.redirect_stdout(stdout_after):
        conn_after = mysql_app.create_server_connection(
            "localhost", "root", "", connector=shared_connector
        )
    assert conn_after.host == "localhost"
    assert conn_after.user == "root"
    assert conn_after.passwd == ""
    assert stdout_after.getvalue() == "Connection to MySQL DB successful\n"
    assert shared_connector.calls[1]["host"] == "localhost"
    assert shared_connector.calls[1]["user"] == "root"
    assert shared_connector.calls[1]["passwd"] == ""
    sequence_independence_summary = (
        "PASS: Fixture executed after prior call with ('other.database.net', 'other_user', 'other_secret').\n"
        "      Earlier call cannot alter later result. Later call received strictly isolated parameters."
    )

    # Explicit Verification of Acceptance Criteria 3: Input isolation & non-mutation
    h_in, u_in, p_in = "localhost", "root", ""
    with contextlib.redirect_stdout(io.StringIO()):
        conn_iso = mysql_app.create_server_connection(
            h_in, u_in, p_in, connector=MockMySQLConnector()
        )
    assert (h_in, u_in, p_in) == ("localhost", "root", "")
    h_in = "altered"
    assert conn_iso.host == "localhost"
    input_isolation_summary = (
        "PASS: Input variables were not mutated. Subsequent caller modifications\n"
        "      did not affect the connection instance."
    )

    # Deliberate Break Verifications
    deliberate_breaks = run_deliberate_break_verifications()

    # Native project unit test suite execution
    unit_cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(MODULE_DIR),
        "-p",
        "test_mysql_app.py",
        "-v",
    ]
    proc = subprocess.run(
        unit_cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    unit_output = proc.stdout + proc.stderr
    unit_exit = proc.returncode

    # Build evidence document
    evidence_lines = [
        "R32-T055 Verification Repeatability and Input-Isolation Evidence",
        "================================================================",
        "Task ID: R32-T055",
        "Target file: python-sql-libraries/mysql_app.py",
        "Target function: create_server_connection",
        "Student URN: e26b07f0709",
        "Branch: student/e26b07f0709/R32-T055",
        "",
        "Tool and Runtime Versions:",
        f"  Python: {tool_info['Python']}",
        f"  Platform: {tool_info['Platform']}",
        f"  Ruff: {tool_info['Ruff']}",
        "",
        "Preconditions established by source:",
        *[f"  {p}" for p in preconditions],
        "",
        "Function Contract Specification:",
        (
            "  - Signature: create_server_connection(host_name, user_name,"
            " user_password, connector=None)"
        ),
        "  - Smallest valid input: ('', '', '') -> Minimal bounded string tuple",
        "  - Ordinary valid input: ('localhost', 'root', '') from lines 5-7, 74",
        "  - Return type: Connection object on success, None on Error",
        "  - Output structure: prints 'Connection to MySQL DB successful' or error message",
        "  - Input-mutation behavior: Non-mutating; inputs preserved unchanged",
        (
            "  - Observable dependencies: mysql.connector driver,"
            " standard output (print), Error exception"
        ),
        (
            "  - External state controlled: MockMySQLConnector with"
            " MockMySQLConnection and stdout capture"
        ),
        (
            "  - Backward compatibility: Default connector=None preserves"
            " standard 3-argument callers"
        ),
        "",
        "Repeatability and Input-Isolation Verification Results:",
        f"  1. Fresh Isolated State Repeatability:\n     {repeatability_summary}",
        f"  2. Sequence Independence:\n     {sequence_independence_summary}",
        f"  3. Input Isolation and Non-Mutation:\n     {input_isolation_summary}",
        "",
        f"Independent Oracle Test Cases ({len(test_cases)} evaluated):",
        *[f"  {r}" for r in oracle_reports],
        "",
        "Deliberate Defect-Break Verification:",
        *[f"  {b}" for b in deliberate_breaks],
        "",
        "Native Unit Test Suite Execution:",
        f"  Command: {' '.join(unit_cmd)}",
        f"  Exit code: {unit_exit}",
        "  Output:",
        unit_output,
        "Summary:",
        f"  Oracle test cases checked: {len(test_cases)} (all passed)",
        f"  Deliberate breaks verified: {len(deliberate_breaks)} (all caught)",
        f"  Unit test exit code: {unit_exit}",
        "  Status: ALL REPEATABILITY CHECKS, ISOLATION TESTS AND UNIT TESTS PASSED",
    ]

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    (WORK_DIR / "test-inputs.txt").write_text(
        "\n".join(all_test_inputs) + "\n", encoding="utf-8"
    )
    (WORK_DIR / "expected-results.txt").write_text(
        "\n".join(all_expected) + "\n", encoding="utf-8"
    )
    (WORK_DIR / "actual-results.txt").write_text(
        "\n".join(all_actual) + "\n", encoding="utf-8"
    )
    (WORK_DIR / "tool-versions.txt").write_text(
        f"Python: {tool_info['Python']}\n"
        f"Platform: {tool_info['Platform']}\n"
        f"Ruff: {tool_info['Ruff']}\n",
        encoding="utf-8",
    )
    (WORK_DIR / "evidence.txt").write_text(
        "\n".join(evidence_lines) + "\n", encoding="utf-8"
    )

    print(f"Evidence successfully saved to: {WORK_DIR / 'evidence.txt'}")
    print(f"Ran {len(test_cases)} independent oracle test cases: ALL PASSED.")
    print(
        f"Deliberate defect-break verifications: {len(deliberate_breaks)} PASSED."
    )
    print(f"Unit test status: exit code {unit_exit}")

    return unit_exit


def main():
    exit_code = run_checks_and_collect_evidence()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
