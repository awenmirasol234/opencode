import os
import re
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import TextIO, Tuple


SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|token|secret|api[_-]?key|private[_-]?key)\s*[:=]\s*([^\s,;]+)"
)
SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
ASCII_SPINNER_FRAMES = ("|", "/", "-", "\\")
SPINNER_INTERVAL_SECONDS = 0.1


def spinner_frames(stream: TextIO) -> Tuple[str, ...]:
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        "".join(SPINNER_FRAMES).encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return ASCII_SPINNER_FRAMES
    return SPINNER_FRAMES


def redact_text(text, secret_values=None):
    if text is None:
        return ""

    # Redact known values and common secret formats before logging.
    redacted = str(text)
    if secret_values:
        for value in secret_values:
            if value:
                redacted = redacted.replace(str(value), "[REDACTED]")

    redacted = SECRET_PATTERN.sub(r"\1=[REDACTED]", redacted)
    return redacted


class Logger:
    def __init__(self, log_path, stream=None, secret_values=None):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.log_path.open("a", encoding="utf-8")
        self.stream = stream or sys.stdout
        self.secret_values = secret_values or []
        # Only interactive terminals should receive color codes.
        self.use_color = self.stream.isatty() and not os.environ.get("NO_COLOR")
        self.spinner_lock = threading.Lock()
        self.spinner_stop = None
        self.spinner_thread = None

    def close(self):
        self.stop_spinner()
        if not self.file.closed:
            self.file.close()

    def _write_spinner_frame(self, frame):
        with self.spinner_lock:
            self.stream.write("\r" + frame)
            self.stream.flush()

    def _run_spinner(self, frames, stop_event):
        frame_index = 1
        try:
            while not stop_event.wait(SPINNER_INTERVAL_SECONDS):
                self._write_spinner_frame(frames[frame_index % len(frames)])
                frame_index += 1
        except (OSError, ValueError):
            return

    def start_spinner(self):
        if not self.use_color:
            return

        self.stop_spinner()
        frames = spinner_frames(self.stream)
        stop_event = threading.Event()
        self._write_spinner_frame(frames[0])
        thread = threading.Thread(
            target=self._run_spinner,
            args=(frames, stop_event),
            daemon=True,
        )
        self.spinner_stop = stop_event
        self.spinner_thread = thread
        thread.start()

    def stop_spinner(self):
        stop_event = self.spinner_stop
        thread = self.spinner_thread
        if stop_event is None:
            return

        stop_event.set()
        if thread is not None and thread is not threading.current_thread():
            thread.join()

        with self.spinner_lock:
            try:
                self.stream.write("\r\033[2K")
                self.stream.flush()
            except (OSError, ValueError):
                pass
        self.spinner_stop = None
        self.spinner_thread = None

    def _write(self, level, message):
        self.stop_spinner()
        # Use the same redacted message for the file and terminal.
        clean_message = redact_text(message, self.secret_values)
        level_label = "[{0}]".format(level)
        line = "{0} {1}".format(level_label, clean_message)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.file.write("[{0}] {1}\n".format(timestamp, line))
        self.file.flush()

        terminal_line = line
        if self.use_color:
            color = ""
            if level == "INFO":
                color = "\033[36m"
            elif level in (" OK ", "PASS"):
                color = "\033[32m"
            elif level == "WARN":
                color = "\033[33m"
            elif level == "FAIL":
                color = "\033[31m"
            terminal_line = color + level_label + "\033[0m " + clean_message
        self.stream.write(terminal_line + "\n")
        self.stream.flush()

    def info(self, message):
        self._write("INFO", message)
        self.start_spinner()

    def ok(self, message):
        self._write(" OK ", message)

    def success(self, message):
        self._write("PASS", message)

    def warning(self, message):
        self._write("WARN", message)

    def fail(self, message):
        self._write("FAIL", message)
