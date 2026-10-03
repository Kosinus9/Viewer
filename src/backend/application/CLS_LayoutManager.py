from ..domain.DUT.STRUCT.ST_JobLayout          import ST_JobLayout
from ..infrastructure.CLS_ConfigurationManager import CLS_ConfigurationManager


# Manage the arrangement of view sections in the viewer.
class CLS_LayoutManager:
    # Store the configuration and prepare unset screen and layout values.
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

    # Calculate and store a centered single-window layout using configured ratios.
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

    # Use common dimensions; odd screen pixels remain outside the windows.
    def calculate_layouts(self, number_of_active_section: int) -> list[ST_JobLayout] | None:
        if type(number_of_active_section) is not int or not 1 <= number_of_active_section <= 4:
            raise ValueError("number_of_active_section must be an integer between 1 and 4.")
        if self._screen_width is None or self._screen_height is None:
            return None
        if number_of_active_section == 1:
            stJobLayout = self.calculate_layout()
            return [stJobLayout]

        width = self._screen_width // 2
        height = self._screen_height if number_of_active_section == 2 else self._screen_height // 2
        if width == 0:
            raise ValueError("Screen width is too small to split into two zones.")
        if height == 0:
            raise ValueError("Screen height is too small to split into two zones.")
        if number_of_active_section == 2:
            return [
                ST_JobLayout(0, 0, width, height),
                ST_JobLayout(width, 0, width, height),
            ]

        stJobLayouts = [
            ST_JobLayout(0, 0, width, height),
            ST_JobLayout(width, 0, width, height),
        ]
        if number_of_active_section == 3:
            stJobLayouts.append(ST_JobLayout((self._screen_width - width) // 2, height, width, height))
        else:
            stJobLayouts.extend([
                ST_JobLayout(0, height, width, height),
                ST_JobLayout(width, height, width, height),
            ])
        return stJobLayouts

    # Store the supplied geometry as the current single-window layout.
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

    # Retrieve the current layout without recalculating its geometry.
    def get_layout(self) -> ST_JobLayout | None:
        return self._current_layout

    # Layout updates are not implemented yet.
    def update_layout(self) -> None:
        pass

    # Clearing the current layout is not implemented yet.
    def reset_layout(self) -> None:
        pass

    # Resetting the manager is not implemented yet.
    def reset(self) -> None:
        pass
