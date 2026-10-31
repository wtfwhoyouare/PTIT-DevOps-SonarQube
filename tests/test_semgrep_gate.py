import json
import os
from pathlib import Path
import tempfile
import unittest

from ci import semgrep_gate


class SemgrepGateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_path = Path(self.temp_dir.name) / "semgrep.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_gate_passes_when_no_errors(self):
        data = {
            "results": [
                {
                    "check_id": "test-warning",
                    "path": "test.php",
                    "start": {"line": 10},
                    "extra": {
                        "severity": "WARNING",
                        "message": "Potential warning",
                        "metadata": {"cwe": "CWE-20"},
                    },
                }
            ]
        }
        self.json_path.write_text(json.dumps(data), encoding="utf-8")
        code = semgrep_gate.evaluate_gate(self.json_path)
        self.assertEqual(code, 0)

    def test_gate_fails_when_errors_detected_and_enforced(self):
        data = {
            "results": [
                {
                    "check_id": "tainted-sql",
                    "path": "InlaneWeb/web/src/pages/login.php",
                    "start": {"line": 19},
                    "extra": {
                        "severity": "ERROR",
                        "message": "SQL Injection detected",
                        "metadata": {"cwe": "CWE-89"},
                    },
                }
            ]
        }
        self.json_path.write_text(json.dumps(data), encoding="utf-8")
        with unittest.mock.patch.dict(os.environ, {"ENFORCE_SECURITY_GATE": "true"}):
            code = semgrep_gate.evaluate_gate(self.json_path)
            self.assertEqual(code, 1)

    def test_gate_passes_in_report_only_mode(self):
        data = {
            "results": [
                {
                    "check_id": "tainted-sql",
                    "path": "InlaneWeb/web/src/pages/login.php",
                    "start": {"line": 19},
                    "extra": {
                        "severity": "ERROR",
                        "message": "SQL Injection detected",
                        "metadata": {"cwe": "CWE-89"},
                    },
                }
            ]
        }
        self.json_path.write_text(json.dumps(data), encoding="utf-8")
        with unittest.mock.patch.dict(os.environ, {"ENFORCE_SECURITY_GATE": "false"}):
            code = semgrep_gate.evaluate_gate(self.json_path)
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()

