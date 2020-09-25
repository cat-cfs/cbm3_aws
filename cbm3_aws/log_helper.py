import datetime
import logging


def start_logging(level):
    rootLogger = logging.getLogger()

    logFormatter = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M")

    log_path = "cbm3_aws_log_{date}.log".format(
        date=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    fileHandler = logging.FileHandler(log_path, "w")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(level)


def get_logger():
    return logging.getLogger("cbm3_aws")
