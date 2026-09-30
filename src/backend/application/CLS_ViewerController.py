from .CLS_LayoutManager          import CLS_LayoutManager
from .CLS_SectionManager         import CLS_SectionManager
from .CLS_TimerLifecycleManager  import CLS_TimerLifecycleManager


# Main backend controller that coordinates the application managers.
class CLS_ViewerController:
    def __init__(
        self,
        section_manager         : CLS_SectionManager,
        layout_manager          : CLS_LayoutManager,
        timer_lifecycle_manager : CLS_TimerLifecycleManager,
    ) -> None:
        # Store the managers provided by the caller.
        self._section_manager         = section_manager
        self._layout_manager          = layout_manager
        self._timer_lifecycle_manager = timer_lifecycle_manager

    @property
    def section_manager(self) -> CLS_SectionManager:
        # Give read-only access to the section manager.
        return self._section_manager

    @property
    def layout_manager(self) -> CLS_LayoutManager:
        # Give read-only access to the layout manager.
        return self._layout_manager

    @property
    def timer_lifecycle_manager(self) -> CLS_TimerLifecycleManager:
        # Give read-only access to the timer lifecycle manager.
        return self._timer_lifecycle_manager

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
