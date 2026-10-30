import io
import tempfile
import unittest
from pathlib import Path

from docker_deployment.logger import Logger, redact_text


class LoggerTests(unittest.TestCase):
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

        self.assertIn("\033[36m[INFO]\033[0m The deployment started.\n", terminal_text)

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
