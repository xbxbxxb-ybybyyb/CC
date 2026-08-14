# coding: utf-8
# Author：fengchi863
# Date ：2021/6/16 9:41

# coding: utf-8
# Author：fengchi863
# Date ：2021/1/27 10:47
'''
20210127之后的第二个版本
抱团趋势股的参与方式
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_windcode2int
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import get_stock_name_dict, save_xlsx, get_df_sum
from ShortTermTrading.conf.path_conf import qushigu_data_path, junk_path
from ShortTermTrading.Util.System import get_minutely_df_true, get_daily_df_true, check_shape, add_stock_name
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
        data = pd.read_pickle(qushigu_data_path)
        data.columns = list(map(trans_windcode2int, data.columns.tolist()))
        data.index = list(map(int, data.index.tolist()))
        data = data.reindex(columns=self.stk_list).fillna(False)
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

    def add_minutely_low_judge(self, kind='ma5_boost'):
        ma5 = self.daily_close_badj.rolling(5).mean().shift(1)
        ma5_boost = ma5 * 1.02 # 上方0.2%个区间

        # 第一种，回调到ma5上区间内
        if kind == 'ma5_boost':
            expanding_low = self.intra_minute_close_badj.groupby('date').expanding().min()
            expanding_low = expanding_low.droplevel(0)
            pre_close = self.daily_pre_close_badj
            # 与昨收价比较
            expanding_low_rel_pre_close_pct = pd.DataFrame((expanding_low.values.reshape(pre_close.shape[0], 242, -1) / \
                pre_close.values[:, None, :] - 1).reshape(-1, len(self.stk_list)), index=expanding_low.index, columns=expanding_low.columns)
            # 与ma5_boost比较
            low_pct_judge = expanding_low_rel_pre_close_pct < -0.01 # 最低点相对于昨日收盘价小与-0.01
            low_judge = pd.DataFrame((expanding_low.values.reshape(ma5_boost.shape[0], 242, ma5_boost.shape[1]) < ma5_boost.values[:, None, :]).reshape(-1, len(self.stk_list)),\
                index=expanding_low.index, columns=expanding_low.columns)
            low_judge2 = pd.DataFrame((expanding_low.values.reshape(ma5_boost.shape[0], 242, ma5_boost.shape[1]) > ma5.values[:, None, :]).reshape(-1, len(self.stk_list)),\
                index=expanding_low.index, columns=expanding_low.columns)
            curr_pct_judge = (self.intra_minute_close_badj / expanding_low - 1) >= 0.01
            return low_judge & low_judge2 & low_pct_judge & curr_pct_judge
        # 第二种，回调到ma5
        if kind == 'ma5':
            expanding_low = self.intra_minute_close_badj.groupby('date').expanding().min()
            expanding_low = expanding_low.droplevel(0)
            pre_close = self.daily_pre_close_badj
            # 与昨收价比较
            expanding_low_rel_pre_close_pct = pd.DataFrame((expanding_low.values.reshape(pre_close.shape[0], 242, -1) / \
                           pre_close.values[:, None, :] - 1).reshape(-1, len(self.stk_list)), index=expanding_low.index, columns=expanding_low.columns)
            low_pct_judge = expanding_low_rel_pre_close_pct < -0.01  # 最低点相对于昨日收盘价小与-0.01

            # 与ma5比较
            low_judge = pd.DataFrame((expanding_low.values.reshape(ma5.shape[0], 242, ma5_boost.shape[1]) < ma5.values[:,None,:]).reshape(-1, len(
                self.stk_list)), index=expanding_low.index, columns=expanding_low.columns)
            curr_pct_judge = (self.intra_minute_close_badj / expanding_low - 1) >= 0.01
            curr_px_judge = pd.DataFrame((self.intra_minute_close_badj.values.reshape(ma5.shape[0], 242, ma5.shape[1]) > ma5.values[:,None,:]).reshape(-1,len(self.stk_list)), \
                          index=self.intra_minute_close_badj.index, columns=self.intra_minute_close_badj.columns)

            return low_judge & low_pct_judge & curr_pct_judge & curr_px_judge
        if kind == 'all':
            return self.add_minutely_low_judge(kind='ma5_boost') | self.add_minutely_low_judge(kind='ma5')

    def calc_daily_stock_v2(self):
        index_cond = self.add_index_cond()  # 使用大盘择时条件
        st_cond = self.add_st_cond()
        mkt_cap_cond = self.add_mkt_cap_cond()
        t1_cond = self.add2_t1_cond()
        t5_cond = self.add2_t5_cond()
        multi_arrange_cond = self.add_multi_arrange_cond()
        check_shape(st_cond, mkt_cap_cond, t1_cond, multi_arrange_cond, t5_cond)
        daily_cond = st_cond & mkt_cap_cond & t1_cond & multi_arrange_cond & t5_cond
        daily_cond = daily_cond.rolling(3).sum() > 0
        daily_cond = daily_cond & index_cond.values[:, None]
        daily_cond = daily_cond.fillna(False)
        return daily_cond

    def calc_daily_stock_v3(self):
        st_cond = self.add_st_cond()
        # index_cond = self.add_index_cond()  # 使用大盘择时条件
        mkt_cap_cond = self.add_mkt_cap_cond(cap=80)
        ma_cond = self.inter_ma()
        inter_cond2 = self.inter_cond2_v3()
        t5_cond = self.add2_t5_cond()
        check_shape(st_cond, mkt_cap_cond, ma_cond, inter_cond2, t5_cond)
        daily_cond = st_cond & mkt_cap_cond & ma_cond & inter_cond2 & t5_cond
        # daily_cond = daily_cond & index_cond.values[:, None]
        daily_cond = daily_cond.fillna(False)
        return daily_cond

    def calc_intra_judge(self):
        intra_judge = self.add_minutely_low_judge(kind='all')
        return intra_judge.fillna(False)

def wrapper(start_date, end_date):
    print('start', start_date, end_date)
    sg = SignalGenerator(start_date=start_date, end_date=end_date)
    print('初始化完成')
    daily_cond = sg.calc_daily_stock_v3()
    intra_judge = sg.calc_intra_judge()

    print('日间条件与日内条件整合')
    t1 = time.time()
    assert daily_cond.shape[1] == intra_judge.shape[1]  # 数据校验
    assert daily_cond.columns.tolist() == intra_judge.columns.tolist()
    stk_minute_point = pd.DataFrame((intra_judge.values.reshape(daily_cond.shape[0], -1, daily_cond.shape[1]) & \
                                     daily_cond.values[:, None, :]).reshape(-1, len(sg.stk_list)),
                                    index=intra_judge.index, columns=intra_judge.columns)
    stk_minute_point = stk_minute_point.dropna(how='all', axis=0)  # 买点
    stk_minute_point = stk_minute_point.loc[start_date:end_date]
    print('日间日内整合完毕，耗时%ds' % (time.time() - t1))
    return stk_minute_point

if __name__ == '__main__':
    date_list_para = [(20140101, 20151231),
                      (20160101, 20171231),
                      (20180101, 20191231),
                      (20200101, 20201231)]

    # pool = Pool(10)
    # res_dict = dict()
    # res_list = list()
    # for idx, date_para in enumerate(date_list_para):
    #     print(date_para)
    #     res_dict[idx] = pool.apply_async(wrapper, (*date_para,))
    # pool.close()
    # pool.join()
    #
    # for idx in res_dict:
    #     res_list[idx] = res_dict[idx].get()
    #
    # res = pd.concat([res_list[x] for x in res_list])
    # res = res.sort_index()
    idx = 3
    date_para = date_list_para[idx]
    res = wrapper(date_para[0], date_para[1])
    res.to_pickle(junk_path + '20210616_%d.pkl' % (idx+1))

    # minutely_true_df = get_minutely_df_true(stk_minute_point)
    # minutely_true_df = add_stock_name(minutely_true_df)
    # daily_true_df = get_daily_df_true(daily_cond)
    # daily_true_df = add_stock_name(daily_true_df)
    # save_xlsx(daily_true_df, junk_path, 'daily_true_df1.xlsx')
    # save_xlsx(minutely_true_df, junk_path, 'minutely_true_df1.xlsx')