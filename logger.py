import logging
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    def __init__(
        self, logger_name: str = "mia_cat", log_level: int = logging.INFO
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)

        # create a formatter
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # create a handler and set the formatter
        handler = TimedRotatingFileHandler(
            f"{logger_name}.log", when="m", interval=1, backupCount=10
        )
        handler.setFormatter(fmt)

        # add the handler to the logger
        self.logger.addHandler(handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)


# if __name__ == "__main__":
#     # Logger Test
#     TEST_LOG_PATH = "./log/test"
#
#     logger = Logger(TEST_LOG_PATH)
#     logger.info("This is an info message")
#     logger.debug("This is a debug message")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")
#     logger.critical("This is a critical message")
