import unittest

from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType


class TestViewSection(unittest.TestCase):
    def test_file_type_is_undetermined_before_initialization(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        self.assertIsNone(clsViewSection.file_type)

    def test_initialize_identifies_type_from_file_path(self):
        for file_path, expected_type in (
            ("documents/document.pdf", E_FileType.PDF),
            ("documents/document.PDF", E_FileType.PDF),
            ("documents/document", E_FileType.ERROR),
            ("documents/document.txt", E_FileType.ERROR),
            ("documents/document.xyz", E_FileType.ERROR),
        ):
            with self.subTest(file_path=file_path):
                clsViewSection = CLS_ViewSection("section-1", "different-name.bin", file_path)
                clsViewSection.initialize()
                self.assertIs(clsViewSection.file_type, expected_type)

    def test_file_type_is_read_only(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        clsViewSection.initialize()
        with self.assertRaises(AttributeError):
            clsViewSection.file_type = E_FileType.ERROR
        self.assertIs(clsViewSection.file_type, E_FileType.PDF)


if __name__ == "__main__":
    unittest.main()
