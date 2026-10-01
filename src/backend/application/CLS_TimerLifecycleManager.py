from ..domain.DUT.STRUCT.ST_JobLifecycle import ST_JobLifecycle


# Manage section timing and timer lifecycle operations.
class CLS_TimerLifecycleManager:
    def __init__(self) -> None:
        # The timer type will be defined later.
        self._active_timers: list[object] = []

    @property
    def active_timers(self) -> list[object]:
        # Access the active timers.
        return self._active_timers

    def get_lifecycle(self) -> ST_JobLifecycle:
        return ST_JobLifecycle()

    # Timer operations will be implemented later.
    def initialize(self) -> None:
        pass

    def start_timer(self) -> None:
        pass

    def stop_timer(self) -> None:
        pass

    def reset_timer(self) -> None:
        pass

    def remove_timer(self) -> None:
        pass

    def clear_timers(self) -> None:
        pass

    def update(self) -> None:
        pass

    def shutdown(self) -> None:
        pass
