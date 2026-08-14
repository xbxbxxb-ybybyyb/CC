# coding: utf-8
# Author：fengchi863
# Date ：2022/3/11 14:31

from SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from SimiStock.dataApi import getData, tradeDate
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import hedge_path
import numpy as np
import pandas as pd
from itertools import product


class SimiMethodTrend1(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252):
        super().__init__(start_date, end_date, concept=concept)
        close_badj = getData.get_daily_1factor('close_badj', date_list=self.shift_date_list)

        self.method_name = '日频close相关性'
        self.close_badj = close_badj
        self.pre_days_num = pre_days_num

    def simi_strategy(self, stk_id, trade_date, concept_list):
        res_dict = dict()

        start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
        end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        date_list = tradeDate.get_date_range(start_date, end_date)

        close = self.close_badj[stk_id][date_list].values

        for stk_id in concept_list:
            compare = self.close_badj[stk_id][date_list].values
            if np.isfinite(compare).sum() == 0:
                continue
            corr = np.corrcoef(close, compare)[0, 1]
            res_dict[stk_id] = corr
        corr = pd.Series(res_dict)
        corr = corr.sort_values(ascending=False).dropna()
        # return corr.index.tolist(), [np.nan] * len(corr)
        return corr.index.tolist(), [1] * len(corr), corr.values.tolist()


if __name__ == '__main__':
    param_dict = {'concept': ['SW1', 'SW2', 'SW3', 'all_market'],
                  'pre_days_num': [182, 252]}
    param_list = list(product(param_dict['concept'], param_dict['pre_days_num']))
    for param in param_list:
        concept = param[0]
        pre_days_num = param[1]
        smt1 = SimiMethodTrend1(start_date=20180101, end_date=20210631, concept=concept, pre_days_num=pre_days_num)
        result = smt1.get_hedge_list(mode='multi')
        save_name = f'{smt1.method_name}_{concept}_{pre_days_num}_result.pkl'
        util.save_list2pkl(result, hedge_path, save_name)
