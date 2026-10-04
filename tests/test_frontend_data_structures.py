import unittest

from src.backend.domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from src.backend.domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout


class TestFrontendDataStructures(unittest.TestCase):
    def test_backend_to_frontend_preserves_data_and_layout_identity(self):
        stJobLayout = ST_JobLayout(480, 270, 960, 540)
        stBackendToFrontendData = ST_BackendToFrontendData(
            renderer_name="CLS_PDFRenderer",
            section_id="section-1",
            file_name="provided-name.pdf",
            file_path="documents/document.pdf",
            stJobLayout=stJobLayout,
        )
        self.assertEqual(stBackendToFrontendData.renderer_name, "CLS_PDFRenderer")
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
