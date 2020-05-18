# region App data
import datetime
import re

APP_NAME = "Flask Rest Api Skeleton"
APP_SHORT_NAME = "FRAS"
APP_DESCRIPTION = "Skeleton of the application for developing the REST API of the service"
APP_VERSION = "0.1.1 (Alpha)"
APP_COPYRIGHT = "NEMCHINOV.PRO 2020"
APP_API_PREFIX = "v1"

# endregion

# region Other
EMPTY_DATE = datetime.datetime(1, 1, 1, 0, 0, 0)
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"
DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_SQL_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DATETIME_FORMAT_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')

OK = "ok"
ERR = "error"
INFO = "info"

# endregion
