import threading
import time

class HumanResumeTimeoutError(Exception):
    """Raised when no human input is received before timeout."""
    pass

def pause_for_human_resume(timeout=300):
    """
    Pause execution until the user presses Enter or the timeout elapses.
    If the timeout elapses with no input, raise HumanResumeTimeoutError.
    """
    resume_event = threading.Event()

    def wait_for_input():
        input("⏸️  Paused — press [Enter] to resume early...\n")
        resume_event.set()

    # Start a background thread waiting for user input
    threading.Thread(target=wait_for_input, daemon=True).start()
    print(f"(Auto-cancel in {timeout//60} min if no input)\n")

    if not resume_event.wait(timeout):
        # Timed out without human action
        raise HumanResumeTimeoutError(
            f"No input received after {timeout} seconds; aborting."
        )

    print("▶️  Resuming script...")
