# coding: utf-8
# Author：fengchi863
# Date ：2021/10/26 16:15

'''
20211215:
修改中期趋势股处的参数
'''

import os, sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件')

from ShortTermTrading.dataApi.stockList import trans_windcode2int
from ShortTermTrading.dataApi.getData import get_daily_1factor
from ShortTermTrading.Util.tools import save_pickle
from ShortTermTrading.conf.path_conf import junk_path, faamonitor_path
from ShortTermTrading.Util.System import check_shape
import pandas as pd
from DailyTrendStockBase import DailyTrendStockBase


class DailyTrendStock(DailyTrendStockBase):
    def __init__(self, start_date=20200101, end_date=20201231):
        super().__init__(start_date, end_date)

    # 流通市值条件
    def mkt_cap_cond(self, cap=250):
        stk_daily_mkt_cap = get_daily_1factor('float_a_shares', code_list=self.stk_list, date_list=self.cal_date_list)
        stk_daily_close = get_daily_1factor('close', code_list=self.stk_list, date_list=self.cal_date_list)
        stk_daily_float_cap = stk_daily_mkt_cap * stk_daily_close
        stk_daily_float_cap = stk_daily_float_cap / 10000
        stk_daily_float_cap_cond = stk_daily_float_cap >= cap
        return stk_daily_float_cap_cond

    def t1_cond(self):
        pctchg_cond = self.daily_pctchg > 7
        return pctchg_cond

    def t5_cond(self):
        low_t1 = self.daily_low_badj.rolling(5).min().shift(1)
        close_low_t1 = self.daily_close_badj.shift(1) / low_t1 - 1
        close_low_cond = close_low_t1 <= 0.15
        return close_low_cond

    # 多头排列条件
    def multi_arrange_cond(self):
        data = pd.read_pickle(faamonitor_path + '中期趋势股20211201.pkl')
        data.columns = list(map(trans_windcode2int, data.columns.tolist()))
        data.index = list(map(int, data.index.tolist()))
        data = data.reindex(columns=self.stk_list, index=self.cal_date_list).fillna(False)
        return data

    def concat_cond(self, *cond_args, **cond_kargs):
        st_cond = self.st_cond()
        mkt_cap_cond = self.mkt_cap_cond(cap=200)
        t1_cond = self.t1_cond()
        t5_cond = self.t5_cond()
        multi_arrange_cond = self.multi_arrange_cond()
        check_shape(st_cond, mkt_cap_cond, t1_cond, multi_arrange_cond, t5_cond)
        daily_cond = st_cond & mkt_cap_cond & t1_cond & multi_arrange_cond & t5_cond
        daily_cond = daily_cond.rolling(3).sum() > 0
        daily_cond = daily_cond.fillna(False)
        daily_cond = daily_cond.shift(1).loc[self.date_list]
        return daily_cond

    def calc_daily_stock(self, *cond_args, **cond_kargs):
        return self.concat_cond(*cond_args, **cond_kargs)


if __name__ == '__main__':
    dts = DailyTrendStock(20210101, 20211201)
    res = dts.calc_daily_stock()
    save_pickle(res, junk_path, 'trend_daily_stock_20211215_oldVersion.pkl')
