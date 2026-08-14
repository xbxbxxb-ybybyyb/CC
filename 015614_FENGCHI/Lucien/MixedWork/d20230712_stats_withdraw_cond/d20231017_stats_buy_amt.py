# coding: utf-8
# Author：fengchi863
# Date ：2023/10/17 10:35

import pandas as pd
import numpy as np
import re
import datetime as dt
from dataApi.sendInfo import send_file
from tqdm import tqdm
from xquant.marketdata import MarketData
import os
from datetime import datetime, timedelta
from
mdp = MarketData()

tick_path = '/data/user/015614/TEST/及时撤单/tick_data/'
trans_path = '/data/user/015614/TEST/及时撤单/trans_data/'

ORDER_MONEY = 1000000
TIME_INTERVAL = 60  # 秒

project1_v3_path='/data/group/800463/project/project1_prod/left_v2212/'
basic_file_path_europa = project1_v3_path + 'Basic_zt_test/Basic_zt_001.h5'

project1_path='/data/group/800463/project/project1_prod/'
result_path_europa = project1_path + 'LabelProfit_fix/001/'

param = {'sell_vol_pct': 0.15,
         'max_amt': 2000 * 10000,
         'max_vol': 300,
         'lag_ms_SH': 250,
         'lag_ms_SZ': 20,
         'cover_amt': 1500}

from xquant.factordata import FactorData
s = FactorData()
start_date = 20220518
end_date = 20230518
# factor_LabelProfit_zt(start_date, end_date, param, basic_file_path_europa, result_path_europa, 'twap')