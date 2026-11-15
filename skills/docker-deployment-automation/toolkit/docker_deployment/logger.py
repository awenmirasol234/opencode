import re
import sys
import threading
from datetime import datetime
from pathlib import Path

SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|token|secret|api[_-]?key|private[_-]?key)\s*[:=]\s*([^\s,;]+)"
)

SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
ASCII_SPINNER_FRAMES = ("|", "/", "-", "\\")
SPINNER_INTERVAL_SECONDS = 0.1

LEVEL_COLORS = {
    "ok": "\033[32m",
    "warn": "\033[33m",
    "fail": "\033[31m",
}


def spinner_frames(stream):
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        encoding = "utf-8"
    try:
        "".join(SPINNER_FRAMES).encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return ASCII_SPINNER_FRAMES
    return SPINNER_FRAMES


def redact_text(text, secret_values=None):
    redacted = str(text)
    if secret_values:
        for value in secret_values:
            if value:
                redacted = redacted.replace(str(value), "[REDACTED]")
    redacted = SECRET_PATTERN.sub(r"\1=[REDACTED]", redacted)
    return redacted


class Logger:
    def __init__(self, log_path, stream=None, secret_values=None):
        self.log_path = log_path
        self.stream = stream
        if self.stream is None:
            self.stream = sys.stdout
        if not secret_values:
            secret_values = []
        self.secret_values = secret_values
        self.use_color = bool(self.stream.isatty())
        self.frames = spinner_frames(self.stream)
        self.frame_index = 0
        self.spinner_lock = threading.Lock()
        self.spinner_stop = None
        self.spinner_thread = None
        self.file = None
        try:
            path = Path(log_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self.file = path.open("a", encoding="utf-8")
        except OSError:
            self.file = None

    def next_frame(self):
        frames = self.frames
        frame = frames[self.frame_index % len(frames)]
        self.frame_index += 1
        return frame

    def write_spinner_frame(self, frame, message):
        with self.spinner_lock:
            self.stream.write("\r{0} {1}".format(frame, message))
            self.stream.flush()

    def run_spinner(self, stop_event, message):
        try:
            while not stop_event.wait(SPINNER_INTERVAL_SECONDS):
                frame = self.next_frame()
                self.write_spinner_frame(frame, message)
        except (OSError, ValueError):
            return

    def start_spinner(self, message):
        clean_message = redact_text(message, self.secret_values)
        self.stop_spinner()
        frame = self.next_frame()
        if not self.use_color:
            print("{0} {1}".format(frame, clean_message), file=self.stream)
            return
        self.write_spinner_frame(frame, clean_message)
        stop_event = threading.Event()
        self.spinner_stop = stop_event
        thread = threading.Thread(
            target=self.run_spinner,
            args=(stop_event, clean_message),
            daemon=True,
        )
        self.spinner_thread = thread
        thread.start()

    def stop_spinner(self):
        stop_event = self.spinner_stop
        thread = self.spinner_thread
        self.spinner_stop = None
        self.spinner_thread = None
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

    def write(self, level, message):
        clean_message = redact_text(message, self.secret_values)
        label = "[{0}]".format(level.upper())
        self.stop_spinner()
        if self.use_color:
            color = LEVEL_COLORS.get(level, "")
            print("{0}{1}\033[0m {2}".format(color, label, clean_message), file=self.stream)
        else:
            print("{0} {1}".format(label, clean_message), file=self.stream)
        if self.file:
            stamp = datetime.now().isoformat(timespec="seconds")
            self.file.write("{0} {1} {2}\n".format(stamp, label, clean_message))
            self.file.flush()

    def info(self, message):
        self.start_spinner(message)

    def ok(self, message):
        self.write("ok", message)

    def warn(self, message):
        self.write("warn", message)

    def fail(self, message):
        self.write("fail", message)

    def close(self):
        self.stop_spinner()
        if self.file:
            self.file.close()
            self.file = None
