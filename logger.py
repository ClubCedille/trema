import logging
from datetime import datetime
import pytz

montreal_tz = pytz.timezone('America/Montreal')

class TimezoneFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        local_time = datetime.fromtimestamp(record.created, montreal_tz)
        if datefmt:
            return local_time.strftime(datefmt)
        return local_time.isoformat()

formatter = TimezoneFormatter(
    fmt='%(asctime)s [%(levelname)s] %(name)s.%(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger('trema_logger')
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
