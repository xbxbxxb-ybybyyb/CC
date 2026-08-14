# coding: utf-8
# Author：fengchi863
# Date ：2021/4/1 10:18

from LimitUpPredStrategy.backtest.strategy_backtest.StrategyTest import StrategyTest
import pandas as pd
from LimitUpPredStrategy.conf.path_conf import pred_output_path, bt_output_path, \
    strategy_pool_file_path, filterd_tick_pool_file_path
from ShortTermTrading.Util.tools import get_curr_datetime, get_today_date

# 加入时间戳
date = get_today_date()
datetime = get_curr_datetime()
full_datetime = date * 1000000 + datetime

def get_stock_pool(pool_type=None, key='low_board'):
    if pool_type == 'all':
        pred = pd.read_pickle(filterd_tick_pool_file_path)
        pred = pred.set_index(['date', 'code', 'tick'])
    else:
        pred = pd.read_hdf(strategy_pool_file_path, key=key)
    pred.index.names = ['date', 'stk_id', 'time']
    pred.columns = ['pred']
    return pred
'''
all_board = pd.read_pickle(filterd_tick_pool_file_path)

pred = get_stock_pool(key='all_strategy_board')

pred_file_name = 'all_strategy_signal.pkl'
output_file_name = 'all_strategy_bt_result_%d.xlsx' % full_datetime

# 使用模型结果
# pred = pd.read_pickle(pred_output_path + pred_file_name)['y_pred']

self = StrategyTest(start_date=20200101, end_date=20201231, buy_money=3000000, buy_weight=0.1)
self.get_strategy_result(pred, N=30)  # 卖出周期为N分钟
result = self.statistic_factor(save_path=bt_output_path + output_file_name)
'''
#### 全量测试所有库 ####
stock_pool_list = [
    # 'all', #
    # 'low_board', # 低位板
    # 'dragon_board', # 龙头板
    # 'compensate_board', # 补涨板
    'virga2consis_board', # 分歧转一致板
    # 'all_strategy_board' # 细分策略集合板
]
for stock_pool in stock_pool_list:
    if stock_pool == 'all':
        pred = get_stock_pool(pool_type='all')
        output_file_name = 'all_board_bt_result_%d.xlsx' % full_datetime
    else:
        pred = get_stock_pool(key=stock_pool)
        output_file_name = '%s_bt_result_%d.xlsx' % (stock_pool, full_datetime)

    # self = StrategyTest(start_date=20150407, end_date=20191231, buy_money=3000000, buy_weight=0.1)
    # self = StrategyTest(start_date=20140722, end_date=20150612, buy_money=3000000, buy_weight=0.1)
    self = StrategyTest(start_date=20200101, end_date=20201231, buy_money=3000000, buy_weight=0.1)
    self.get_strategy_result(pred, N=30, cost=0.001)  # 卖出周期为N分钟
    result = self.statistic_factor(save_path=bt_output_path + '20210510牛市测试/' +  output_file_name)
    print('%s已完成' % stock_pool)