import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import time
from multiprocessing import Pool

import os
import gc
import numpy as np
import pandas as pd
from xquant.marketdata import MarketData
from xquant.xqutils.helper import multicore_init

from dataApi.getData import get_daily_1factor
from dataApi.stockList import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date, get_date_range
from dataApi import aimr
from dataApi.sendInfo import send_file
from LimitUpStrategy.CallAuction import clean_tick_auction_data, calc_auction_factor

def load_auction_factor_1d(date, address='/arch1/user/015836/LimitUpStrategy/factor/'):
    fp = np.memmap(f'{address}/{date}.npy', 'float64', 'r', 128).reshape(-1, 70)
    arr = fp.__array__()
    del fp
    # print(time.strftime('%Y-%m-%d %H:%M:%S'), date)
    return arr


root_path = '/arch1/user/015836/LimitUpStrategy/'

# 1 完成率
date_list = get_date_range(20130104, 20211117)
finish_date_list = sorted([int(x[:-4]) for x in os.listdir(f'{root_path}/finish_tag/')])
unfinished_date_list = sorted(list(set(date_list) - set(finish_date_list)))  # []

# 2 错误样本分析
error_list1 = sorted([tuple(int(y) for y in x[:-4].split('_')) for x in os.listdir(f'{root_path}/error/')])
error_list = error_list1[72:]
md = MarketData()
error_analyse = []
for j, (date, code) in enumerate(error_list1):
    code = trans_int2windcode(code)
    date = str(date)
    tick = md.get_data_by_date('Stock', code, date, trading_phase_code=['1', '2'])
    error_analyse.append([j, tick['TradingPhaseCode'].iloc[0], tick['PreClosePx'].iloc[0], tick['LastPx'].iloc[0], tick['TotalVolumeTrade'].iloc[0]])
    print(j, tick['TradingPhaseCode'].iloc[0], tick['PreClosePx'].iloc[0], tick['LastPx'].iloc[0], tick['TotalVolumeTrade'].iloc[0])

# arr = np.load(f'{root_path}/factor/20170221.npy')

for j, (date, code) in enumerate(error_list1):
    tick1, tick2 = clean_tick_auction_data(md, date, code)
    factor = calc_auction_factor(date, code, tick1, tick2)
    print(j)

# 3 全样本描述
date_list = get_date_range(20130104, 20211123)
columns = [
    'date', 'code', 'delay_sec', 'T_tender_pct_mean', 'T_tender_pct_std', 'T_tender_max_up', 'T_tender_max_down', 'T_tender_mup',
    'T_tender_mup_len', 'T_tender_mdd', 'T_tender_mdd_len', 'T_tender_bid_amt_max_down', 'T_tender_ask_amt_max_down',
    'T_tender_bid_ff_rate_down', 'T_tender_ask_ff_rate_down', 'T_tender_bidask_amt_mean', 'T_tender_bidask_amt_std',
    'T_tender_bidask_ff_rate_mean', 'T_tender_bidask_ff_rate_std', 'T_tender_bidupask_rate', 'delay_sec2',
    'T_tender_bid_ff_rate', 'T_tender_ask_ff_rate', 'T_tender_bidmask_ff_rate', 'T_tender_bidmask_amt', 'T_open_bid_amt',
    'T_open_ask_amt', 'T_open_bidask_amt', 'T_open_bid_ff_rate', 'T_open_ask_ff_rate', 'T_open_bidask_ff_rate',
    'T_open_bidivask', 'T_open_pct_bid2c', 'T_open_pct_ask2c', 'T_open_pct_bidask', 'T_open_main_bid_amt',
    'T_open_main_ask_amt', 'T_open_main_bidask_amt', 'T_open_main_bid_ff_rate', 'T_open_main_ask_ff_rate',
    'T_open_main_bidask_ff_rate', 'T_open_main_bidivask', 'T_open_main_pct_bid2c', 'T_open_main_pct_ask2c',
    'T_open_main_pct_bidask', 'T_open_pct', 'T_open_amt', 'T_auc1_pct', 'T_auc2_pct', 'T_auc1_climitup', 'T_auc1_climitdown',
    'T_auc1_limitup', 'T_auc1_limitdown', 'T_auc2_climitup', 'T_auc2_climitdown', 'T_auc2_limitup', 'T_auc2_limitdown',
    'T_auc_climitup', 'T_auc_climitdown', 'T_auc_limitup', 'T_auc_limitdown', 'T_auc1_upnum', 'T_auc1_downnum',
    'T_auc1_updownnum', 'T_auc2_upnum', 'T_auc2_downnum', 'T_auc2_updownnum', 'T_auc_upnum', 'T_auc_downnum', 'T_auc_updownnum'
]
data = np.r_[tuple(load_auction_factor_1d(x) for x in date_list)] # (6996067, 70)
data = pd.DataFrame(data, columns=columns)
invalid = data.query('date == 0') # 400893 5.73%
data = data.query('date > 0')
pd.to_pickle(data, f'{root_path}/data.pkl')

data = pd.read_pickle(f'{root_path}/data.pkl')
describe = data.describe(percentiles=[0.005, 0.01, 0.02, 0.05, 0.25, 0.5, 0.75, 0.95, 0.98, 0.99, 0.995]).T
kurt = data.kurt()
skew = data.skew()
describe.insert(3, 'skew', skew)
describe.insert(4, 'kurt', kurt)
describe.to_excel(f'{root_path}/data_describe.xlsx')
send_file('015836', f'{root_path}/data_describe.xlsx')

delay_sec22 = data[data['T_open_main_bidivask'].notnull() & data['T_tender_bid_ff_rate'].notnull() &
                   data['delay_sec'].notnull() & data['T_open_ask_amt'].isnull()]