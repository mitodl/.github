"""Run with: python3 -m unittest discover scripts"""

import unittest

from renovate_own_packages import MAX_REMOVALS, names_from_manifest, npm_name_from_package_json, update_config


class NamesFromManifest(unittest.TestCase):
    def test_pyproject_project_and_poetry(self):
        self.assertEqual(names_from_manifest("pyproject.toml", '[project]\nname = "ol-llm"\n'), ["ol-llm"])
        self.assertEqual(names_from_manifest("a/pyproject.toml", '[tool.poetry]\nname = "edx-sga"\n'), ["edx-sga"])

    def test_setup_py(self):
        self.assertEqual(names_from_manifest("setup.py", 'setup(name="rapid-response-xblock", version="1")'),
                         ["rapid-response-xblock"])

    def test_placeholders_and_bad_toml_are_skipped(self):
        self.assertEqual(names_from_manifest("pyproject.toml", '[project]\nname = "<replace me>"\n'), [])
        self.assertEqual(names_from_manifest("setup.py", 'setup(name="{{ cookiecutter.name }}")'), [])
        self.assertEqual(names_from_manifest("pyproject.toml", "not = = toml"), [])


class NpmNameFromPackageJson(unittest.TestCase):
    def test_public_private_and_invalid(self):
        self.assertEqual(npm_name_from_package_json('{"name": "eslint-config-mitodl"}'), ["eslint-config-mitodl"])
        self.assertEqual(npm_name_from_package_json('{"name": "app", "private": true}'), [])
        self.assertEqual(npm_name_from_package_json("{not json"), [])
        self.assertEqual(npm_name_from_package_json('\ufeff{"name": "redux-asserts"}'), ["redux-asserts"])


class UpdateConfig(unittest.TestCase):
    def config(self):
        return {"packageRules": [
            {"matchDatasources": ["pypi"], "matchPackageNames": ["ol-llm", "old-pkg"], "minimumReleaseAge": None},
            {"matchDatasources": ["npm"], "matchPackageNames": ["@mitodl/**"], "minimumReleaseAge": None},
            {"matchDatasources": ["pypi"], "matchPackageNames": ["django"], "automerge": False},
        ]}

    def test_replaces_both_lists_and_reports_changes(self):
        config = self.config()
        changes = update_config(config, ["ol-llm", "witan-core"], ["eslint-config-mitodl"])
        self.assertEqual(config["packageRules"][0]["matchPackageNames"], ["ol-llm", "witan-core"])
        self.assertEqual(config["packageRules"][1]["matchPackageNames"], ["@mitodl/**", "eslint-config-mitodl"])
        self.assertEqual(config["packageRules"][2]["matchPackageNames"], ["django"])  # unrelated rule untouched
        self.assertEqual(changes["pypi"], (["witan-core"], ["old-pkg"]))
        self.assertEqual(changes["npm"], (["eslint-config-mitodl"], []))

    def test_refuses_mass_removal(self):
        config = self.config()
        config["packageRules"][0]["matchPackageNames"] = ["ol-llm"] + [f"pkg-{i}" for i in range(MAX_REMOVALS + 1)]
        with self.assertRaises(SystemExit) as cm:
            update_config(config, ["ol-llm"], ["x"])  # non-empty, so it's the removal cap that refuses
        self.assertIn("refusing to remove", str(cm.exception))

    def test_refuses_empty_npm_list_under_the_cap(self):
        config = self.config()
        config["packageRules"][1]["matchPackageNames"] = ["@mitodl/**", "a", "b", "c"]
        with self.assertRaises(SystemExit):
            update_config(config, ["ol-llm"], [])

    def test_missing_rule_exits(self):
        config = self.config()
        del config["packageRules"][1]
        with self.assertRaises(SystemExit):
            update_config(config, ["ol-llm"], ["x"])


if __name__ == "__main__":
    unittest.main()
