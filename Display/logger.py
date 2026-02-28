import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level=logging.INFO):
    """Configure root logger with rotating file and console handlers.

    Args:
        level: Logging level (default: INFO). FPS metrics use DEBUG,
               sensor warnings use WARNING, C library failures use ERROR.
    """
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")

    file_handler = RotatingFileHandler(
        log_dir / "scope.log", maxBytes=5_000_000, backupCount=3
    )
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
