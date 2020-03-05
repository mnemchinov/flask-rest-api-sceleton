import datetime

from bin.common.Const import DATE_FORMAT
from bin.common.Styles import Style


def _now():
    return datetime.datetime.now().strftime(DATE_FORMAT)


def normal(message: str = ""):
    _log_message(f"     {message}")


def info(message: str = ""):
    _log_message(f"{Style.info('INF')}: {message}")


def ok(message: str = ""):
    _log_message(f"{Style.ok('OK ')}: {message}")


def warning(message: str = ""):
    _log_message(f"{Style.warning('WRN')}: {message}")


def error(message: str = ""):
    _log_message(f"{Style.error('ERR')}: {message}")


def header(message: str = ""):
    _log_message(f"{Style.header(message)}")


# normal = 0
# info = 1
# ok = 2
# warning = 3
# Header = 4
#
# class levels:
#     normal: normal
#     info: info
#     ok: ok
#     warning: warning
#     Header: Header


def _log_message(message: str = "", level=0):
    print(f"{_now()}: {message} {Style.Colors.reset}")
