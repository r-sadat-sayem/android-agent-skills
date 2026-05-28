import importlib.util
import tempfile
import unittest
from pathlib import Path


def _load_smoke_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "template_smoke_check.py"
    spec = importlib.util.spec_from_file_location("template_smoke_check", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


smoke = _load_smoke_module()


class WearTemplateSmokeTests(unittest.TestCase):
    def test_flags_invalid_int_dp_extension(self):
        content = """
package com.example
private val Int.dp get() = androidx.compose.ui.unit.dp.run { this@dp.dp }
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "BadTemplate.kt"
            path.write_text(content, encoding="utf-8")
            violations = smoke.check_template(path)

        self.assertTrue(any("invalid custom Int.dp extension" in v for v in violations))

    def test_passes_standard_dp_import_usage(self):
        content = """
package com.example
import androidx.compose.ui.unit.dp

fun spacing() = 16.dp
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "GoodTemplate.kt"
            path.write_text(content, encoding="utf-8")
            violations = smoke.check_template(path)

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
