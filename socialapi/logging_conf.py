import logging
from logging.config import dictConfig

from socialapi.config import DevConfig, ProdConfig, config


def obfuscated(email: str, obfuscated_length: int) -> str:
    characters = email[:obfuscated_length]
    first, last = email.split("@")

    return characters + ("*" * (len(first) - obfuscated_length)) + "@" + last


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        record.test_property = "verycosy"

        # 로깅 메서드에 전달된 extra 값
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)

        return True


filters = ["correlation_id", "email_obfuscation"]
handlers = ["default", "rotating_file"]
if isinstance(config, ProdConfig):
    handlers.append("someplatform")


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    # filter = asgi_correlation_id.CorrelationIdFilter(uuid_length=8, default_value="-")
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "[%(test_property)s] (%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    # "class": "logging.Formatter",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    # format 키의 값으로 사용된 변수들을 알아서 json으로 뽑아준다
                    "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    # "class": "logging.StreamHandler",
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": filters,
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "socialapi.log",
                    "maxBytes": 1024 * 1024,  # 1MB
                    "backupCount": 5,
                    "encoding": "utf8",
                    "filters": filters,
                },
                # + 외부 logging solution..
            },
            # 최상위에 root logger가 있음
            "loggers": {
                "uvicorn": {
                    "handlers": handlers,
                    "level": "INFO",
                },
                "socialapi": {
                    "handlers": handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "databases": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
            },
        }
    )
