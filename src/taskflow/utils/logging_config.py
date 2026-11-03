import logging

from pathlib import Path


def configure_logging(log_file="data/taskflow.log"):
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(path)
        ]
    )