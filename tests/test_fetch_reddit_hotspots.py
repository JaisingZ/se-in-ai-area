import importlib.util
import os
import sys
import unittest
from unittest.mock import patch
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_reddit_hotspots.py"
spec = importlib.util.spec_from_file_location("fetch_reddit_hotspots", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class EnvIntTests(unittest.TestCase):
    def setUp(self):
        self.original_limit = os.environ.get("REDDIT_LIMIT")
        self.original_user_agent = os.environ.get("REDDIT_USER_AGENT")

    def tearDown(self):
        if self.original_limit is None:
            os.environ.pop("REDDIT_LIMIT", None)
        else:
            os.environ["REDDIT_LIMIT"] = self.original_limit

        if self.original_user_agent is None:
            os.environ.pop("REDDIT_USER_AGENT", None)
        else:
            os.environ["REDDIT_USER_AGENT"] = self.original_user_agent

    def test_env_int_uses_default_on_missing_value(self):
        os.environ.pop("REDDIT_LIMIT", None)
        self.assertEqual(module._env_int("REDDIT_LIMIT", 20), 20)

    def test_env_int_uses_default_on_empty_value(self):
        os.environ["REDDIT_LIMIT"] = ""
        self.assertEqual(module._env_int("REDDIT_LIMIT", 20), 20)

    def test_env_int_uses_default_on_invalid_value(self):
        os.environ["REDDIT_LIMIT"] = "abc"
        self.assertEqual(module._env_int("REDDIT_LIMIT", 20), 20)

    def test_env_int_uses_default_on_non_positive_value(self):
        os.environ["REDDIT_LIMIT"] = "0"
        self.assertEqual(module._env_int("REDDIT_LIMIT", 20), 20)

    def test_env_int_accepts_positive_integer(self):
        os.environ["REDDIT_LIMIT"] = "15"
        self.assertEqual(module._env_int("REDDIT_LIMIT", 20), 15)


    def test_user_agent_uses_default_on_missing_value(self):
        os.environ.pop("REDDIT_USER_AGENT", None)
        self.assertEqual(module._user_agent(), "se-in-ai-area/0.1 (by github-actions)")

    def test_user_agent_uses_default_on_empty_value(self):
        os.environ["REDDIT_USER_AGENT"] = ""
        self.assertEqual(module._user_agent(), "se-in-ai-area/0.1 (by github-actions)")

    def test_user_agent_keeps_configured_value(self):
        os.environ["REDDIT_USER_AGENT"] = "my-bot/1.0"
        self.assertEqual(module._user_agent(), "my-bot/1.0")


class MainFlowTests(unittest.TestCase):
    def test_main_returns_zero_on_http_403_blocked(self):
        err = module.urllib.error.HTTPError(
            url="https://www.reddit.com/r/test/hot.json",
            code=403,
            msg="Blocked",
            hdrs=None,
            fp=None,
        )
        with patch.object(module, "fetch", side_effect=err), patch.object(module, "save") as mock_save:
            rc = module.main()

        self.assertEqual(rc, 0)
        mock_save.assert_not_called()

    def test_main_returns_non_zero_on_http_500(self):
        err = module.urllib.error.HTTPError(
            url="https://www.reddit.com/r/test/hot.json",
            code=500,
            msg="Server Error",
            hdrs=None,
            fp=None,
        )
        with patch.object(module, "fetch", side_effect=err), patch.object(module, "save") as mock_save:
            rc = module.main()

        self.assertEqual(rc, 1)
        mock_save.assert_not_called()

if __name__ == "__main__":
    unittest.main()
