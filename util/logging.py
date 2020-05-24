import sys


class Logger:
    def __init__(self, debug: bool):
        self.debug = debug

    def is_debug_mode(self):
        return self.debug

    def log_debug(self, message: str):
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stdout)

    @staticmethod
    def log_info(message: str):
        print(f"{message}", file=sys.stdout)

    @staticmethod
    def log_error(message: str):
        print(f"{message}", file=sys.stderr)