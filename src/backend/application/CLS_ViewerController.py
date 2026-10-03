from uuid                                   import uuid4

from .CLS_LayoutManager                     import CLS_LayoutManager
from .CLS_SectionManager                    import CLS_SectionManager
from .CLS_TimerLifecycleManager             import CLS_TimerLifecycleManager

from ..domain.DUT.ENUM.E_CommandType        import E_CommandType
from ..domain.DUT.STRUCT.ST_Command         import ST_Command
from ..domain.DUT.STRUCT.ST_Job             import ST_Job
from ..domain.DUT.STRUCT.ST_JobSection      import ST_JobSection
from ..domain.DUT.STRUCT.ST_JobLayout       import ST_JobLayout
from ..domain.DUT.STRUCT.ST_JobLifecycle    import ST_JobLifecycle

# Main backend controller that coordinates the application managers.
class CLS_ViewerController:
    def __init__(
        self, 
        clsSectionManager         : CLS_SectionManager,
        clsLayoutManager          : CLS_LayoutManager,
        clsTimerLifecycleManager  : CLS_TimerLifecycleManager,
    ) -> None:
        # Store the managers provided by the caller.
        self._clsSectionManager         = clsSectionManager
        self._clsLayoutManager          = clsLayoutManager
        self._clsTimerLifecycleManager  = clsTimerLifecycleManager

    @property
    def section_manager(self) -> CLS_SectionManager:
        # Give read-only access to the section manager.
        return self._clsSectionManager

    @property
    def layout_manager(self) -> CLS_LayoutManager:
        # Give read-only access to the layout manager.
        return self._clsLayoutManager

    @property
    def timer_lifecycle_manager(self) -> CLS_TimerLifecycleManager:
        # Give read-only access to the timer lifecycle manager.
        return self._clsTimerLifecycleManager

    def process_command(self, stCommand: ST_Command) -> None:
        print(
            "\n[TRACE TEMP][ViewerController] Entree dans process_command()\n"
            f"  command_type : {stCommand.command_type.name}\n"
            "  section_id   : non attribue pour OPEN, recherche par fichier pour les autres commandes\n"
            f"  file_name    : {stCommand.file_name}\n"
            f"  file_path    : {stCommand.file_path}\n"
        )
        command_type = stCommand.command_type

        if command_type == E_CommandType.OPEN:
            print("[TRACE TEMP][ViewerController] Branche OPEN selectionnee")
            print("[TRACE TEMP][ViewerController] Appel de create_job(stCommand)")
            stJob = self.create_job(stCommand)
            print(
                "\n[TRACE TEMP][ViewerController] Retour de create_job()\n"
                f"  resultat : {'ST_Job (champs ci-dessus)' if stJob is not None else 'None'}\n"
            )
            if stJob is not None:
                print(
                    "[TRACE TEMP][ViewerController] ST_Job valide reçu\n"
                    f"  command_type : {stJob.command_type.name}\n"
                    f"  section_id   : {stJob.stJobSection.section_id}\n"
                    f"  file_name    : {stJob.stJobSection.file_name}\n"
                    f"  file_path    : {stJob.stJobSection.file_path}\n"
                ) 
                print(
                    "[TRACE TEMP][ViewerController] Transmission du ST_Job au SectionManager\n"
                    f"  section_id : {stJob.stJobSection.section_id}\n"
                )
                section_id = self._clsSectionManager.create_section(stJob)
                print(
                    "[TRACE TEMP][ViewerController] Retour de SectionManager.create_section()\n"
                    f"  section_id : {section_id}\n"
                )
        elif command_type in (E_CommandType.SHOW, E_CommandType.HIDE, E_CommandType.CLOSE):
            section_id = self._clsSectionManager.find_section(
                stCommand.file_name, stCommand.file_path
            )
            if section_id is None:
                return

            print(
                "[TRACE TEMP][ViewerController] Routage de la commande\n"
                f"  command_type : {command_type.name}\n"
                f"  section_id   : {section_id}\n"
            )
            if command_type == E_CommandType.SHOW:
                self._clsSectionManager.show_section(section_id)
            elif command_type == E_CommandType.HIDE:
                self._clsSectionManager.hide_section(section_id)
            elif command_type == E_CommandType.CLOSE:
                self._clsSectionManager.close_section(section_id)
        elif command_type == E_CommandType.RESET:
            pass

    def create_job(self, stCommand: ST_Command) -> ST_Job | None:
        file_path = stCommand.file_path
        if not file_path:
            raise ValueError("OPEN requires a file_path.")

        file_name      = stCommand.file_name
        section_id     = str(uuid4())

        stJobSection   = ST_JobSection(
            file_name  = file_name,
            file_path  = file_path,
            section_id = section_id,
        )

        stJobLayout = self._clsLayoutManager.calculate_layout()
        if stJobLayout is None:
            # Screen dimensions must be supplied before calculating the layout.
            print("[TRACE TEMP][create_job] calculate_layout() retourne None : aucun ST_Job construit")
            return None

        stJobLifecycle = self._clsTimerLifecycleManager.get_lifecycle()
        stJob = ST_Job(
            command_type   = stCommand.command_type,
            stJobSection   = stJobSection,
            stJobLayout    = stJobLayout,
            stJobLifecycle = stJobLifecycle,
        )
        print(
            "\n[TRACE TEMP][create_job] ST_Job construit\n"
            f"  command_type : {stJob.command_type.name}\n"
            "\n  Section:\n"
            f"    file_name  : {stJob.stJobSection.file_name}\n"
            f"    file_path  : {stJob.stJobSection.file_path}\n"
            f"    section_id : {stJob.stJobSection.section_id}\n"
            "\n  Layout:\n"
            f"    position_x : {stJob.stJobLayout.position_x}\n"
            f"    position_y : {stJob.stJobLayout.position_y}\n"
            f"    width      : {stJob.stJobLayout.width}\n"
            f"    height     : {stJob.stJobLayout.height}\n"
            "\n  Lifecycle:\n"
            f"    duration         : {stJob.stJobLifecycle.duration}\n"
            f"    ignore_lifecycle : {stJob.stJobLifecycle.ignore_lifecycle}\n"
        )
        if not self.validate_job(stJob):
            print("[TRACE TEMP][create_job] validate_job() retourne False : retour None")
            return None
        print("[TRACE TEMP][create_job] ST_Job valide : retour du job")
        return stJob

    def validate_job(self, stJob: ST_Job) -> bool:
        if not isinstance(stJob, ST_Job):
            return False
        if stJob.command_type != E_CommandType.OPEN:
            return False

        stJobSection = stJob.stJobSection
        if not isinstance(stJobSection, ST_JobSection):
            return False
        for value in (
            stJobSection.file_name,
            stJobSection.file_path,
            stJobSection.section_id,
        ):
            if not isinstance(value, str) or not value:
                return False

        stJobLayout = stJob.stJobLayout
        if not isinstance(stJobLayout, ST_JobLayout):
            return False
        for value in (
            stJobLayout.position_x,
            stJobLayout.position_y,
            stJobLayout.width,
            stJobLayout.height,
        ):
            if type(value) is not int:
                return False
        if stJobLayout.position_x < 0 or stJobLayout.position_y < 0:
            return False
        if stJobLayout.width <= 0 or stJobLayout.height <= 0:
            return False

        stJobLifecycle = stJob.stJobLifecycle
        if not isinstance(stJobLifecycle, ST_JobLifecycle):
            return False
        if type(stJobLifecycle.ignore_lifecycle) is not bool:
            return False
        if stJobLifecycle.duration is not None:
            if type(stJobLifecycle.duration) not in (int, float):
                return False
            if not stJobLifecycle.duration > 0:
                return False

        return True

    # Prepare the backend for use. Not implemented yet.
    def initialize(self) -> None:
        pass

    # Start backend activity. Not implemented yet.
    def start(self) -> None:
        pass

    # Stop backend activity. Not implemented yet.
    def stop(self) -> None:
        pass

    # Return the backend to its initial state. Not implemented yet.
    def reset(self) -> None:
        pass

    # Close the backend and release resources. Not implemented yet.
    def shutdown(self) -> None:
        pass
