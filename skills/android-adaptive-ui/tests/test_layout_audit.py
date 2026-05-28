import importlib.util
import tempfile
import unittest
from pathlib import Path


def _load_layout_audit_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "layout_audit.py"
    spec = importlib.util.spec_from_file_location("layout_audit", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


layout_audit = _load_layout_audit_module()


class ScrollabilityXmlTests(unittest.TestCase):
    def _fixture_path(self, name: str) -> Path:
        return Path(__file__).resolve().parent / "fixtures" / "layout" / name

    def test_warns_large_linear_layout_without_scroll_ancestor_even_with_unrelated_scrollview(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="wrap_content">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
    </ScrollView>

    <LinearLayout
        android:id="@+id/content_container"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
    </LinearLayout>
</LinearLayout>
"""
        with tempfile.TemporaryDirectory() as td:
            layout_dir = Path(td) / "res" / "layout"
            layout_dir.mkdir(parents=True, exist_ok=True)
            xml_path = layout_dir / "activity_main.xml"
            xml_path.write_text(xml, encoding="utf-8")

            result = layout_audit.run_audit([str(xml_path)])
            findings = [f for f in result.findings if f.category == "Scrollability"]

        self.assertEqual(len(findings), 1)
        self.assertIn("content_container", findings[0].message)
        self.assertGreater(findings[0].line, 0)

    def test_no_warning_when_large_linear_layout_is_wrapped_by_scrollview(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <LinearLayout
        android:id="@+id/inside_scroll"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" />
    </LinearLayout>
</ScrollView>
"""
        with tempfile.TemporaryDirectory() as td:
            layout_dir = Path(td) / "res" / "layout"
            layout_dir.mkdir(parents=True, exist_ok=True)
            xml_path = layout_dir / "activity_scroll.xml"
            xml_path.write_text(xml, encoding="utf-8")

            result = layout_audit.run_audit([str(xml_path)])
            findings = [f for f in result.findings if f.category == "Scrollability"]

        self.assertEqual(findings, [])

    def test_fixtures_nested_scroll_and_recyclerview_do_not_warn(self):
        for fixture in [
            "nested_scroll_chain.xml",
            "nested_scrollview_linearlayout.xml",
            "recyclerview_only.xml",
        ]:
            with self.subTest(fixture=fixture):
                result = layout_audit.run_audit([str(self._fixture_path(fixture))])
                findings = [f for f in result.findings if f.category == "Scrollability"]
                self.assertEqual(findings, [])

    def test_mixed_layout_tree_flags_only_non_scrolling_block(self):
        result = layout_audit.run_audit([str(self._fixture_path("mixed_layout_tree.xml"))])
        findings = [f for f in result.findings if f.category == "Scrollability"]

        self.assertEqual(len(findings), 1)
        self.assertIn("problem_block", findings[0].message)


if __name__ == "__main__":
    unittest.main()
