
import argparse

from src.backend.application.CLS_CommandManager         import CLS_CommandManager
from src.backend.application.CLS_LayoutManager          import CLS_LayoutManager
from src.backend.application.CLS_SectionManager         import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager  import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController       import CLS_ViewerController
from src.backend.infrastructure.CLS_PlatformAdapter     import CLS_PlatformAdapter
from src.backend.infrastructure.CLS_FrontendBridge      import CLS_FrontendBridge

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Viewer")
    parser.add_argument("file_path", 
                        nargs = "?", 
                        help  = "File to open")
                        
    args   = parser.parse_args(argv)
    print(f"\n[TRACE TEMP][main] Reception du chemin\n  file_path : {args.file_path}\n")

    clsCommandManager        = CLS_CommandManager()
    clsLayoutManager         = CLS_LayoutManager()
    clsSectionManager        = CLS_SectionManager(clsLayoutManager)
    clsPlatformAdapter       = CLS_PlatformAdapter()
    clsTimerLifecycleManager = CLS_TimerLifecycleManager()
    clsFrontendBridge        = CLS_FrontendBridge()
    clsViewerController      = CLS_ViewerController(
                                                    clsSectionManager,
                                                    clsTimerLifecycleManager,
                                                    clsFrontendBridge
    )

    width, height            = clsPlatformAdapter.get_screen_dimensions()
    clsLayoutManager.set_screen_dimensions(width, height)

    if args.file_path is not None:
        print("[TRACE TEMP][main] Appel de CLS_CommandManager.create_open_command()")
        st_command = clsCommandManager.create_open_command(args.file_path)
        clsViewerController.process_command(st_command)

if __name__ == "__main__":
    main()
