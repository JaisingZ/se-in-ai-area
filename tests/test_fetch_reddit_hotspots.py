import importlib.util
import os
import sys
import unittest
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

    def tearDown(self):
        if self.original_limit is None:
            os.environ.pop("REDDIT_LIMIT", None)
        else:
            os.environ["REDDIT_LIMIT"] = self.original_limit

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


if __name__ == "__main__":
    unittest.main()
