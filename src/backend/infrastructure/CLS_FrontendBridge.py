from collections.abc                              import Callable

from ..domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from ..domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData


class CLS_FrontendBridge:
    # Initialise les deux sens de communication sans donnée ni callback.
    def __init__(self) -> None:
        self._stBackendToFrontendData:  list[ST_BackendToFrontendData]  = []
        self._stFrontendToBackendData:  ST_FrontendToBackendData | None = None
        self._event_callback:           Callable[[ST_FrontendToBackendData], object] | None = None

    # Enregistre le destinataire des événements sans dépendre du Controller.
    def set_event_callback(self, callback: Callable[[ST_FrontendToBackendData], object]) -> None:
        self._event_callback = callback

    # Remplace la liste préparée tout en conservant les structures reçues.
    def set_backend_to_frontend_data(self, stBackendToFrontendData: list[ST_BackendToFrontendData]) -> None:
        self._stBackendToFrontendData = list(stBackendToFrontendData)

    # Retourne une copie de la liste ; les structures restent partagées.
    def get_backend_to_frontend_data(self) -> list[ST_BackendToFrontendData]:
        return list(self._stBackendToFrontendData)

    # Réutilise le chemin événementiel pour recevoir les données frontend.
    def set_frontend_to_backend_data(self, stFrontendToBackendData: ST_FrontendToBackendData) -> None:
        self.receive_event(stFrontendToBackendData)

    # Conserve l'événement puis notifie immédiatement le callback, sans interprétation.
    def receive_event(self, stFrontendToBackendData: ST_FrontendToBackendData) -> None:
        self._stFrontendToBackendData = stFrontendToBackendData
        if self._event_callback is not None:
            self._event_callback(stFrontendToBackendData)

    # Expose le dernier événement sans le consommer ; None avant réception.
    def get_frontend_to_backend_data(self) -> ST_FrontendToBackendData | None:
        return self._stFrontendToBackendData
