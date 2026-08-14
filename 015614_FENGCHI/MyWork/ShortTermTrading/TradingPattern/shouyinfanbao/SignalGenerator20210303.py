# coding: utf-8
# Author：fengchi863
# Date ：2021/1/11 14:35
'''
根据最新的内容进行
'''

# coding: utf-8
# Author：fengchi863
# Date ：2021/1/11 14:35
'''
获取历史上的股票池，分歧转一致的涨停板股票池
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import get_stock_name_dict
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import root_path
from tqdm import tqdm
import time

class SignalGenerator:

    def __init__(self, start_date=20200101, end_date=20201231):
        shift_start_date = get_pre_trade_date(start_date, 30)
        shift_end_date = get_pre_trade_date(end_date, 5)
        date_list = get_date_range(shift_start_date, end_date)
        daily_st = clean_stock_list(no_pause=False, no_ST=True, least_live_days=0, start_date=shift_start_date, end_date=end_date)
        stk_list = sorted(daily_st.columns.tolist())

        daily_close_badj = get_daily_1factor('close_badj', code_list=stk_list, date_list=date_list)
        daily_pre_close_badj = get_daily_1factor('pre_close_badj', code_list=stk_list, date_list=date_list)
        daily_high_badj = get_daily_1factor('high_badj', code_list=stk_list, date_list=date_list)
        daily_low_badj = get_daily_1factor('low_badj', code_list=stk_list, date_list=date_list)
        daily_swing = get_daily_1factor('swing', code_list=stk_list, date_list=date_list)
        daily_open_badj = get_daily_1factor('open_badj', code_list=stk_list, date_list=date_list)
        daily_pctchg = get_daily_1factor('pct_chg', code_list=stk_list, date_list=date_list)
        daily_amt = get_daily_1factor('amt', code_list=stk_list, date_list=date_list)
        daily_turn = get_daily_1factor('turn', code_list=stk_list, date_list=date_list)
        daily_limit_max = get_daily_1factor('limit_max', code_list=stk_list, date_list=date_list)
        daily_adj_factor = get_daily_1factor('adjfactor', code_list=stk_list, date_list=date_list)
        daily_high = get_daily_1factor('high', code_list=stk_list, date_list=date_list)
        daily_low = get_daily_1factor('low', code_list=stk_list, date_list=date_list)

        self.date_list = date_list
        self.shift_start_date = shift_start_date
        self.shift_end_date = shift_end_date
        self.start_date = start_date
        self.end_date = end_date
        self.stk_list = stk_list
        self.daily_st = daily_st.reindex_like(daily_close_badj).fillna(True)
        self.daily_close_badj = daily_close_badj
        self.daily_pre_close_badj = daily_pre_close_badj
        self.daily_high_badj = daily_high_badj
        self.daily_low_badj = daily_low_badj
        self.daily_swing = daily_swing
        self.daily_open_badj = daily_open_badj
        self.daily_pctchg = daily_pctchg
        self.daily_amt = daily_amt
        self.daily_turn = daily_turn
        self.daily_limit_max = daily_limit_max
        self.daily_adj_factor = daily_adj_factor
        self.daily_high = daily_high
        self.daily_low = daily_low

        self.daily_max_pct = self.calc_limit_up_pct()
        self.stk_code_name_dict = get_stock_name_dict()

    def calc_limit_up_pct(self):
        stk_list20 = list() # 20cm
        for stk_code in self.stk_list:
            if stk_code // 1000 == 300 or stk_code // 1000 == 688:
                stk_list20.append(stk_code)
        stk_list10 = list(set(self.stk_list) - set(stk_list20))

        daily_max_pct = pd.DataFrame(index=self.date_list, columns=self.stk_list)
        daily_max_pct.loc[self.shift_start_date:20200820, self.stk_list] = 0.098
        daily_max_pct.loc[20200820:self.end_date, stk_list10] = 0.098
        daily_max_pct.loc[20200820:self.end_date, stk_list20] = 0.198
        return daily_max_pct

    # 日间条件
    def add_st_cond(self):
        return self.daily_st

    # 条件二：日间涨跌幅条件
    def add_pctchg_cond(self):
        ###
        daily_pctchg_threshold = 3 # 得出来的是百分比
        stk_pctchg_judge_d2 = self.daily_pctchg.shift(2) > daily_pctchg_threshold
        ###
        stk_daily_pct_chg_rank = self.daily_close_badj.pct_change(3).rank(ascending=False, axis=1)
        stk_daily_pct_chg_rank_judge = stk_daily_pct_chg_rank <= 80
        stk_daily_pct_chg_rank_judge = stk_daily_pct_chg_rank_judge.shift(2)

        return stk_pctchg_judge_d2 & stk_daily_pct_chg_rank_judge

    # 条件三：分歧日条件
    def add_t1_cond(self):
        # 分歧日涨跌幅限制
        stk_pctchg_judge_d1 = ((self.daily_pctchg < self.daily_max_pct * 0.9 * 100) & (
                    self.daily_pctchg > self.daily_max_pct * -0.9 * 100)).shift(1)
        # 去掉见顶分时
        stk_daily_baodie1 = self.daily_close_badj < self.daily_low_badj * 1.005  # 大于全天最低价的千5
        stk_daily_baodie2 = self.daily_swing > 0.1  # 振幅大于10%
        stk_daily_baodie_judge = stk_daily_baodie1 & stk_daily_baodie2
        stk_daily_baodie_judge = ~(stk_daily_baodie_judge.shift(1).fillna(False))

        return stk_pctchg_judge_d1 & stk_daily_baodie_judge

    # 条件四：分歧日前一天收盘价为过去20天最高价
    def add_t2_cond(self):
        stk_rolling_max_judge = self.daily_close_badj >= self.daily_close_badj.rolling(20).max()
        stk_rolling_max_judge = stk_rolling_max_judge.shift(2)
        return stk_rolling_max_judge

    def add_daily_amt_cond(self):
        stk_high_pctchg = self.daily_high_badj / self.daily_pre_close_badj
        stk_reach_limit_judge = stk_high_pctchg > self.daily_max_pct

        stk_daily_amt_pct_1d = self.daily_amt.pct_change(1)
        stk_daily_amt_pct_judge1 = stk_daily_amt_pct_1d > 0
        stk_daily_amt_pct_judge2 = stk_daily_amt_pct_1d > -0.2

        stk_daily_amt_judge = (stk_daily_amt_pct_judge2 & stk_reach_limit_judge) | (
                    stk_daily_amt_pct_judge1 & (~stk_reach_limit_judge))
        stk_daily_amt_judge = stk_daily_amt_judge.shift(1)
        return stk_daily_amt_judge

    def add_turn_cond(self):
        stk_daily_turn_rolling10 = self.daily_turn.rolling(10).mean()
        stk_daily_turn_judge = self.daily_turn > stk_daily_turn_rolling10
        return stk_daily_turn_judge.shift(1)

    def add_limit_up_cond(self):
        stk_daily_limit_up_cond = self.daily_high == self.daily_limit_max
        stk_daily_not_all_limit_up = self.daily_low != self.daily_limit_max
        return stk_daily_limit_up_cond & stk_daily_not_all_limit_up

    # 日内条件
    def add_pctchg_judge(self):
        stk_daily_pre_close = get_daily_1factor('pre_close_badj', date_list=self.date_list, code_list=self.stk_list)
        stk_minute_pctchg = pd.DataFrame(
            (self.intra_minute_close_badj.values.reshape(stk_daily_pre_close.shape[0], 242, stk_daily_pre_close.shape[1]) /
             stk_daily_pre_close.values[:, None, :] - 1).reshape(self.intra_minute_close_badj.shape[0], self.intra_minute_close_badj.shape[1]), \
            index=self.intra_minute_close_badj.index, columns=self.intra_minute_close_badj.columns)
        stk_minute_pctchg_buy_judge = stk_minute_pctchg > 0  # 买入时涨跌幅大于0 stk_minute_pctchg_buy_judge
        return stk_minute_pctchg_buy_judge

    def add_qrr_judge(self):
        stk_amt_rolling10 = self.intra_minute_amt.groupby('date').rolling(10).mean().fillna(100)  # 控制前10分钟量比一定满足
        stk_amt_rolling_2m_mean = self.intra_minute_amt.groupby('date').rolling(2).mean()
        stk_intraday_qrr_judge = (stk_amt_rolling_2m_mean / stk_amt_rolling10 >= 0.8)
        stk_intraday_qrr_judge = stk_intraday_qrr_judge.droplevel(0)  # 买入时量比没有下降
        return stk_intraday_qrr_judge

    def add_vwap_judge(self):
        vol = get_minute_1factor('vol', code_list=self.stk_list, start_datetime=self.shift_start_date, end_datetime=self.end_date)
        amt = get_minute_1factor('amt', code_list=self.stk_list, start_datetime=self.shift_start_date, end_datetime=self.end_date)
        vwap = amt.groupby('date').cumsum() / vol.groupby('date').cumsum()
        stk_minute_vwap_judge = self.intra_minute_close_nbadj > vwap  # 买入时股价高于当天vwap
        return stk_minute_vwap_judge

    def add_speed_amt_judge(self):
        pctchg_speed_2m = self.intra_minute_close_badj.pct_change(3)  # 三分钟限制了只能从934开始买了
        pctchg_speed_2m_judge = pctchg_speed_2m > 0.015
        stk_speed_amt_judge = self.add_qrr_judge() & pctchg_speed_2m_judge
        stk_speed_amt_judge = stk_speed_amt_judge.rolling(5).sum() >= 1
        return stk_speed_amt_judge

    # 叠加板块
    def get_need_stk_list(self, s: pd.Series):
        pct10_num = len(s) * 0.2
        if pct10_num <= 3:
            return s.index.tolist()
        elif 3 < pct10_num <= 7:
            return s.sort_values(ascending=False)[:int(pct10_num)].index.tolist()
        elif pct10_num > 7:
            return s.sort_values(ascending=False)[:7].index.tolist()
        else:
            return list()

if __name__ == '__main__':
    print('初始化...')
    t1 = time.time()
    sg = SignalGenerator(start_date=20140101, end_date=20201231)
    print('初始化完毕，耗时%ds' % (time.time() - t1))
    # 日间条件汇总

    print('准备日间条件')
    t1 = time.time()
    st_cond = sg.add_st_cond()
    pctchg_cond = sg.add_pctchg_cond()
    t1_cond = sg.add_t1_cond()
    t2_cond = sg.add_t2_cond()
    amt_cond = sg.add_daily_amt_cond()
    turn_cond = sg.add_turn_cond()
    limit_up_cond = sg.add_limit_up_cond()
    assert st_cond.shape == pctchg_cond.shape == t1_cond.shape == t2_cond.shape == amt_cond.shape == turn_cond.shape == limit_up_cond.shape
    daily_cond = st_cond & pctchg_cond & t1_cond & t2_cond & amt_cond & turn_cond & limit_up_cond
    print('日间条件计算完毕，耗时%ds' % (time.time() - t1))

    print(daily_cond.shape)
    daily_cond = daily_cond.fillna(False)

    # 叠加日内条件
    print('准备日内条件')
    t1 = time.time()
    pctchg_judge = sg.add_pctchg_judge()
    vwap_judge = sg.add_vwap_judge()
    speed_amt_judge = sg.add_speed_amt_judge()
    assert pctchg_judge.shape == vwap_judge.shape == speed_amt_judge.shape
    intra_judge = pctchg_judge & vwap_judge & speed_amt_judge
    print('日内条件计算完毕，耗时%ds' % (time.time() - t1))


    daily_cond.to_pickle(root_path + 'LimitUpPredStrategy/stock_pool/virga2consis.pkl')
    # 检验结果
    # res = daily_cond.stack()[daily_cond.stack()]




