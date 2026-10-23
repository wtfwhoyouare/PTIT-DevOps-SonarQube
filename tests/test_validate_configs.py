import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ci")))
import validate_configs


class ValidateConfigsTests(unittest.TestCase):
    def test_all_monitoring_configs_are_valid(self):
        exit_code = validate_configs.main()
        self.assertEqual(exit_code, 0, "Cấu hình monitoring phải hợp lệ 100%")


if __name__ == "__main__":
    unittest.main()
