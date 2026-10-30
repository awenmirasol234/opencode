import io
import tempfile
import unittest
from pathlib import Path

from docker_deployment.logger import (
    ASCII_SPINNER_FRAMES,
    SPINNER_FRAMES,
    Logger,
    redact_text,
    spinner_frames,
)


class LoggerTests(unittest.TestCase):
    def test_spinner_frames_use_unicode_when_the_stream_supports_it(self):
        class UnicodeStream:
            encoding = "utf-8"

        self.assertEqual(spinner_frames(UnicodeStream()), SPINNER_FRAMES)

    def test_spinner_frames_use_ascii_when_the_stream_does_not_support_unicode(self):
        class AsciiStream:
            encoding = "ascii"

        self.assertEqual(spinner_frames(AsciiStream()), ASCII_SPINNER_FRAMES)

    def test_stage_spinner_stops_before_the_next_log_message(self):
        class TerminalStream(io.StringIO):
            def isatty(self):
                return True

        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.info("Working on the deployment.")
            logger.success("The deployment completed.")
            logger.close()

            terminal_text = output.getvalue()

        self.assertIn(
            "\r\033[36m[INFO]\033[0m "
            + SPINNER_FRAMES[0]
            + " Working on the deployment.",
            terminal_text,
        )
        self.assertIn("\r\033[2K", terminal_text)
        self.assertIn("\033[32m[PASS]\033[0m The deployment completed.\n", terminal_text)

    def test_colors_only_the_log_level_on_interactive_output(self):
        class TerminalStream(io.StringIO):
            def isatty(self):
                return True

        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.info("The deployment started.")
            logger.close()

            terminal_text = output.getvalue()

        self.assertIn(
            "\033[36m[INFO]\033[0m "
            + SPINNER_FRAMES[0]
            + " The deployment started.",
            terminal_text,
        )

    def test_redacts_secret_values_and_key_value_secrets(self):
        message = "TOKEN=token-value password: secret-value"

        redacted = redact_text(message, ["token-value", "secret-value"])

        self.assertNotIn("token-value", redacted)
        self.assertNotIn("secret-value", redacted)
        self.assertIn("[REDACTED]", redacted)

    def test_logger_does_not_write_secret_values(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = io.StringIO()
            logger = Logger(log_path, output, ["secret-value"])

            logger.fail("The command returned password: secret-value.")
            logger.close()

            file_text = log_path.read_text(encoding="utf-8")
            terminal_text = output.getvalue()

        self.assertNotIn("secret-value", file_text)
        self.assertNotIn("secret-value", terminal_text)

    def test_writes_uncolored_timestamped_file_logs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = io.StringIO()
            logger = Logger(log_path, output)

            logger.info("The deployment started.")
            logger.close()

            file_text = log_path.read_text(encoding="utf-8")

        self.assertIn("[INFO] The deployment started.", file_text)
        self.assertNotIn("\033[", file_text)


if __name__ == "__main__":
    unittest.main()
