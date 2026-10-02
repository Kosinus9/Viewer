import unittest
from unittest.mock import call, patch

from src.backend.infrastructure.CLS_PlatformAdapter import CLS_PlatformAdapter


class TestPlatformAdapter(unittest.TestCase):
    def test_returns_two_positive_integers_from_windows(self):
        with patch("src.backend.infrastructure.CLS_PlatformAdapter.ctypes") as windows:
            get_metrics = windows.windll.user32.GetSystemMetrics
            get_metrics.side_effect = [1920, 1080]
            dimensions = CLS_PlatformAdapter().get_screen_dimensions()

        self.assertEqual(len(dimensions), 2)
        self.assertEqual(dimensions, (1920, 1080))
        for dimension in dimensions:
            self.assertIs(type(dimension), int)
            self.assertGreater(dimension, 0)
        self.assertEqual(get_metrics.call_args_list, [call(0), call(1)])

    def test_rejects_non_positive_dimensions(self):
        for dimensions in ((0, 1080), (1920, 0), (-1, 1080), (1920, -1)):
            with self.subTest(dimensions=dimensions):
                with patch("src.backend.infrastructure.CLS_PlatformAdapter.ctypes") as windows:
                    windows.windll.user32.GetSystemMetrics.side_effect = dimensions
                    with self.assertRaisesRegex(RuntimeError, "invalid screen dimensions"):
                        CLS_PlatformAdapter().get_screen_dimensions()


if __name__ == "__main__":
    unittest.main()
