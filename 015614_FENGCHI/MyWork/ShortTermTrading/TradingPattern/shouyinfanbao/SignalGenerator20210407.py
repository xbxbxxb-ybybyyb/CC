# coding: utf-8
# Author：fengchi863
# Date ：2021/1/11 14:35
'''
根据最新的内容进行
获取历史上的股票池，分歧转一致的涨停板股票池，叠加日内条件以及板块条件
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import get_stock_name_dict, get_active_concept_list
from ShortTermTrading.ConceptApi.ConceptApi import get_concept_values
import pandas as pd, numpy as np
from multiprocessing import Pool
from ShortTermTrading.conf.path_conf import junk_path
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

        self.intra_minute_amt = intra_minute_amt
        self.intra_minute_close_badj = intra_minute_close_badj
        self.intra_minute_close_nbadj = intra_minute_close_nbadj

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

    def add_concept_cond(self, stats_profit):
        def wrapper(concept):
            trigger_concat = []
            concept_stk = get_concept_values('Concept_StockList', concept, start_date=self.shift_start_date,
                                             end_date=self.end_date)
            concept_stk_copy = pd.DataFrame(np.array(concept_stk.loc[stats_profit.index.get_level_values('date')]), \
                                            index=stats_profit.index, columns=concept_stk.columns)
            stk_list = list(set(stk_buy_point.columns.tolist()).intersection(set(concept_stk_copy.columns.tolist())))
            trigger_stk_1concept = stats_profit[stk_list] & concept_stk_copy[stk_list]

            # 判断这个概念能否在那一分钟触发
            trigger_stk_1concept_judge = trigger_stk_1concept.sum(axis=1) >= 1
            trigger_stk_1concept_judge = trigger_stk_1concept_judge[trigger_stk_1concept_judge]
            trigger_stk_1concept_judge = trigger_stk_1concept_judge.reset_index()

            for idx in range(len(trigger_stk_1concept_judge)):
                date, time = trigger_stk_1concept_judge.iloc[idx]['date'], trigger_stk_1concept_judge.iloc[idx]['time']
                concept_stk = get_concept_values('Concept_StockList', concept, date, date).loc[date]
                concept_stk_list = concept_stk[concept_stk].index.tolist()
                if concept_stk_list == 0:
                    continue
                else:
                    tmp_minute_close_badj = get_minute_1factor('close_badj', code_list=concept_stk_list,
                                                                       start_datetime=date, end_datetime=date)
                    tmp_daily_pre_close_badj = get_daily_1day(['pre_close_badj'], code_list=concept_stk_list,
                                                                      date=date)
                    start_stk_pctchg = tmp_minute_close_badj.loc[date, 930] / tmp_daily_pre_close_badj[
                        'pre_close_badj'] - 1
                    tmp_stk_pctchg = tmp_minute_close_badj.loc[date, time] / tmp_daily_pre_close_badj[
                        'pre_close_badj'] - 1

                    need_stk_list = self.get_need_stk_list(tmp_stk_pctchg)
                    if len(need_stk_list) == 0:
                        continue
                    if start_stk_pctchg[need_stk_list].mean() < -0.02:
                        continue
                    if tmp_stk_pctchg[need_stk_list].mean() < -0.02:
                        continue

                    tmp_s = trigger_stk_1concept.loc[date, time]
                    trigger_stk_list = tmp_s[tmp_s].index.tolist()
                    for trigger_stk in trigger_stk_list:
                        trigger_concat.append((date, time, concept, trigger_stk))
            return trigger_concat

        active_concept_list2020 = get_active_concept_list()
        pbar = tqdm(total=len(active_concept_list2020))

        def update(*param):
            pbar.update()
            if pbar.last_print_n == len(active_concept_list2020):
                pbar.close()

        pool = Pool(16)
        pool_dict = dict()
        for concept in active_concept_list2020:
            pool_dict[concept] = pool.apply_async(wrapper, (concept,), callback=update)
        pool.close()
        pool.join()
        # pool_dict = dict()
        # for concept in active_concept_list2020:
        #     pool_dict[concept] = wrapper(concept)


        records = []
        for concept in pool_dict:
            try:
                records += pool_dict[concept].get()
            except:
                print(concept, 'wrong')
                records += wrapper(concept)

        # 去重
        record_set = set()
        final_record = []
        for record in records:
            date, time, stk_code = record[0], record[1], record[3]
            if (date, time, stk_code) not in record_set:
                record_set.add((date, time, stk_code))
                final_record.append(record)
            else:
                continue

        return final_record

if __name__ == '__main__':
    print('初始化...')
    t1 = time.time()
    sg = SignalGenerator(start_date=20200101, end_date=20210228) # 因全部计算量太大，所以采用每两年计算一次，然后使用script中的脚本拼接
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

    print('日间条件与日内条件整合')
    t1 = time.time()
    assert daily_cond.shape[1] == intra_judge.shape[1]  # 数据校验
    assert daily_cond.columns.tolist() == intra_judge.columns.tolist()
    daily_judge = pd.DataFrame(np.array(daily_cond.loc[intra_judge.index.get_level_values('date')]), \
                               index=intra_judge.index, columns=intra_judge.columns)
    stk_buy_point = daily_judge & intra_judge  # 总的触发信号
    stk_buy_point = stk_buy_point.dropna(how='all', axis=0)  # 买点
    print('日间日内整合完毕，耗时%ds' % (time.time() - t1))

    print('叠加板块')
    t1 = time.time()
    stk_buy_point = stk_buy_point.fillna(False)
    stats_profit = (stk_buy_point * 1.0)[stk_buy_point]
    stats_profit = stats_profit.groupby('date').cumsum() == 1
    record = sg.add_concept_cond(stats_profit=stats_profit)
    print('叠加板块完毕，耗时%ds' % (time.time() - t1))

    rec_df = pd.DataFrame()
    for rec in record:
        rec_df = rec_df.append(pd.DataFrame([[rec[0], rec[1], rec[3]]]), ignore_index=True)

    rec_df.to_pickle(junk_path + 'fenqizhuanyizhi_4.pkl')