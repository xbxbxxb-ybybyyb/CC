# coding: utf-8
# Author：fengchi863
# Date ：2021/1/27 10:47
'''
20210127之后的第二个版本
抱团趋势股的参与方式
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_windcode2int
from ShortTermTrading.dataApi.tradeDate import get_date_range
from ShortTermTrading.dataApi.getData import get_daily_1factor
from ShortTermTrading.conf.path_conf import faamonitor_path, man_made_concept_data_path, daily_monitor_path
from ShortTermTrading.Util.System import fetch_man_made_monitor_list
from ShortTermTrading.Util.tools import *
from FaaMonitor.Util.DtUtil import DtUtil
# import talib
import time

class TrendStock:

    def __init__(self, start_date=20200101, end_date=20201231):
        shift_start_date = get_pre_trade_date(start_date, 5)
        shift_end_date = get_pre_trade_date(end_date, 5)
        date_list = get_date_range(shift_start_date, end_date)
        daily_st = clean_stock_list(no_pause=False, no_ST=True, least_live_days=0, start_date=shift_start_date, end_date=end_date)
        stk_list = sorted(daily_st.columns.tolist())

        daily_close_badj = get_daily_1factor('close_badj', code_list=stk_list, date_list=date_list)
        daily_pre_close_badj = get_daily_1factor('pre_close_badj', code_list=stk_list, date_list=date_list)
        daily_high_badj = get_daily_1factor('high_badj', code_list=stk_list, date_list=date_list)
        daily_low_badj = get_daily_1factor('low_badj', code_list=stk_list, date_list=date_list)
        daily_open_badj = get_daily_1factor('open_badj', code_list=stk_list, date_list=date_list)
        daily_pctchg = get_daily_1factor('pct_chg', code_list=stk_list, date_list=date_list)
        daily_amt = get_daily_1factor('amt', code_list=stk_list, date_list=date_list)

        self.date_list = date_list
        self.shift_start_date = shift_start_date
        self.shift_end_date = shift_end_date
        self.start_date = start_date
        self.end_date = end_date
        self.stk_list = stk_list
        self.daily_st = daily_st
        self.daily_close_badj = daily_close_badj
        self.daily_pre_close_badj = daily_pre_close_badj
        self.daily_high_badj = daily_high_badj
        self.daily_low_badj = daily_low_badj
        self.daily_open_badj = daily_open_badj
        self.daily_pctchg = daily_pctchg
        self.daily_amt = daily_amt

        self.stk_code_name_dict = get_stock_name_dict()
        self.daily_stock = None

    # 日间条件
    def add_st_cond(self):
        return self.daily_st

    # 流通市值条件
    def add_mkt_cap_cond(self, cap=80):
        stk_daily_mkt_cap = get_daily_1factor('float_a_shares', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_close = get_daily_1factor('close', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_float_cap = stk_daily_mkt_cap * stk_daily_close
        stk_daily_float_cap = stk_daily_float_cap / 10000
        stk_daily_float_cap_cond = stk_daily_float_cap >= cap
        return stk_daily_float_cap_cond

    # 前5(不含T日)涨跌幅<=15%
    def add_t5_cond(self):
        pctchg_5d = self.daily_close_badj.pct_change(5).shift(1)
        cond = pctchg_5d <= 0.15
        return cond

    # 前2日价格一直在5日均线上方
    def add_ma_cond(self, d_num=2):
        close_rolling_mean = self.daily_close_badj.rolling(5).mean()
        daily_ma_cond = self.daily_close_badj > close_rolling_mean
        daily_ma_cond = daily_ma_cond.rolling(d_num).sum() == d_num
        return daily_ma_cond

    def add2_t1_cond(self, shift_num=0):
        pctchg_cond = self.daily_pctchg > 4
        if shift_num == 0:
            return pctchg_cond
        else:
            return pctchg_cond.shift(shift_num)

    def inter_cond2(self):
        cond1 = self.add_ma_cond(d_num=1) & self.add2_t1_cond(shift_num=0)
        cond2 = self.add_ma_cond(d_num=2) & self.add2_t1_cond(shift_num=1)
        cond3 = self.add_ma_cond(d_num=3) & self.add2_t1_cond(shift_num=2)
        return cond1 | cond2 | cond3

    def inter_ma(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        ma20 = self.daily_close_badj.rolling(20).mean()
        ma60 = self.daily_close_badj.rolling(60).mean()
        res = (ma5 > ma20) & (ma20 > ma60)
        return res

    # 前5日涨跌幅<=15%，剔除在一波上涨的高位触发信号
    def add2_t5_cond(self):
        low_t1 = self.daily_low_badj.rolling(5).min().shift(1)
        close_low_t1 = self.daily_close_badj.shift(1) / low_t1 - 1
        close_low_cond = close_low_t1 <= 0.15
        return close_low_cond

    @staticmethod
    def get_stock_concept(stk_code, concept_df: pd.DataFrame):
        concept_list = concept_df[concept_df['股票代码'] == stockList.trans_int2windcode(stk_code)]['主题'].tolist()
        return ','.join(concept_list)

    def calc_daily_stock(self):
        st_cond = self.add_st_cond()
        mkt_cap_cond = self.add_mkt_cap_cond()
        t1_cond = self.inter_cond2()
        t5_cond = self.add2_t5_cond()
        ma_cond = self.inter_ma()
        daily_cond = st_cond & mkt_cap_cond & t5_cond & ma_cond
        daily_cond = daily_cond.rolling(3).sum() > 0
        daily_cond = daily_cond & t1_cond
        daily_cond = daily_cond.fillna(False)
        daily_cond_list = daily_cond.iloc[-1][daily_cond.iloc[-1]].index.tolist()
        self.daily_stock = daily_cond_list

    def add2excel(self, df):
        self.calc_daily_stock()
        df['趋势股'] = df['股票代码'].apply(lambda x:
                        '是' if stockList.trans_windcode2int(x) in self.daily_stock else '否')
        return df

if __name__ == '__main__':
    ts = TrendStock(end_date=20210609)
    ts.calc_daily_stock()