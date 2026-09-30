from .CLS_LayoutManager          import CLS_LayoutManager
from .CLS_SectionManager         import CLS_SectionManager
from .CLS_TimerLifecycleManager  import CLS_TimerLifecycleManager


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
