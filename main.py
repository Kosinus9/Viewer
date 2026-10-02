
import argparse

from src.backend.application.CLS_CommandManager         import CLS_CommandManager
from src.backend.application.CLS_LayoutManager          import CLS_LayoutManager
from src.backend.application.CLS_SectionManager         import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager  import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController       import CLS_ViewerController

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Viewer")
    parser.add_argument("file_path", 
                        nargs = "?", 
                        help  = "File to open")
                        
    args   = parser.parse_args(argv)
    print(f"[TRACE TEMP][main] Reception de file_path={args.file_path!r}")

    command_manager          = CLS_CommandManager()
    section_manager          = CLS_SectionManager()
    layout_manager           = CLS_LayoutManager()
    timer_lifecycle_manager  = CLS_TimerLifecycleManager()
    viewer_controller        = CLS_ViewerController(
                                                    section_manager, 
                                                    layout_manager, 
                                                    timer_lifecycle_manager
    )

    if args.file_path is not None:
        print("[TRACE TEMP][main] Appel de CLS_CommandManager.create_open_command()")
        st_command = command_manager.create_open_command(args.file_path)
        viewer_controller.process_command(st_command)

if __name__ == "__main__":
    main()

    