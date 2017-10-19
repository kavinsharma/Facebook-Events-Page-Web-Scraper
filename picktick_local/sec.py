import time
from datetime import datetime

date_str = "2008-11-10 17:53:59"
dt_obj = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print dt_obj

timestamp = time.mktime(dt_obj)
print repr(timestamp)

