from typing import Optional, Union
import time
from datetime import datetime, timezone, timedelta


def parse_params(params: str):
    if params.startswith('0x'):
        params = params[2:]
    while params:
        print(params[:64])
        params = params[64:]


def unix_to_strtime(unix_time: Union[int, float, str] = None, utc_offset: Optional[int] = None,
                    format: str = '%d.%m.%Y %H:%M:%S') -> str:
    if not unix_time:
        unix_time = time.time()

    if isinstance(unix_time, str):
        unix_time = int(unix_time)

    if utc_offset is None:
        strtime = datetime.fromtimestamp(unix_time)
    elif utc_offset == 0:
        strtime = datetime.utcfromtimestamp(unix_time)
    else:
        strtime = datetime.utcfromtimestamp(unix_time).replace(tzinfo=timezone.utc).astimezone(
            tz=timezone(timedelta(seconds=utc_offset * 60 * 60)))

    return strtime.strftime(format)
