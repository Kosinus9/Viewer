from ..domain.DUT.STRUCT.ST_JobLayout          import ST_JobLayout
from ..infrastructure.CLS_ConfigurationManager import CLS_ConfigurationManager


# Manage the arrangement of view sections in the viewer.
class CLS_LayoutManager:
    def __init__(
        self,
        clsConfigurationManager: CLS_ConfigurationManager | None = None,
    ) -> None:
        self._clsConfigurationManager = (
            clsConfigurationManager if clsConfigurationManager is not None
            else CLS_ConfigurationManager()
        )
        self._screen_width:   int | None = None
        self._screen_height:  int | None = None
        self._current_layout: ST_JobLayout | None = None

    @property
    def current_layout(self) -> ST_JobLayout | None:
        # Access the current layout.
        return self._current_layout

    # Initialization will be implemented later.
    def initialize(self) -> None:
        pass

    # The caller supplies the available screen dimensions through PlatformAdapter.
    def set_screen_dimensions(self, screen_width: int, screen_height: int) -> None:
        if type(screen_width) is not int or type(screen_height) is not int:
            raise ValueError("Screen dimensions must be integers.")
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError("Screen dimensions must be positive.")
        self._screen_width   = screen_width
        self._screen_height  = screen_height
        self._current_layout = None

    def calculate_layout(self) -> ST_JobLayout | None:
        if self._screen_width is None or self._screen_height is None:
            return None

        width = max(1, int(
            self._screen_width * self._clsConfigurationManager.window_width_ratio
        ))
        height = max(1, int(
            self._screen_height * self._clsConfigurationManager.window_height_ratio
        ))
        self.set_layout(
            position_x = (self._screen_width - width) // 2,
            position_y = (self._screen_height - height) // 2,
            width      = width,
            height     = height,
        )
        return self._current_layout

    def set_layout(
        self,
        position_x: int,
        position_y: int,
        width:      int,
        height:     int,
    ) -> None:
        self._current_layout = ST_JobLayout(
            position_x       = position_x,
            position_y       = position_y,
            width            = width,
            height           = height,
        )

    def get_layout(self) -> ST_JobLayout | None:
        return self._current_layout

    def update_layout(self) -> None:
        pass

    def reset_layout(self) -> None:
        pass

    def reset(self) -> None:
        pass
