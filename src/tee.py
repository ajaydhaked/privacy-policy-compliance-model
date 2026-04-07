import sys

class Tee:
    """Write to both the terminal and a file simultaneously."""
    def __init__(self, file_path):
        self._terminal = sys.stdout
        self._file     = open(file_path, "w", encoding="utf-8")

    def write(self, message):
        self._terminal.write(message)
        self._file.write(message)

    def flush(self):
        self._terminal.flush()
        self._file.flush()

    def close(self):
        self._file.close()