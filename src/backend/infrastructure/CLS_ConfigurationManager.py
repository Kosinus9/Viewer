class CLS_ConfigurationManager:
    def __init__(
        self,
        window_width_ratio: float = 0.50,
        window_height_ratio: float = 0.50,
    ) -> None:
        if not 0 < window_width_ratio <= 1:
            raise ValueError("window_width_ratio must be between 0 (exclusive) and 1.")
        if not 0 < window_height_ratio <= 1:
            raise ValueError("window_height_ratio must be between 0 (exclusive) and 1.")

        self._window_width_ratio  = window_width_ratio
        self._window_height_ratio = window_height_ratio

    @property
    def window_width_ratio(self) -> float:
        return self._window_width_ratio

    @property
    def window_height_ratio(self) -> float:
        return self._window_height_ratio
