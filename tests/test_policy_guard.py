import unittest
from ci.policy_guard import (
    validate_commit_message,
    validate_push_event,
    validate_pull_request_event,
)


class PolicyGuardTests(unittest.TestCase):
    def test_valid_commit_messages(self):
        valid_cases = [
            "feat(auth): thêm cơ chế đăng nhập",
            "fix(db): khắc phục timeout kết nối",
            "sec(sqli): chuyển đổi câu lệnh sang prepared statement",
            "ci(docker): bổ sung cổng smoke test kiểm tra healthcheck",
            "docs(policy): cập nhật tài liệu quy tắc triển khai",
            "refactor(layout): tách header dùng chung",
            "test(ci): bổ sung unit test cho policy guard",
            "chore: dọn dẹp các tệp tạm",
            "Merge pull request #10 from wtfwhoyouare/namng",
            "Merge branch 'dev' into namng",
        ]
        for msg in valid_cases:
            valid, _ = validate_commit_message(msg)
            self.assertTrue(valid, f"Expected '{msg}' to be valid")

    def test_invalid_commit_messages(self):
        invalid_cases = [
            "fixed bug login",
            "update code",
            "fix login without colon",
            "random commit text",
            "",
        ]
        for msg in invalid_cases:
            valid, reason = validate_commit_message(msg)
            self.assertFalse(valid, f"Expected '{msg}' to be invalid")
            self.assertTrue(len(reason) > 0)

    def test_push_event_with_invalid_commit(self):
        event = {
            "ref": "refs/heads/namng",
            "commits": [
                {"id": "abc123456", "message": "feat(auth): login ok"},
                {"id": "def789012", "message": "bad commit message"},
            ],
        }
        ret = validate_push_event(event)
        self.assertEqual(ret, 1)

    def test_push_event_with_valid_commits(self):
        event = {
            "ref": "refs/heads/namng",
            "commits": [
                {"id": "abc123456", "message": "feat(auth): login ok"},
                {"id": "def789012", "message": "docs(readme): update guide"},
            ],
        }
        ret = validate_push_event(event)
        self.assertEqual(ret, 0)

    def test_pr_to_dev_valid_title(self):
        event = {
            "pull_request": {
                "base": {"ref": "dev"},
                "head": {"ref": "namng"},
                "title": "[namng] feat(db): bổ sung endpoint healthcheck",
            }
        }
        ret = validate_pull_request_event(event)
        self.assertEqual(ret, 0)

    def test_pr_to_dev_invalid_title(self):
        event = {
            "pull_request": {
                "base": {"ref": "dev"},
                "head": {"ref": "namng"},
                "title": "feat(db): missing username prefix",
            }
        }
        ret = validate_pull_request_event(event)
        self.assertEqual(ret, 1)

    def test_pr_to_main_invalid_head(self):
        event = {
            "pull_request": {
                "base": {"ref": "main"},
                "head": {"ref": "namng"},
                "title": "release: v1.0.0 - Production Launch",
            }
        }
        ret = validate_pull_request_event(event)
        self.assertEqual(ret, 1)

    def test_pr_to_main_valid_release(self):
        event = {
            "pull_request": {
                "base": {"ref": "main"},
                "head": {"ref": "dev"},
                "title": "release: v1.0.0 - Triển khai cổng thông tin Logistics lên Production",
            }
        }
        ret = validate_pull_request_event(event)
        self.assertEqual(ret, 0)

    def test_pr_to_main_invalid_release_title(self):
        event = {
            "pull_request": {
                "base": {"ref": "main"},
                "head": {"ref": "dev"},
                "title": "merge dev to main without release prefix",
            }
        }
        ret = validate_pull_request_event(event)
        self.assertEqual(ret, 1)


if __name__ == "__main__":
    unittest.main()
