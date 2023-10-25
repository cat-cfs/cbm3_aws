import datetime
import logging


def start_logging(name: str, level: str) -> None:
    rootLogger = logging.getLogger()

    logFormatter = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
    )

    log_path = "{name}_{date}.log".format(
        name=name, date=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    )
    fileHandler = logging.FileHandler(log_path, "w")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"cbm3_aws.{name}")
