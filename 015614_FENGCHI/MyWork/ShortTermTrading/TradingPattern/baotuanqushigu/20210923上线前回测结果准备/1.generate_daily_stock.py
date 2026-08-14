# coding: utf-8
# Author：fengchi863
# Date ：2021/9/8 20:53

'''
继承了sub_strategy2.py
用于生成股票池并回测，选定在特定行业上的结果，于上线前的趋势股回测
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_windcode2int
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import get_stock_name_dict, save_xlsx, get_df_sum, save_pickle
from ShortTermTrading.conf.path_conf import qushigu_data_path, junk_path, faamonitor_path
from ShortTermTrading.Util.System import get_minutely_df_true, get_daily_df_true, check_shape, add_stock_name
from ShortTermTrading.Util.System import check_shape, add_stock_name, fetch_man_made_monitor_list
import pandas as pd, numpy as np
from xquant.factordata import FactorData
from tqdm import tqdm
import talib
import time
from multiprocessing import Pool


class SignalGenerator:

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

        intra_minute_amt = get_minute_1factor('amt', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_close_badj = get_minute_1factor('close_badj', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_close_nbadj = get_minute_1factor('close', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)

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

        self.intra_minute_amt = intra_minute_amt
        self.intra_minute_close_badj = intra_minute_close_badj
        self.intra_minute_close_nbadj = intra_minute_close_nbadj

        self.stk_code_name_dict = get_stock_name_dict()

    # 指数条件
    def add_index_cond(self):
        s = FactorData()
        index_data = s.get_factor_value(
            "WIND_AIndexEODPrices",
            s_info_windcode=['399005.SZ', '399001.SZ', '000001.SH'],
            factors=['s_info_windcode', 'trade_dt', 's_dq_close', 's_dq_open', 's_dq_amount'],
            trade_dt=self.date_list
        )
        date_list_str = list(map(str, self.date_list))
        index_close = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE').loc[date_list_str]
        index_close.index = index_close.index.map(int)
        index_open = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_OPEN').loc[date_list_str]
        index_open.index = index_open.index.map(int)
        index_ma5 = index_close.rolling(5).mean() < index_close
        ma5_sum = index_ma5.sum(axis=1)

        a1, a2, a3 = talib.MACD(np.array(index_close['000001.SH']), fastperiod=12, slowperiod=26, signalperiod=9)
        macd = pd.Series(a3, index=self.date_list)

        return (ma5_sum.shift(1) >= 2) & (macd.shift(1) > macd.shift(2))

    # 日间条件
    def add_st_cond(self):
        return self.daily_st

    # 流通市值条件
    def add_mkt_cap_cond(self, cap=250):
        stk_daily_mkt_cap = get_daily_1factor('float_a_shares', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_close = get_daily_1factor('close', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_float_cap = stk_daily_mkt_cap * stk_daily_close
        stk_daily_float_cap = stk_daily_float_cap / 10000
        stk_daily_float_cap_cond = stk_daily_float_cap >= cap
        return stk_daily_float_cap_cond.shift(1)

    # 涨跌幅条件
    def add_t1_cond(self, d_num=3, pct_threshold1=0.06, pct_threshold2=0.03):
        pctchg1 = self.daily_close_badj.pct_change(d_num)
        pctchg_cond1 = pctchg1 >= pct_threshold1
        pctchg2 = self.daily_pctchg > pct_threshold2
        pctchg_cond2 = pctchg2.rolling(d_num).sum() >= 2
        return (pctchg_cond1 & pctchg_cond2).shift(1)

    # 前5(不含近3日)涨跌幅<=15%
    def add_t5_cond(self):
        low_t5 = self.daily_low_badj.rolling(5).min().shift(3)
        close_low_t5 = self.daily_close_badj.shift(3) / low_t5 - 1
        close_low_cond = close_low_t5 <= 0.15
        return close_low_cond.shift(1)

    # 多头排列条件
    def add_multi_arrange_cond(self):
        data = pd.read_pickle(faamonitor_path + '中期趋势股20211207.pkl')
        data.columns = list(map(trans_windcode2int, data.columns.tolist()))
        data.index = list(map(int, data.index.tolist()))
        data = data.reindex(columns=self.stk_list, index=self.date_list).fillna(False)
        return data.shift(1).loc[self.shift_start_date:self.end_date]

    # 前2日价格一直在5日均线上方
    def add_ma_cond(self, d_num=2):
        close_rolling_mean = self.daily_close_badj.rolling(5).mean()
        daily_ma_cond = self.daily_close_badj > close_rolling_mean
        daily_ma_cond = daily_ma_cond.rolling(d_num).sum() == d_num
        return daily_ma_cond.shift(1)

    def inter_ma(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        ma20 = self.daily_close_badj.rolling(20).mean()
        ma60 = self.daily_close_badj.rolling(60).mean()
        res = (ma5 > ma20) & (ma20 > ma60)
        return res.shift(1)

    # 最近3日平均成交额排名市场前150
    def add_amt_rank_cond(self, d_num=3, rank_num=150):
        amt_rolling_mean = self.daily_amt.rolling(d_num).mean()
        daily_amt_cond = amt_rolling_mean.rank(ascending=False, axis=1) < rank_num
        return daily_amt_cond.shift(1)

    # 第二种筛选方式
    def add2_t1_cond(self):
        pctchg_cond = self.daily_pctchg > 7
        return pctchg_cond.shift(1)

    # 前2日价格一直在5日均线上方
    def add_ma_cond_v3(self, d_num=2):
        close_rolling_mean = self.daily_close_badj.rolling(5).mean()
        daily_ma_cond = self.daily_close_badj > close_rolling_mean
        daily_ma_cond = daily_ma_cond.rolling(d_num).sum() == d_num
        return daily_ma_cond

    def add2_t1_cond_v3(self, shift_num=0):
        pctchg_cond = self.daily_pctchg > 4
        if shift_num == 0:
            return pctchg_cond
        else:
            return pctchg_cond.shift(shift_num)

    def inter_cond2_v3(self):
        cond1 = self.add_ma_cond_v3(d_num=1) & self.add2_t1_cond_v3(shift_num=0)
        cond2 = self.add_ma_cond_v3(d_num=2) & self.add2_t1_cond_v3(shift_num=1)
        cond3 = self.add_ma_cond_v3(d_num=3) & self.add2_t1_cond_v3(shift_num=2)
        return (cond1 | cond2 | cond3).shift(1)

    # 前5日涨跌幅<=15%，剔除在一波上涨的高位触发信号
    def add2_t5_cond(self):
        low_t1 = self.daily_low_badj.rolling(5).min().shift(1)
        close_low_t1 = self.daily_close_badj.shift(1) / low_t1 - 1
        close_low_cond = close_low_t1 <= 0.15
        return close_low_cond.shift(1)

    def calc_daily_stock_v2(self):
        # index_cond = self.add_index_cond()  # 使用大盘择时条件
        st_cond = self.add_st_cond()
        mkt_cap_cond = self.add_mkt_cap_cond(cap=200)
        t1_cond = self.add2_t1_cond()
        t5_cond = self.add2_t5_cond()
        multi_arrange_cond = self.add_multi_arrange_cond()
        check_shape(st_cond, mkt_cap_cond, t1_cond, multi_arrange_cond, t5_cond)
        daily_cond = st_cond & mkt_cap_cond & t1_cond & multi_arrange_cond & t5_cond
        daily_cond = daily_cond.rolling(3).sum() > 0
        # daily_cond = daily_cond & index_cond.values[:, None]
        daily_cond1 = daily_cond.fillna(False)
        return daily_cond

    # def calc_daily_stock_v3(self):
    #     st_cond = self.add_st_cond()
    #     # index_cond = self.add_index_cond()  # 使用大盘择时条件
    #     mkt_cap_cond = self.add_mkt_cap_cond(cap=250)
    #     ma_cond = self.inter_ma()
    #     inter_cond2 = self.inter_cond2_v3()
    #     t5_cond = self.add2_t5_cond()
    #     check_shape(st_cond, mkt_cap_cond, ma_cond, inter_cond2, t5_cond)
    #     daily_cond = st_cond & mkt_cap_cond & ma_cond & inter_cond2 & t5_cond
    #     # daily_cond = daily_cond & index_cond.values[:, None]
    #     daily_cond = daily_cond.fillna(False)
    #     return daily_cond

    def calc_intra_judge(self):
        intra_judge = self.add_minutely_low_judge(kind='all')
        return intra_judge.fillna(False)


def wrapper(start_date, end_date):
    print('start', start_date, end_date)
    sg = SignalGenerator(start_date=start_date, end_date=end_date)
    print('初始化完成')
    daily_cond = sg.calc_daily_stock_v2()

    monitor_list = fetch_man_made_monitor_list()
    monitor_list = list(set(monitor_list).intersection(set(daily_cond.columns.tolist())))
    daily_cond = daily_cond[monitor_list]
    return daily_cond


if __name__ == '__main__':
    # start_date = 20210501
    start_date = 20210101
    end_date = 20211201
    res = wrapper(start_date, end_date)
    # save_pickle(res, junk_path, 'trend_daily_stock_20210923.pkl')
    save_pickle(res, junk_path, 'trend_daily_stock_20211216test.pkl')

# from ShortTermTrading.conf.path_conf import qushigu_data_path, junk_path
# import pandas as pd
# check1 = pd.read_pickle(junk_path + 'trend_daily_stock_20211216test.pkl')
# check2 = pd.read_pickle(junk_path + 'trend_daily_stock_20211215_oldVersion.pkl')
# check11 = check1.stack()[check1.stack()]
# check22 = check2.stack()[check2.stack()]
# check1.shape
# check2.shape