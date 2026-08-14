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


class SimiMethodTrend2(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252):
        super().__init__(start_date, end_date, concept=concept)
        pctchg = getData.get_daily_1factor('pct_chg', date_list=self.shift_date_list)

        self.method_name = '日频pctchg相关性'
        self.pctchg = pctchg
        self.pre_days_num = pre_days_num

    def simi_strategy(self, stk_id, trade_date, concept_list):
        res_dict = dict()

        start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
        end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        date_list = tradeDate.get_date_range(start_date, end_date)

        close = self.pctchg[stk_id][date_list].values

        ascend_flag = False
        for stk_id in concept_list:
            compare = self.pctchg[stk_id][date_list].values
            if np.isfinite(compare).sum() == 0:
                continue
            corr, ascend_flag = self.corr(close, compare, method='日频pctchg皮尔逊相关性')
            res_dict[stk_id] = corr
        corr = pd.Series(res_dict)
        corr = corr.sort_values(ascending=ascend_flag).dropna()
        # return corr.index.tolist(), [np.nan] * len(corr)
        return corr.index.tolist(), [1] * len(corr), corr.values.tolist()

    @staticmethod
    def corr(arr1, arr2, method=None):
        if method == '日频pctchg皮尔逊相关性':
            return np.corrcoef(arr1, arr2)[0, 1], False
        elif method == '日频pctchg欧式相关性':
            return np.linalg.norm(arr1 - arr2, ord=2), True
        elif method == '日频pctchg曼哈顿相关性':
            return np.linalg.norm(arr1 - arr2, ord=1), True
        elif method == '日频pctchg生物距离':
            up = np.sum(np.abs(arr1 - arr2))
            down = np.sum(arr1) + np.sum(arr2)
            down = 1e-5 if down == 0 else down
            return up / down


if __name__ == '__main__':
    param_dict = {'concept': ['SW1', 'SW2', 'SW3', 'all_market'],
                   'pre_days_num': [182, 252]}
    param_list = list(product(param_dict['concept'], param_dict['pre_days_num']))
    for param in param_list:
        concept = param[0]
        pre_days_num = param[1]
        smt1 = SimiMethodTrend2(start_date=20180101, end_date=20200631, concept=concept, pre_days_num=pre_days_num)
        result = smt1.get_hedge_list(mode='multi', kernal_num=20)
        save_name = f'{smt1.method_name}_{concept}_{pre_days_num}_result.pkl'
        util.save_list2pkl(result, hedge_path, save_name)