from __future__ import annotations

import unittest

from stellatowerassistant.core.config.settings import RESOURCE_DIR, TEMPLATES


class SettingsTestCase(unittest.TestCase):
    def test_template_directory_exists(self) -> None:
        self.assertTrue(RESOURCE_DIR.is_dir())

    def test_known_templates_resolve_to_files(self) -> None:
        for key in ("quick_start", "next", "start_battle", "save"):
            self.assertTrue((RESOURCE_DIR / TEMPLATES[key]).is_file(), key)


if __name__ == "__main__":
    unittest.main()
