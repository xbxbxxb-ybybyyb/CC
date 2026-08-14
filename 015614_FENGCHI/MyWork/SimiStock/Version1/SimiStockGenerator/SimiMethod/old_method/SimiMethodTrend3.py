# coding: utf-8
# Author：fengchi863
# Date ：2022/3/11 17:20

import numpy as np
import pandas as pd

from SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import hedge_path
from dataApi import getData, tradeDate
from itertools import product


class SimiMethodTrend3(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252):
        super().__init__(start_date, end_date, concept=concept)
        shift_start_date = tradeDate.get_pre_trade_date(start_date, pre_days_num)
        shift_end_date = end_date
        close = getData.get_minute_1factor('close_5m',
                                           start_datetime=shift_start_date,
                                           end_datetime=shift_end_date,
                                           minute_interval=5)

        self.method_name = '5分钟close相关性'
        self.close = close
        self.pre_days_num = pre_days_num

    def simi_strategy(self, stk_id, trade_date, concept_list):
        res_dict = dict()

        start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
        end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        date_list = tradeDate.get_date_range(start_date, end_date)

        if stk_id in self.close.columns.tolist():
            close = self.close[stk_id].loc[(start_date, 925):(end_date, 1500)].values
        else:
            return list(), list(), list()

        for stk_id in concept_list:
            if stk_id not in self.close.columns:
                continue
            try:
                compare = self.close[stk_id].loc[(start_date, 925):(end_date, 1500)].values
            except:
                print(1)
            if np.isfinite(compare).sum() == 0:
                continue
            corr = np.corrcoef(close, compare)[0, 1]
            res_dict[stk_id] = corr
        corr = pd.Series(res_dict)
        corr = corr.sort_values(ascending=False).dropna()
        # return corr.index.tolist(), [np.nan] * len(corr)
        return corr.index.tolist(), [1] * len(corr.index), corr.values.tolist()


if __name__ == '__main__':
    param_dict = {'concept': ['SW1', 'SW2', 'SW3', 'allMarket'],
                  'pre_days_num': [60, 120]}
    param_list = list(product(param_dict['concept'], param_dict['pre_days_num']))
    for param in param_list:
        concept = param[0]
        pre_days_num = param[1]
        smt1 = SimiMethodTrend3(start_date=20180101, end_date=20200631, concept=concept, pre_days_num=pre_days_num)
        result = smt1.get_hedge_list(kernal_num=20, mode='multi')
        save_name = f'{smt1.method_name}_{concept}_{pre_days_num}_result.pkl'
        util.save_list2pkl(result, hedge_path, save_name)
