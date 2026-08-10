kind = 'IC'
dtype = 'IndexStock'
end_date_standard = '20210101'
start_date_standard = '20201101'
days_interval = 50

save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_prod/cfg_fullhistory/' % kind

import sys
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_rewrite/factor_framework')
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_rewrite/%s_factors' % str.lower(kind))
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_rewrite/utils')
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor
from data_player import DataPlayer
from data_center import DataCenter
from multifactor.IO import IO
import multifactor.utility.dt as udt
from task_runner import TaskRunner
from future_factor import FutureFactor
import datetime
from function_tools import *
from scipy.stats import skew
import os, importlib
import time
import datetime
fs = [f for f in os.listdir('/data/user/015626/data/share/Code/factor_rewrite/%s_factors' % str.lower(kind)) if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])

ts = TaskRunner(save_factor=True, factor_root_path='/data/user/015626/data/share/LOCAL_DATA/factor_code_and_value/factor_value/append_20210902/')

from ss1_cfg_zf import ss1_cfg_zf
factor = ss1_cfg_zf()

dc = DataCenter(variety = 'IC', data_type= factor.data_type, instrument_type=factor.instrument_type, data_dict = factor.data_dict, 
                    start_date = '20201115', end_date = '20201231', days_past = factor.days_past)

raw, norm = ts.run_factor_multi_day(factor = factor, variety = 'IC', data_center = dc, start_date = '20201201', end_date = '20201231', ncore=24)