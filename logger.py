import os

OUTPUT_DIR = os.path.join("data", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROCESS_LOG = os.path.join(OUTPUT_DIR, "process.md")
RESULT_LOG = os.path.join(OUTPUT_DIR, "result.md")
DEBUG_LOG = os.path.join(OUTPUT_DIR, "debug.md")

def log_process(message: str) -> None:
    with open(PROCESS_LOG, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def log_result(message: str) -> None:
    with open(RESULT_LOG, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def log_debug(message: str) -> None:
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(message + "\n")
