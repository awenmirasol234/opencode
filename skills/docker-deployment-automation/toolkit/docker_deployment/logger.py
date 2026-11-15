import re
import sys
from datetime import datetime
from pathlib import Path

SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|token|secret|api[_-]?key|private[_-]?key)\s*[:=]\s*([^\s,;]+)"
)

LEVEL_COLORS = {
    "info": "\033[36m",
    "ok": "\033[32m",
    "warn": "\033[33m",
    "fail": "\033[31m",
}


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
        self.file = None
        try:
            path = Path(log_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self.file = path.open("a", encoding="utf-8")
        except OSError:
            self.file = None

    def write(self, level, message):
        clean_message = redact_text(message, self.secret_values)
        label = "[{0}]".format(level.upper())
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
        self.write("info", message)

    def ok(self, message):
        self.write("ok", message)

    def warn(self, message):
        self.write("warn", message)

    def fail(self, message):
        self.write("fail", message)

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
