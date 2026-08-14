# coding: utf-8
# Author：fengchi863
# Date ：2021/2/1 17:18

'''
1、添加了大盘择时条件
2、添加了去除部分交易的方法
3、ma5使用盘中实时ma5
4、大盘当天跌幅超过一定值不再买入
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_windcode2int
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import get_stock_name_dict, save_xlsx, del_star_stk, get_df_sum
from ShortTermTrading.conf.path_conf import qushigu_data_path, junk_path
from ShortTermTrading.Util.System import get_minutely_df_true, get_daily_df_true, check_shape, add_stock_name
import pandas as pd, numpy as np
from xquant.factordata import FactorData
from tqdm import tqdm
import time
import talib

class SignalGenerator:

    def __init__(self, start_date=20200101, end_date=20201231):
        shift_start_date = get_pre_trade_date(start_date, 45)
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
        daily_index_close = get_daily_1factor('close', code_list=['SZZZ'], date_list=date_list, type='bench')

        intra_minute_amt = get_minute_1factor('amt', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_close_badj = get_minute_1factor('close_badj', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_close_nbadj = get_minute_1factor('close', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_index_close = get_minute_1factor('close', code_list=['SZZZ'], type='bench').loc[(shift_start_date, 925):(end_date, 1500)]

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
        self.daily_index_close = daily_index_close

        self.intra_minute_amt = intra_minute_amt
        self.intra_minute_close_badj = intra_minute_close_badj
        self.intra_minute_close_nbadj = intra_minute_close_nbadj
        self.intra_minute_index_close = intra_minute_index_close

        self.stk_code_name_dict = get_stock_name_dict()

    ##################
    # 指数条件
    def add_index_cond(self):
        s = FactorData()
        index_data = s.get_factor_value(
            "WIND_AIndexEODPrices",
            s_info_windcode=['399005.SZ', '399001.SZ', '000001.SH'],
            factors=['s_info_windcode', 'trade_dt', 's_dq_close', 's_dq_open', 's_dq_amount'], trade_dt=self.date_list
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

    # 第二种剔除方案
    def add2_index_cond(self):
        ret = pd.DataFrame(True, index=self.date_list, columns=['cond'])
        apart_date_list = [20200226,20200227,20200228,20200310,20200311,20200313,20200316,
                           20200317,20200318,20200715,20200716]
        ret.loc[apart_date_list, 'cond'] = False
        return ret
    ##################

    # 日间条件
    def add_st_cond(self):
        return self.daily_st

    # 流通市值条件
    def add_mkt_cap_cond(self, cap=250):
        stk_daily_mkt_cap = get_daily_1factor('float_a_shares', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_close = get_daily_1factor('close', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_float_cap = stk_daily_mkt_cap * stk_daily_close
        stk_daily_float_cap = stk_daily_float_cap.rolling(90).mean() / 10000
        stk_daily_float_cap_cond = stk_daily_float_cap >= cap
        return stk_daily_float_cap_cond.shift(1)

    # 涨跌幅条件
    def add_t1_cond(self, d_num=3, pct_threshold1=0.06, pct_threshold2=3):
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
        # data = pd.read_pickle(qushigu_data_path)
        data = pd.read_pickle('/data/group/800319/Faamonitor/中期趋势股20210510.pkl')
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

    #########################
    # 最近3日平均成交额排名市场前150
    def add_amt_rank_cond(self, d_num=3, rank_num=150):
        amt_rolling_mean = self.daily_amt.rolling(d_num).mean()
        daily_amt_cond = amt_rolling_mean.rank(ascending=False, axis=1) < rank_num
        return daily_amt_cond.shift(1)

    # 第二种筛选方式
    def add2_t1_cond(self):
        pctchg_cond = self.daily_pctchg > 7
        ma5 = self.daily_close_badj.rolling(5).mean()
        ma5_cond = self.daily_close_badj / ma5 > 1.03
        return (pctchg_cond & ma5_cond).shift(1)
    #########################

    # 前5日涨跌幅<=15%，剔除在一波上涨的高位触发信号
    def add2_t5_cond(self):
        low_t1 = self.daily_low_badj.rolling(5).min().shift(1)
        close_low_t1 = self.daily_close_badj.shift(1) / low_t1 - 1
        close_low_cond = close_low_t1 <= 0.15
        return close_low_cond.shift(1)

    # 剔除指数条件，盘中出现过跌幅大于1%的不开仓
    def add_min_pct_judge(self):
        index_pre_close = self.daily_index_close.shift(1)
        intra_minute_index_close = self.intra_minute_index_close
        expanding_low = intra_minute_index_close.groupby('date').expanding().min()
        expanding_low_rel_pre_close_pct = pd.DataFrame((expanding_low.values.reshape(index_pre_close.shape[0], 242, -1) / \
                                     index_pre_close.values[:, None, :] - 1).reshape(-1,1),index=expanding_low.index, columns=expanding_low.columns)
        expanding_low_rel_pre_close_pct = expanding_low_rel_pre_close_pct.droplevel(0)
        return expanding_low_rel_pre_close_pct > -0.01

    def add_minutely_low_judge(self, kind='ma5_boost'):
        # 更改为使用盘中实时ma5，计算方式前面4天的收盘平均价加上盘中实时价/5
        ma4 = (self.daily_close_badj.rolling(4).sum() / 5).shift(1)
        intra_ma = self.intra_minute_close_badj / 5
        ma5 = pd.DataFrame((intra_ma.values.reshape(ma4.shape[0], 242, -1) + ma4.values[:,None,:]).reshape(-1, len(self.stk_list)), \
                           index=intra_ma.index, columns=intra_ma.columns)
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
            low_judge = expanding_low < ma5_boost
            low_judge2 = expanding_low > ma5
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
            low_judge = expanding_low < ma5
            curr_pct_judge = (self.intra_minute_close_badj / expanding_low - 1) >= 0.01
            curr_px_judge = self.intra_minute_close_badj > ma5
            return low_judge & low_pct_judge & curr_pct_judge & curr_px_judge
        if kind == 'all':
            return self.add_minutely_low_judge(kind='ma5_boost') | self.add_minutely_low_judge(kind='ma5')

if __name__ == '__main__':
    print('初始化...')
    start_date = 20210101
    end_date = 20210430
    t1 = time.time()
    sg = SignalGenerator(start_date=start_date, end_date=end_date)
    print('初始化完毕，耗时%ds' % (time.time() - t1))

    print('准备择时条件')
    t1 = time.time()
    # （这是一个修改点）
    index_cond = sg.add_index_cond() # 使用大盘择时条件
    # index_cond = sg.add2_index_cond() # 剔除特定交易日期
    print('择时条件计算完毕，耗时%ds' % (time.time() - t1))

    # # （这是一个修改点）
    # # 日间条件汇总
    # # 类型一个股
    # print('准备日间条件')
    # t1 = time.time()
    # st_cond = sg.add_st_cond()
    # mkt_cap_cond = sg.add_mkt_cap_cond()
    # t1_cond = sg.add_t1_cond()
    # t5_cond = sg.add_t5_cond()
    # multi_arrange_cond = sg.add_multi_arrange_cond()
    # ma_cond = sg.add_ma_cond()
    # amt_rank_cond = sg.add_amt_rank_cond()
    # check_shape(st_cond, mkt_cap_cond, t1_cond, multi_arrange_cond, ma_cond, amt_rank_cond, t5_cond)
    # daily_cond = st_cond & mkt_cap_cond & t1_cond & multi_arrange_cond & ma_cond & \
    #              amt_rank_cond & t5_cond
    # daily_cond = daily_cond & index_cond.values[:,None] # 这里要注意修改，根据是add1还是add2，去掉中括号这部分代码
    # daily_cond = daily_cond.fillna(False)
    # print('日间条件计算完毕，耗时%ds' % (time.time() - t1))

    # 类型2个股
    print('准备日间条件')
    t1 = time.time()
    st_cond = sg.add_st_cond()
    mkt_cap_cond = sg.add_mkt_cap_cond()
    t1_cond = sg.add2_t1_cond()
    t5_cond = sg.add2_t5_cond()
    multi_arrange_cond = sg.add_multi_arrange_cond()
    check_shape(st_cond, mkt_cap_cond, t1_cond, multi_arrange_cond, t5_cond)
    daily_cond = st_cond & mkt_cap_cond & t1_cond & multi_arrange_cond & t5_cond
    daily_cond = daily_cond.rolling(3).sum() > 0 # 在股票池上保留三天
    daily_cond = daily_cond.fillna(False)
    daily_cond = daily_cond & index_cond.values[:,None] # 大盘择时
    print('日间条件计算完毕，耗时%ds' % (time.time() - t1))

    print('准备日内条件')
    t1 = time.time()
    # （这是一个修改点）
    minutely_judge = sg.add_minutely_low_judge(kind='all')
    # min_pct_judge = sg.add_min_pct_judge()
    intra_judge = minutely_judge
    # intra_judge = minutely_judge & min_pct_judge.values
    intra_judge = intra_judge.fillna(False)
    print('日内条件计算完毕，耗时%ds' % (time.time() - t1))

    print('日间条件与日内条件整合')
    t1 = time.time()
    assert daily_cond.shape[1] == intra_judge.shape[1] # 数据校验
    assert daily_cond.columns.tolist() == intra_judge.columns.tolist()
    stk_minute_point = pd.DataFrame((intra_judge.values.reshape(daily_cond.shape[0], -1, daily_cond.shape[1]) & \
                               daily_cond.values[:, None, :]).reshape(-1, len(sg.stk_list)), index=intra_judge.index, columns=intra_judge.columns)
    stk_minute_point = stk_minute_point.dropna(how='all', axis=0) # 买点
    print('日间日内整合完毕，耗时%ds' % (time.time() - t1))

    stk_minute_point = del_star_stk(stk_minute_point) # 剔除科创板个股
    minutely_true_df = get_minutely_df_true(stk_minute_point)
    minutely_true_df = add_stock_name(minutely_true_df)
    daily_true_df = get_daily_df_true(daily_cond)
    daily_true_df = add_stock_name(daily_true_df)
    date_list = get_date_range(start_date, end_date)
    daily_true_df = daily_true_df[(daily_true_df['date']>=start_date) & daily_true_df['date']<=end_date]
    minutely_true_df = minutely_true_df[(minutely_true_df['date']>=start_date) & minutely_true_df['date']<=end_date]

    #####类型2的附加判断条件#####（只有类型2用这个）
    del_idx = list()
    ma4 = (sg.daily_close_badj.rolling(4).sum() / 5).shift(1)
    intra_ma = sg.intra_minute_close_badj / 5
    ma5 = pd.DataFrame((intra_ma.values.reshape(ma4.shape[0], 242, -1) + ma4.values[:, None, :]).reshape(-1, len(sg.stk_list)), \
        index=intra_ma.index, columns=intra_ma.columns)
    daily_ma5_min = ma5.groupby('date').min()
    daily_ma5_min_cond = sg.daily_low_badj > daily_ma5_min
    for idx in tqdm(range(len(minutely_true_df))):
        sample = minutely_true_df.iloc[idx]
        date, stk_id = sample['date'], sample['stk_id']
        look_back_days = [get_pre_trade_date(date), get_pre_trade_date(date, 2), get_pre_trade_date(date, 3), get_pre_trade_date(date, 4)]
        for tmp_date in look_back_days:
            if sg.daily_pctchg.at[tmp_date, stk_id] > 7:
                if daily_ma5_min_cond.at[tmp_date, stk_id]:
                    break
                else:
                    del_idx.append(idx)
                    break
            if daily_ma5_min_cond.at[tmp_date, stk_id]:
                continue
            else:
                del_idx.append(idx)
                break
    minutely_true_df = minutely_true_df.drop(del_idx)
    minutely_true_df = minutely_true_df.reset_index()
    ###############

    save_xlsx(daily_true_df, junk_path, 'daily_true_df1.xlsx')
    save_xlsx(minutely_true_df, junk_path, 'minutely_true_df1.xlsx')