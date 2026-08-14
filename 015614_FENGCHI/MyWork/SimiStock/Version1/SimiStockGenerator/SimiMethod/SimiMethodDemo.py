# coding: utf-8
# Author：fengchi863
# Date ：2022/3/9 8:47

from SimiStockGenerator.Version1.SimiMethodBase.SimiMethodBase import SimiMethodBase
from dataApi import getData, tradeDate
from SimiStock.Version1.SimiStockGenerator.util import util
from SimiStock.Version1.config.path_config import hedge_path
import numpy as np
import pandas as pd
import time


class SimiMethodDemo2(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1'):
        super().__init__(start_date, end_date, concept=concept)
        close_badj = getData.get_daily_1factor('close_badj', date_list=self.shift_date_list)

        self.close_badj = close_badj

    def simi_strategy(self, stk_id, trade_date, concept_list):
        res_dict = dict()

        start_date = tradeDate.get_pre_trade_date(trade_date, 120)
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
        return corr.index.tolist()[:2], [0.8, 0.2]


if __name__ == '__main__':
    smd2 = SimiMethodDemo2(start_date=20200101, end_date=20200131, concept='SW1')
    t1 = time.time()
    result = smd2.get_hedge_list(mode='multi')
    print(time.time() - t1)
    util.save_list2pkl(result, hedge_path, 'test.pkl')
