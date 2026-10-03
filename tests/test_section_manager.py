import unittest
from unittest.mock import patch

from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.domain.DUT.STRUCT.ST_Job import ST_Job
from src.backend.domain.DUT.STRUCT.ST_JobSection import ST_JobSection
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.domain.DUT.STRUCT.ST_JobLifecycle import ST_JobLifecycle


class TestSectionManager(unittest.TestCase):
    def test_new_section_is_registered_before_initializing_exactly_once(self):
        clsSectionManager = CLS_SectionManager()
        stJob = ST_Job(
            command_type=E_CommandType.OPEN,
            stJobSection=ST_JobSection(
                file_name="example.pdf",
                file_path="documents/example.pdf",
                section_id="section-from-job",
            ),
            stJobLayout=ST_JobLayout(0, 0, 960, 540),
            stJobLifecycle=ST_JobLifecycle(),
        )

        initialize_section = CLS_ViewSection.initialize

        def check_registration(clsViewSection):
            self.assertIsInstance(clsViewSection, CLS_ViewSection)
            self.assertIs(
                clsSectionManager.view_sections[stJob.stJobSection.section_id],
                clsViewSection,
            )
            initialize_section(clsViewSection)

        with patch.object(CLS_ViewSection, "initialize", autospec=True, side_effect=check_registration) as initialize, \
                patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
            section_id = clsSectionManager.create_section(stJob)
            clsViewSection = clsSectionManager.get_section(section_id)
            initialize.assert_called_once_with(clsViewSection)

        self.assertEqual(section_id, stJob.stJobSection.section_id)
        self.assertEqual(len(clsSectionManager.view_sections), 1)
        self.assertEqual(clsViewSection.section_id, section_id)
        self.assertEqual(clsViewSection.file_name, stJob.stJobSection.file_name)
        self.assertEqual(clsViewSection.file_path, stJob.stJobSection.file_path)
        self.assertIs(clsViewSection.file_type, E_FileType.PDF)
        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)


if __name__ == "__main__":
    unittest.main()
