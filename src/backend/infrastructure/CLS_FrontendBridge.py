from ..domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData


class CLS_FrontendBridge:
    def __init__(self) -> None:
        self._stBackendToFrontendData: list[ST_BackendToFrontendData] = []

    # Copy the list while preserving the prepared structures.
    def set_backend_to_frontend_data(self, stBackendToFrontendData: list[ST_BackendToFrontendData]) -> None:
        self._stBackendToFrontendData = list(stBackendToFrontendData)

    # Expose the structures without allowing external list changes.
    def get_backend_to_frontend_data(self) -> list[ST_BackendToFrontendData]:
        return list(self._stBackendToFrontendData)
