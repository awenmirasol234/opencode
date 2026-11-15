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


class TerminalStream(io.StringIO):
    def isatty(self):
        return True


class LoggerTests(unittest.TestCase):
    def test_spinner_frames_use_unicode_when_the_stream_supports_it(self):
        class UnicodeStream:
            encoding = "utf-8"

        self.assertEqual(spinner_frames(UnicodeStream()), SPINNER_FRAMES)

    def test_spinner_frames_use_ascii_when_the_stream_does_not_support_unicode(self):
        class AsciiStream:
            encoding = "ascii"

        self.assertEqual(spinner_frames(AsciiStream()), ASCII_SPINNER_FRAMES)

    def test_colors_only_the_log_level_on_interactive_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.ok("The deployment started.")
            logger.close()

            terminal_text = output.getvalue()

        self.assertIn(
            "\033[32m[OK]\033[0m The deployment started.\n",
            terminal_text,
        )

    def test_a_loading_message_shows_the_spinner_without_a_log_level(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.info("Deploying the application.")
            logger.close()

            terminal_text = output.getvalue()

        self.assertIn(
            "\r" + SPINNER_FRAMES[0] + " Deploying the application.",
            terminal_text,
        )
        self.assertNotIn("[INFO]", terminal_text)

    def test_the_spinner_line_is_erased_before_the_finished_line(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.info("Deploying the application.")
            logger.ok("The application deployment completed successfully.")
            logger.close()

            terminal_text = output.getvalue()

        self.assertIn("\r\033[2K", terminal_text)
        self.assertIn(
            "\033[32m[OK]\033[0m The application deployment completed successfully.\n",
            terminal_text,
        )

    def test_a_loading_message_is_not_written_to_the_log_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.info("Deploying the application.")
            logger.ok("The application deployment completed successfully.")
            logger.close()

            file_text = log_path.read_text(encoding="utf-8")

        self.assertNotIn("Deploying the application.", file_text)
        self.assertIn("[OK] The application deployment completed successfully.", file_text)

    def test_a_warning_line_shows_the_level_without_the_spinner(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.warn("The protected path was preserved: data.")
            logger.close()

            terminal_text = output.getvalue()
            file_text = log_path.read_text(encoding="utf-8")

        self.assertIn("\033[33m[WARN]\033[0m The protected path was preserved: data.\n", terminal_text)
        self.assertNotIn(SPINNER_FRAMES[0], terminal_text)
        self.assertIn("[WARN] The protected path was preserved: data.", file_text)

    def test_a_failure_line_shows_the_level_without_the_spinner(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "deployment.log"
            output = TerminalStream()
            logger = Logger(log_path, output)

            logger.fail("The application deployment failed.")
            logger.close()

            terminal_text = output.getvalue()
            file_text = log_path.read_text(encoding="utf-8")

        self.assertIn("\033[31m[FAIL]\033[0m The application deployment failed.\n", terminal_text)
        self.assertNotIn(SPINNER_FRAMES[0], terminal_text)
        self.assertIn("[FAIL] The application deployment failed.", file_text)

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

            logger.ok("The deployment started.")
            logger.close()

            file_text = log_path.read_text(encoding="utf-8")

        self.assertIn("[OK] The deployment started.", file_text)
        self.assertNotIn("\033[", file_text)


if __name__ == "__main__":
    unittest.main()
