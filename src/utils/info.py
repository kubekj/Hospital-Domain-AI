
import debugpy

class Info:
    test_name: str = "default_test"
    level_name: str = "default_level"
    test_folder: str = "./tests"

def handle_debug(is_debug_mode: bool) -> None:
    if is_debug_mode:
        debugpy.listen(("localhost", 1234))  # Open a debugging server at localhost:1234
        debugpy.wait_for_client()  # Wait for the debugger to connect
        debugpy.breakpoint()  # Ensure the program starts paused
    