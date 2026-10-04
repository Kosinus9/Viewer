from collections.abc import Callable

from ..domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from ..domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData


class CLS_FrontendBridge:
    def __init__(self) -> None:
        self._stBackendToFrontendData:  list[ST_BackendToFrontendData]  = []
        self._stFrontendToBackendData:  ST_FrontendToBackendData | None = None
        self._event_callback:           Callable[[ST_FrontendToBackendData], object] | None = None

    def set_event_callback(self, callback: Callable[[ST_FrontendToBackendData], object]) -> None:
        self._event_callback = callback

    # Copy the list while preserving the prepared structures.
    def set_backend_to_frontend_data(self, stBackendToFrontendData: list[ST_BackendToFrontendData]) -> None:
        self._stBackendToFrontendData = list(stBackendToFrontendData)

    # Expose the structures without allowing external list changes.
    def get_backend_to_frontend_data(self) -> list[ST_BackendToFrontendData]:
        return list(self._stBackendToFrontendData)

    def set_frontend_to_backend_data(self, stFrontendToBackendData: ST_FrontendToBackendData) -> None:
        self.receive_event(stFrontendToBackendData)

    # Store the event before notifying the backend synchronously.
    def receive_event(self, stFrontendToBackendData: ST_FrontendToBackendData) -> None:
        self._stFrontendToBackendData = stFrontendToBackendData
        if self._event_callback is not None:
            self._event_callback(stFrontendToBackendData)

    def get_frontend_to_backend_data(self) -> ST_FrontendToBackendData | None:
        return self._stFrontendToBackendData
