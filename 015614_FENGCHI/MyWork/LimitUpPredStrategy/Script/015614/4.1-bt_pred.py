# coding: utf-8
# Author：fengchi863
# Date ：2021/4/23 16:06

from LimitUpPredStrategy.backtest.strategy_backtest.StrategyTest1 import StrategyTest
from LimitUpPredStrategy.conf.path_conf import pred_output_path, bt_output_path
from LimitUpPredStrategy.Util.DataUtil import DataUtil
import os

file_path = pred_output_path + 'linear_reg/linear_reg_trainPeriod60_predictPeriod10_factorNum75_pctThreshold0.03_signal_r2s3.pkl'
pred = DataUtil.read_pickle(file_path)['prediction']

output_file_name = bt_output_path + os.path.split(file_path)[-1].replace('.pkl', '_bt_result.xlsx')

# 20150407
st = StrategyTest(start_date=20150101, end_date=20191231, buy_money=3000000, buy_weight=0.1, tick_delay=6)
st.get_strategy_result(pred, N=30, cost=0.001)  # 卖出周期为N分钟
result = st.statistic_factor(save_path=output_file_name)
print('回测已完成')
