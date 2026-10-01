from pathlib                           import Path

from .CLS_LayoutManager                import CLS_LayoutManager
from .CLS_SectionManager               import CLS_SectionManager
from .CLS_TimerLifecycleManager        import CLS_TimerLifecycleManager

from ..domain.DUT.ENUM.E_CommandType   import E_CommandType
from ..domain.DUT.STRUCT.ST_Command    import ST_Command
from ..domain.DUT.STRUCT.ST_Job        import ST_Job
from ..domain.DUT.STRUCT.ST_JobSection import ST_JobSection

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
        command_type = stCommand.command_type

        if command_type == E_CommandType.OPEN:
            self.create_job(stCommand)
        elif command_type == E_CommandType.SHOW:
            pass
        elif command_type == E_CommandType.HIDE:
            pass
        elif command_type == E_CommandType.CLOSE:
            pass
        elif command_type == E_CommandType.RESET:
            pass

    def create_job(self, stCommand: ST_Command) -> ST_Job | None:
        file_path = stCommand.file_path
        if not file_path:
            raise ValueError("OPEN requires a file_path.")

        file_name      = Path(file_path).name
        section_id     = self._clsSectionManager.find_section(file_name, file_path)
        if section_id is None:
            section_id = self._clsSectionManager.create_section(file_name, file_path)

        stJobSection   = ST_JobSection(
            file_name  = file_name,
            file_path  = file_path,
            section_id = section_id,
        )

        stJobLayout = self._clsLayoutManager.calculate_layout()
        if stJobLayout is None:
            # Screen dimensions must be supplied before calculating the layout.
            return None

        stJobLifecycle = self._clsTimerLifecycleManager.get_lifecycle()
        stJob = ST_Job(
            command_type   = stCommand.command_type,
            stJobSection   = stJobSection,
            stJobLayout    = stJobLayout,
            stJobLifecycle = stJobLifecycle,
        )
        return stJob

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
