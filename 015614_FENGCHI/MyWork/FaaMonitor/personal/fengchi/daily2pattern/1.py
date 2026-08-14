# coding: utf-8
# Author：fengchi863
# Date ：2021/2/1 15:04

'''
每天为第二天的分歧转一致个股生成监控
'''

import os, sys
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')

from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_int2windcode
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import *
from ShortTermTrading.Util.System import fetch_man_made_monitor_list, check_shape
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import daily_monitor_path, man_made_concept_data_path
from FaaMonitor.Util.DtUtil import DtUtil
import time

class DailyMonitor:

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

        self.date_list = date_list
        self.shift_start_date = shift_start_date
        self.shift_end_date = shift_end_date
        self.start_date = start_date
        self.end_date = end_date
        self.stk_list = stk_list
        self.daily_close_badj = daily_close_badj
        self.daily_st = daily_st.reindex_like(daily_close_badj).fillna(True)
        self.daily_pre_close_badj = daily_pre_close_badj
        self.daily_high_badj = daily_high_badj
        self.daily_low_badj = daily_low_badj
        self.daily_swing = daily_swing
        self.daily_open_badj = daily_open_badj
        self.daily_pctchg = daily_pctchg
        self.daily_amt = daily_amt
        self.daily_turn = daily_turn

        self.daily_max_pct = self.calc_limit_up_pct()

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
        stk_pctchg_judge_d2 = self.daily_pctchg > daily_pctchg_threshold
        ###
        stk_daily_pct_chg_rank = self.daily_close_badj.pct_change(3).rank(ascending=False, axis=1)
        stk_daily_pct_chg_rank_judge = stk_daily_pct_chg_rank <= 80
        stk_daily_pct_chg_rank_judge = stk_daily_pct_chg_rank_judge

        return (stk_pctchg_judge_d2 & stk_daily_pct_chg_rank_judge).shift(1)

    # 条件三：分歧日条件
    def add_t1_cond(self):
        # 分歧日涨跌幅限制
        stk_pctchg_judge_d1 = ((self.daily_pctchg < self.daily_max_pct * 0.9 * 100) & (
                    self.daily_pctchg > self.daily_max_pct * -0.9 * 100))
        # 去掉见顶分时
        stk_daily_baodie1 = self.daily_close_badj < self.daily_low_badj * 1.005  # 大于全天最低价的千5
        stk_daily_baodie2 = self.daily_swing > 0.1  # 振幅大于10%
        stk_daily_baodie_judge = stk_daily_baodie1 & stk_daily_baodie2
        stk_daily_baodie_judge = ~stk_daily_baodie_judge

        return stk_pctchg_judge_d1 & stk_daily_baodie_judge

    # 条件四：分歧日前一天收盘价为过去20天最高价
    def add_t2_cond(self):
        stk_rolling_max_judge = self.daily_close_badj >= self.daily_close_badj.rolling(20).max()
        stk_rolling_max_judge = stk_rolling_max_judge
        return stk_rolling_max_judge.shift(1)

    def add_daily_amt_cond(self):
        stk_high_pctchg = self.daily_high_badj / self.daily_pre_close_badj
        stk_reach_limit_judge = stk_high_pctchg > self.daily_max_pct

        stk_daily_amt_pct_1d = self.daily_amt.pct_change(1)
        stk_daily_amt_pct_judge1 = stk_daily_amt_pct_1d > 0
        stk_daily_amt_pct_judge2 = stk_daily_amt_pct_1d > -0.2

        stk_daily_amt_judge = (stk_daily_amt_pct_judge2 & stk_reach_limit_judge) | (
                    stk_daily_amt_pct_judge1 & (~stk_reach_limit_judge))
        return stk_daily_amt_judge

    def add_turn_cond(self):
        stk_daily_turn_rolling10 = self.daily_turn.rolling(10).mean()
        stk_daily_turn_judge = self.daily_turn > stk_daily_turn_rolling10
        return stk_daily_turn_judge

    @staticmethod
    def get_stock_concept(stk_code, concept_df:pd.DataFrame):
        concept_list = concept_df[concept_df['股票代码'] == stockList.trans_int2windcode(stk_code)]['主题'].tolist()
        return ','.join(concept_list)

if __name__ == '__main__':
    tomorrow_date = get_tomorrow_date()
    end_date = DtUtil.get_today_date()
    start_date = get_pre_trade_date(tomorrow_date, 60)
    print('明天日期为%d，为明天的分歧转一致策略作准备！' % tomorrow_date)
    print('初始化...')
    t1 = time.time()
    dm = DailyMonitor(start_date=start_date, end_date=end_date)
    print('初始化完毕，耗时%ds' % (time.time() - t1))
    if not os.path.exists(daily_monitor_path + '分歧转一致追涨/%d/' % tomorrow_date + 'to_deal_list.pkl'):
        # 日间条件汇总
        print('准备日间条件')
        t1 = time.time()
        st_cond = dm.add_st_cond()
        pctchg_cond = dm.add_pctchg_cond()
        t1_cond = dm.add_t1_cond()
        t2_cond = dm.add_t2_cond()
        amt_cond = dm.add_daily_amt_cond()
        turn_cond = dm.add_turn_cond()
        check_shape(st_cond, pctchg_cond, t1_cond, t2_cond, amt_cond, turn_cond)
        daily_cond = st_cond & pctchg_cond & t1_cond & t2_cond & amt_cond & turn_cond
        print('日间条件计算完毕，耗时%ds' % (time.time() - t1))

        print('准备与监控池整合')
        t1 = time.time()
        daily_cond_list = daily_cond.loc[end_date][daily_cond.loc[end_date]].index.tolist()
        monitor_list = fetch_man_made_monitor_list()
        to_deal_list = list(set(monitor_list).intersection(set(daily_cond_list)))
        to_deal_name_list = list(map(get_stock_name, to_deal_list))
        print('准备监控的个股：', ','.join(to_deal_name_list))
        message = '%d发生分歧的个股：' % end_date + ','.join(to_deal_name_list)

        print('得出有可能交易的个股，耗时%ds' % (time.time() - t1))

        concept_df = pd.read_excel(man_made_concept_data_path)
        concept_df = concept_df.rename(columns={'Unnamed: 0': '股票代码'})
        concept_df['主题'] = concept_df['概念板块'] + '_' + concept_df['子主题']
        df = pd.DataFrame([to_deal_list, to_deal_name_list], index=['股票代码','股票名称']).T
        df['所属主题'] = df['股票代码'].apply(lambda x: dm.get_stock_concept(x, concept_df))
        save_xlsx(df, daily_monitor_path + '分歧转一致追涨/%d/' % tomorrow_date, '分歧转一致追涨%d.xlsx' % tomorrow_date)
        send_file(['015614'], daily_monitor_path + '分歧转一致追涨/%d/' % tomorrow_date + '分歧转一致追涨%d.xlsx' % tomorrow_date)