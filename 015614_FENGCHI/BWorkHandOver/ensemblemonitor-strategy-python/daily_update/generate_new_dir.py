# @Time : 2021/2/22 14:44
# @Author : Zhichen Lu
# @File : generate_new_dir.py
import os
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
import configparser
lm = link.LinkMessage()

def daily_initial_generation(T_plus_1_date,date,barly_max_buy,stk_min_amt,per_signal_ratio,order_ratio):

    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash')
    holding = pd.Series(holding)

    s = FactorData()
    close = s.get_factor_value('WIND_AShareEODPrices',factor_names=['TRADE_DT','S_DQ_CLOSE','S_INFO_WINDCODE'],S_INFO_WINDCODE=holding.index.tolist(),TRADE_DT=[str(date)])
    if len(holding)>0:
        close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
        cap = close * holding
    else:
        cap = pd.Series()

    account_cap = cash + cap.sum()
    config = configparser.ConfigParser()
    per_amt = max(account_cap * per_signal_ratio//10000*10000,10000)
    config['strategy_init'] = {
        'date': T_plus_1_date,
        'pre_date': date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': stk_min_amt,
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': -1,
        'order_ratio':order_ratio
    }
    print(dict(config['strategy_init']))

    config['account_info'] = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    if os.path.exists(init_conf_path + '%d.ini' % T_plus_1_date):
        os.remove(init_conf_path + '%d.ini' % T_plus_1_date)
    with open(init_conf_path + '%d.ini' % T_plus_1_date, 'w') as configfile:
        config.write(configfile)

from online_conf import *
local_config_path = '/data/group/800319/strategy_local_path3/'
if not os.path.exists(local_config_path):
    os.mkdir(local_config_path)

path_dict = dict(
# 当日收盘持仓信息(持仓量、第一次买入信息、可交易量)
holding_info_path = local_config_path + 'holding_info/',
# 当日收盘持仓股的买入时间
buy_time_info_path = local_config_path + 'buy_time_info/',
# 超参数(均值、标准差)，日期为T-1日，参数用于T日
hyper_param_path = local_config_path + 'factor_hyper_param/',
# T-1日计算出用于T日的股票池，名字为T-1日
code_list_path = local_config_path + 'code_list/',
# 模型配置文件，文件名为模型更新的日期
model_config_path = local_config_path + 'model_conf/',
model_path = local_config_path + 'model/',

# 每天策略初始化参数路径
init_conf_path = local_config_path + 'daily_init_config/',
# 每天输出路径
daily_out_path = local_config_path + 'daily_output/',
# 每天输出路径
daily_out_path_offline = local_config_path + 'daily_output_offline/',
vol_info_path = local_config_path + 'vol_info/',
restrict_list_path = local_config_path + 'restrict_list/',
factor_list_path = f'{local_config_path}factor_list/',
)
for each in path_dict:
    if not os.path.exists(path_dict[each]):
        os.mkdir(path_dict[each])

import pandas as pd



pre_date = 20210402
initial_day = 20210406
initial_cash = 2000000

pd.to_pickle({'cash':initial_cash},path_dict['holding_info_path']+'%d.pkl'%pre_date)
pd.to_pickle({},path_dict['buy_time_info_path']+'%d.pkl'%pre_date)
daily_initial_generation(T_plus_1_date=initial_day,date=pre_date,barly_max_buy=100,stk_min_amt=int(min(initial_cash*0.001,200000)),per_signal_ratio=0.005,order_ratio=0.1)
