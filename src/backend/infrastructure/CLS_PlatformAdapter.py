import ctypes

# Isolate access to Windows platform services.
class CLS_PlatformAdapter:
    # Return the primary monitor dimensions, rejecting invalid Windows results.
    def get_screen_dimensions(self) -> tuple[int, int]:
        # SM_CXSCREEN and SM_CYSCREEN describe the primary monitor.
        screen_width    = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height   = ctypes.windll.user32.GetSystemMetrics(1)
        if screen_width <= 0 or screen_height <= 0:
            raise RuntimeError("Windows returned invalid screen dimensions.")
        return screen_width, screen_height
