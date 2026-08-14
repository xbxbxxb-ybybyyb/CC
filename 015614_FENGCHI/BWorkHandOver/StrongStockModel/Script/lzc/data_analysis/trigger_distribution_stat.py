# @Time : 2020/11/25 9:46
# @Author : Zhichen Lu
# @File : trigger_distribution_stat.py

import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import gc
import matplotlib.pyplot as plt
import seaborn as sns
from multiprocessing import Pool, Manager
from StrongStockModel.conf.path_config import root_path
from dataApi.getData import get_daily_1factor
sns.set()

profit_list, daily_stat_list, signaly_stat_list, cash_occupy_list, daily_buy, daily_holding, daily_profit_list,daily_profit_rate_list = [], [], [], [], [], [], [], []

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/5min/'  # root_path + 'backtest_result_all_mkt_10bp_cost_revised_framework20201013/'
file_list = os.listdir(base_path)
file_list = sorted(list(filter(lambda x: x.endswith('.xlsx') and 'InSample' in x, file_list)))

for file_name in file_list:
    all_data = pd.read_excel(base_path + file_name, sheet_name=None, index_col=0)
    data = all_data['逐笔持仓统计']
    data['start_date'] = data['start'].apply(lambda  x: x//10000)
    data['start_time'] = data['start'].apply(lambda  x: x%10000)
    data['end_date'] = data['end'].apply(lambda x: x // 10000)
    data['end_time'] = data['end'].apply(lambda x: x % 10000)
    check_distribut_5min = data.groupby('start_time').size()