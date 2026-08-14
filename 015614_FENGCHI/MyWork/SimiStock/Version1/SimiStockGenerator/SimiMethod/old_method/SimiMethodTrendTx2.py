# coding: utf-8
# Author：fengchi863
# Date ：2022/3/11 14:31

"""
给陶鑫生成的版本，版本2
"""

from SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from SimiStock.dataApi import getData, tradeDate
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import hedge_path
import numpy as np
import pandas as pd
from itertools import product


class SimiMethodTrend_bata(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252, hedge_max_num=12,
                 corr_threshold=0.8):
        super().__init__(start_date, end_date, concept=concept)
        pct_chg = getData.get_daily_1factor('pct_chg', date_list=self.shift_date_list)

        self.method_name = '日频pctchg相关性'
        self.pct_chg = pct_chg
        self.pre_days_num = pre_days_num

        self.hedge_max_num = hedge_max_num
        self.corr_threshold = corr_threshold

    def simi_strategy(self, stk_id, trade_date, concept_list):
        res_dict = dict()

        start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
        end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        date_list = tradeDate.get_date_range(start_date, end_date)

        pct_chg = self.pct_chg[stk_id][date_list].values

        for stk_id in concept_list:
            compare = self.pct_chg[stk_id][date_list].values
            if np.isfinite(compare).sum() == 0:
                continue
            corr = np.corrcoef(pct_chg, compare)[0, 1]
            res_dict[stk_id] = corr
        corr = pd.Series(res_dict)
        corr = corr.sort_values(ascending=False).dropna()
        if len(corr) > self.hedge_max_num:
            corr = corr[:self.hedge_max_num]
        corr = corr[corr > self.corr_threshold]
        # return corr.index.tolist(), [np.nan] * len(corr)
        return corr.index.tolist(), [1] * len(corr), corr.values.tolist()


if __name__ == '__main__':
    # param_dict = {'method_name': ['日频pctchg相关性'],
    #               'concept': ['SW1'],
    #               'pre_days_num': [120],
    #               'hedge_max_num': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    #               'corr_threshold': [0.8, 0.75, 0.7, 0.65, 0.6, 0.55]}
    param_dict = {'method_name': ['日频pctchg相关性'],
                  'concept': ['SW1'],
                  'pre_days_num': [120],
                  'hedge_max_num': [14],
                  'corr_threshold': [0.7]}
    param_list = list(product(param_dict['method_name'],
                              param_dict['concept'],
                              param_dict['pre_days_num'],
                              param_dict['hedge_max_num'],
                              param_dict['corr_threshold']))
    for param in param_list:
        method_name = param[0]
        concept = param[1]
        pre_days_num = param[2]
        hedge_max_num = param[3]
        corr_threshold = param[4]
        smt1 = SimiMethodTrend_bata(start_date=20180101, end_date=20200631, concept=concept, pre_days_num=pre_days_num,
                                    hedge_max_num=hedge_max_num, corr_threshold=corr_threshold)
        result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        save_name = f'{smt1.method_name}_{concept}_{pre_days_num}_{hedge_max_num}_{corr_threshold}_result.pkl'
        util.save_list2pkl(result, hedge_path, save_name)