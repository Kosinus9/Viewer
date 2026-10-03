import unittest
from itertools import combinations

from src.backend.application.CLS_LayoutManager import CLS_LayoutManager
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.infrastructure.CLS_ConfigurationManager import CLS_ConfigurationManager


class TestLayoutManager(unittest.TestCase):
    def setUp(self):
        self.clsLayoutManager = CLS_LayoutManager()
        self.clsLayoutManager.set_screen_dimensions(1920, 1080)

    def assert_valid_zones(self, stJobLayouts, width, height):
        for stJobLayout in stJobLayouts:
            self.assertIsInstance(stJobLayout, ST_JobLayout)
            self.assertGreater(stJobLayout.width, 0)
            self.assertGreater(stJobLayout.height, 0)
            self.assertGreaterEqual(stJobLayout.position_x, 0)
            self.assertGreaterEqual(stJobLayout.position_y, 0)
            self.assertLessEqual(stJobLayout.position_x + stJobLayout.width, width)
            self.assertLessEqual(stJobLayout.position_y + stJobLayout.height, height)
        for stFirstJobLayout, stSecondJobLayout in combinations(stJobLayouts, 2):
            self.assertTrue(
                stFirstJobLayout.position_x + stFirstJobLayout.width <= stSecondJobLayout.position_x
                or stSecondJobLayout.position_x + stSecondJobLayout.width <= stFirstJobLayout.position_x
                or stFirstJobLayout.position_y + stFirstJobLayout.height <= stSecondJobLayout.position_y
                or stSecondJobLayout.position_y + stSecondJobLayout.height <= stFirstJobLayout.position_y
            )

    def test_layouts_for_one_to_four_sections(self):
        for number_of_active_section, expected in (
            (1, [(480, 270, 960, 540)]),
            (2, [(0, 0, 960, 1080), (960, 0, 960, 1080)]),
            (3, [(0, 0, 960, 540), (960, 0, 960, 540), (0, 540, 1920, 540)]),
            (4, [(0, 0, 960, 540), (960, 0, 960, 540), (0, 540, 960, 540), (960, 540, 960, 540)]),
        ):
            with self.subTest(number_of_active_section=number_of_active_section):
                stJobLayouts = self.clsLayoutManager.calculate_layouts(number_of_active_section)
                self.assertEqual(len(stJobLayouts), number_of_active_section)
                self.assertEqual(stJobLayouts, [ST_JobLayout(*values) for values in expected])
                self.assert_valid_zones(stJobLayouts, 1920, 1080)

    def test_invalid_section_counts(self):
        for number_of_active_section in (-1, 0, 5, 100, True, False, 1.0, "3", None):
            with self.subTest(number_of_active_section=number_of_active_section):
                with self.assertRaises(ValueError):
                    self.clsLayoutManager.calculate_layouts(number_of_active_section)

    def test_missing_dimensions(self):
        clsLayoutManager = CLS_LayoutManager()
        for number_of_active_section in range(1, 5):
            self.assertIsNone(clsLayoutManager.calculate_layouts(number_of_active_section))
        self.assertIsNone(clsLayoutManager.calculate_layout())

    def test_recalculates_after_four_sections_and_screen_change(self):
        stFourJobLayouts = self.clsLayoutManager.calculate_layouts(4)
        stFourJobLayouts[0].width = 1
        stThreeJobLayouts = self.clsLayoutManager.calculate_layouts(3)
        self.assertEqual(stThreeJobLayouts, [
            ST_JobLayout(0, 0, 960, 540), ST_JobLayout(960, 0, 960, 540),
            ST_JobLayout(0, 540, 1920, 540),
        ])
        self.clsLayoutManager.set_screen_dimensions(800, 600)
        self.assertEqual(self.clsLayoutManager.calculate_layouts(2), [
            ST_JobLayout(0, 0, 400, 600), ST_JobLayout(400, 0, 400, 600),
        ])

    def test_odd_dimensions_cover_screen_without_overlap(self):
        self.clsLayoutManager.set_screen_dimensions(1919, 1079)
        for number_of_active_section in (2, 3, 4):
            stJobLayouts = self.clsLayoutManager.calculate_layouts(number_of_active_section)
            self.assert_valid_zones(stJobLayouts, 1919, 1079)
            self.assertEqual(sum(stJobLayout.width * stJobLayout.height for stJobLayout in stJobLayouts), 1919 * 1079)
            self.assertEqual(stJobLayouts[0].width, 959)
            self.assertEqual(stJobLayouts[1].width, 960)
        self.assertEqual(stJobLayouts[-1], ST_JobLayout(959, 539, 960, 540))

    def test_single_section_preserves_configured_ratios_and_legacy_api(self):
        clsConfigurationManager = CLS_ConfigurationManager(0.75, 0.25)
        clsLayoutManager = CLS_LayoutManager(clsConfigurationManager)
        clsLayoutManager.set_screen_dimensions(800, 600)
        self.assertEqual(clsLayoutManager.calculate_layouts(1), [ST_JobLayout(100, 225, 600, 150)])
        self.assertEqual(clsLayoutManager.calculate_layout(), ST_JobLayout(100, 225, 600, 150))

    def test_screen_too_small_for_required_split(self):
        self.clsLayoutManager.set_screen_dimensions(1, 1)
        self.assertEqual(self.clsLayoutManager.calculate_layouts(1), [ST_JobLayout(0, 0, 1, 1)])
        for number_of_active_section in (2, 3, 4):
            with self.assertRaises(ValueError):
                self.clsLayoutManager.calculate_layouts(number_of_active_section)
        self.clsLayoutManager.set_screen_dimensions(2, 1)
        self.assertEqual(len(self.clsLayoutManager.calculate_layouts(2)), 2)
        for number_of_active_section in (3, 4):
            with self.assertRaises(ValueError):
                self.clsLayoutManager.calculate_layouts(number_of_active_section)


if __name__ == "__main__":
    unittest.main()
