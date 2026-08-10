import multifactor.IO.IO as IO
from multifactor.IO.IO_enums import *
# import multifactor.IO.naming_config as nc
# import multifactor.utility.dt as tdt
# import multifactor.utility.common as ut
# import math
# import pandas as pd
# import numpy as np
# import datetime
# import logging
# import os
# Z:/warehouse/prod/md/CHINA_STOCK/DAILY/HTSC/MD_CHINA_STOCK_DAILY_HTSC.h5
start_date,end_date = 20180101,20180527
take_list = ['close']
base_data = IO.read_data([start_date,end_date],columns=take_list ,ftype=FType.MD,dfreq=DFreq.DAILY,dsource=DSource.WIND)
# base_data = IO.read_data([start_date, end_date], columns=['amt', 'mkt_cap_ard', 'close'])
print(base_data)