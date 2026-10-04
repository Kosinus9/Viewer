import unittest

from src.backend.domain.DUT.ENUM.E_FileType import E_FileType

from src.backend.domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from src.backend.domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout


class TestFrontendDataStructures(unittest.TestCase):
    def test_render_names_and_contract_preserve_each_render_type(self):
        self.assertEqual(
            [E_FileType[name].value for name in ("PDF", "IMAGE", "VIDEO", "TEXT")],
            ["pdf", "image", "video", "text"],
        )
        for render_name in (E_FileType.PDF, E_FileType.IMAGE, E_FileType.VIDEO, E_FileType.TEXT):
            with self.subTest(render_name=render_name):
                stJobLayout = ST_JobLayout(0, 0, 960, 540)
                stBackendToFrontendData = ST_BackendToFrontendData(
                    render_name, "section-1", "provided-name", "documents/resource", stJobLayout
                )
                self.assertIs(stBackendToFrontendData.file_type, render_name)
                self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)

    def test_backend_to_frontend_preserves_data_and_layout_identity(self):
        stJobLayout = ST_JobLayout(480, 270, 960, 540)
        stBackendToFrontendData = ST_BackendToFrontendData(
            file_type=E_FileType.PDF,
            section_id="section-1",
            file_name="provided-name.pdf",
            file_path="documents/document.pdf",
            stJobLayout=stJobLayout,
        )
        self.assertIs(stBackendToFrontendData.file_type, E_FileType.PDF)
        self.assertEqual(stBackendToFrontendData.section_id, "section-1")
        self.assertEqual(stBackendToFrontendData.file_name, "provided-name.pdf")
        self.assertEqual(stBackendToFrontendData.file_path, "documents/document.pdf")
        self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)

    def test_frontend_to_backend_preserves_section_and_event(self):
        stFrontendToBackendData = ST_FrontendToBackendData(
            section_id="section-1",
            event="test-event",
        )
        self.assertEqual(stFrontendToBackendData.section_id, "section-1")
        self.assertEqual(stFrontendToBackendData.event, "test-event")


if __name__ == "__main__":
    unittest.main()
