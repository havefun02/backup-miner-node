import logging

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
            cls._instance._logger = cls._create_logger()
        return cls._instance

    @staticmethod
    def _create_logger(log_file="app.log", log_level=logging.INFO):
        # Create a logger
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        # Create a file handler and set the level
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s     -      %(levelname)s      -     %(message)s')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

        return logger

    def log_info(self, message):
        self._logger.info(message)

    def log_warning(self, message):
        self._logger.warning(message)

    def log_error(self, message):
        self._logger.error(message)

    def log_critical(self, message):
        self._logger.critical(message)

# # Example Usage:
# if __name__ == "__main__":
#     # Creating instances of SingletonLogger
#     logger1 = Logger()
#     logger2 = Logger()

#     # Both instances refer to the same logger
#     assert logger1 is logger2

#     # Log some messages
#     logger1.log_info("This is an informational message.")
#     logger2.log_warning("This is a warning message.")
#     logger1.log_error("This is an error message.")
#     logger2.log_critical("This is a critical message.")
