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
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211222刻画10日均线选股及买卖点测试')

from ShortTermTrading.dataApi.stockList import trans_windcode2int
from ShortTermTrading.dataApi.getData import get_daily_1factor
from ShortTermTrading.Util.tools import save_pickle
from ShortTermTrading.conf.path_conf import junk_path, faamonitor_path
from ShortTermTrading.Util.System import check_shape
import pandas as pd
import numpy as np
from DailyTrendStockBase import DailyTrendStockBase


class DailyTrendStock(DailyTrendStockBase):
    def __init__(self, start_date=20200101, end_date=20201231):
        super().__init__(start_date, end_date)

    # 流通市值条件
    def mkt_cap_cond(self, cap=80):
        stk_daily_mkt_cap = get_daily_1factor('float_a_shares', code_list=self.stk_list, date_list=self.cal_date_list)
        stk_daily_close = get_daily_1factor('close', code_list=self.stk_list, date_list=self.cal_date_list)
        stk_daily_float_cap = stk_daily_mkt_cap * stk_daily_close
        stk_daily_float_cap = stk_daily_float_cap / 10000
        stk_daily_float_cap_cond = stk_daily_float_cap >= cap
        return stk_daily_float_cap_cond

    # 多头排列条件
    def multi_arrange_cond(self):
        data = pd.read_pickle(faamonitor_path + '中期趋势股20211201.pkl')
        data.columns = list(map(trans_windcode2int, data.columns.tolist()))
        data.index = list(map(int, data.index.tolist()))
        data = data.reindex(columns=self.stk_list, index=self.cal_date_list).fillna(False)
        return data

    def ma5_cond(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        cond = self.daily_close_badj > ma5
        cond = cond.rolling(5).sum()
        cond = cond >= 3
        return cond

    def t5_cond(self):
        low_t1 = self.daily_low_badj.rolling(5).min()
        close_low_t1 = self.daily_close_badj / low_t1 - 1
        close_low_cond = close_low_t1 <= 0.15
        return close_low_cond

    def quit_cond(self):
        ma10 = self.daily_close_badj.rolling(10).mean()
        tmp = self.daily_close_badj < ma10
        tmp = tmp.rolling(2).sum() == 2
        tmp = ~tmp
        return tmp

    def concat_cond(self, *cond_args, **cond_kargs):
        st_cond = self.st_cond()
        mkt_cap_cond = self.mkt_cap_cond(cap=200)
        ma5_cond = self.ma5_cond()
        t5_cond = self.t5_cond()
        multi_arrange_cond = self.multi_arrange_cond()
        check_shape(st_cond, mkt_cap_cond, ma5_cond, multi_arrange_cond, t5_cond)
        daily_cond = st_cond & mkt_cap_cond & ma5_cond & multi_arrange_cond & t5_cond

        quit_cond = self.quit_cond()
        quit_arr = quit_cond.values.astype(int)
        quit_arr = daily_cond.values.astype(int) - quit_arr
        quit_arr = np.where(quit_arr == 0, np.nan, quit_arr)
        quit_arr[quit_arr == 0] = np.nan
        quit_cond = pd.DataFrame(quit_arr, index=quit_cond.index, columns=quit_cond.columns)
        quit_cond = quit_cond.fillna(method='ffill')
        quit_cond[quit_cond == -1] = 0

        daily_cond = daily_cond.fillna(False)
        daily_cond = daily_cond.shift(1).loc[self.date_list]
        return daily_cond

    def calc_daily_stock(self, *cond_args, **cond_kargs):
        return self.concat_cond(*cond_args, **cond_kargs)


if __name__ == '__main__':
    dts = DailyTrendStock(20210101, 20211220)
    res = dts.calc_daily_stock()
    save_pickle(res, junk_path, 'trend_daily_stock_ma10_20211222.pkl')

    # check = res.stack()[res.stack()]
