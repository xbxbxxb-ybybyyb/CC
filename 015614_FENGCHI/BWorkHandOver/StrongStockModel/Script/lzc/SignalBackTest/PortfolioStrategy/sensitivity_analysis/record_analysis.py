# @Time : 2020/11/13 15:00
# @Author : Zhichen Lu
# @File : record_analysis.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
import pandas as pd
import os
import numpy as np
from xquant.compute.aimr import AIMR

para_list = []
deal_price_para_list = ['vwap_%dmin' % window for window in [10]]#['twap_%dmin' % window for window in [5, 20, 30]] + ['vwap_%dmin' % window for window in [5, 10, 20, 30]]
for deal_price_path in deal_price_para_list:
    for sample in ['in','out']:
        for cost_rate in [10,12,14,16,18]:
            para_list.append(('%s_record_%ssample_lr_XGB_NN.pkl'%(deal_price_path,sample),cost_rate))
def main():
    record_filename, cost = para_list[idx]
    if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/'+record_filename.replace('record','%dbp_cost'%cost).replace('.pkl','.xlsx')):
        print('exist')
        return
    print(record_filename, cost)
    record = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/record/%s'%record_filename)
    helper = EvaluationHelper(buy_cost_ratio=cost*0.0001, sell_cost_ratio=cost*0.0001)
    helper.one_wave_run(record, kernel=24, output_path='/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/'+record_filename.replace('record','%dbp_cost'%cost).replace('.pkl','.xlsx'),
                        signal_record_save=True)

idx = int(AIMR.getParam())
main()


