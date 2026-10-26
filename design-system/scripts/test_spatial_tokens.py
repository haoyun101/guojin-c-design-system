# -*- coding: utf-8 -*-
"""Regression cases for dependency-based spacing/radius auditing."""
import unittest
from spatial_tokens import audit

class SpatialAliasTest(unittest.TestCase):
    def test_dependency_semantics(self):
        cases = [
            (':root{--a:16px}.c{border-radius:var(--a)}', True),
            (':root{--b:16px;--a:var(--b)}.c{border-radius:var(--a)}', True),
            (':root{--a:var(--RD4)}.c{border-radius:var(--a)}', False),
            (':root{--a:22px}.c{border-radius:var(--a)}', False),
            (':root{--progress:0}.c{left:calc(var(--progress)*1%)}', False),
            (':root{--a:var(--b);--b:var(--a)}.c{gap:var(--a)}', False),
            (':root{--a:24px}.c{padding:var(--a)}', True),
            # v4.0.2 范围收窄
            ('*{margin:0;padding:0px}', False),
            ('.c{margin:0 auto;gap:0}', False),
            ('.b{position:absolute;top:4px;right:8px;inset:16px}', False),
            ('.p{height:32px;border-radius:16px}', False),
            ('.p{width:12px;height:12px;border-radius:6px}', False),
            ('.p{height:40px;border-radius:16px}', True),
            ('.k{--btn-h:32px;--btn-radius:16px}.c{border-radius:var(--btn-radius)}', False),
            ('.k{--btn-h:44px;--btn-radius:16px}.c{border-radius:var(--btn-radius)}', True),
            ('.c{padding:16px}', True),
        ]
        for source, expected in cases:
            with self.subTest(css=source):
                self.assertEqual(bool(audit(source, html=False)), expected)

    def test_no_duplicate_report(self):
        self.assertEqual(len(audit('.x{--my-pad:16px;padding:var(--my-pad)}', html=False)), 1)

if __name__ == '__main__':
    unittest.main()
