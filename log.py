import logging
import colorlog


def logger_config() -> logging.Logger:
    log = logging.getLogger()

    log.setLevel(logging.INFO)
    format_str = "%(asctime)s.%(msecs)d %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    cformat = "%(log_color)s" + format_str
    colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "bold_yellow",
        "ERROR": "bold_red",
        "CRITICAL": "bold_purple",
    }
    formatter = colorlog.ColoredFormatter(cformat, date_format, log_colors=colors)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return log
