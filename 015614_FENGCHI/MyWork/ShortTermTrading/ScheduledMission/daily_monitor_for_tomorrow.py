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
from ShortTermTrading.ConceptApi.ConceptApi import get_concept_values
from ShortTermTrading.interface.ActiveConceptApi import get_active_stock_1concept
from ShortTermTrading.Util.System import fetch_man_made_monitor_list, check_shape
from xquant.thirdpartydata.marketdata import MarketData
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import daily_monitor_path, man_made_concept_data_path
from tqdm import tqdm
from multiprocessing import Pool
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

        self.intra_minute_amt = intra_minute_amt
        self.intra_minute_close_badj = intra_minute_close_badj
        self.intra_minute_close_nbadj = intra_minute_close_nbadj

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

    def start_intra(self, to_deal_list, monitor_concept_df):
        ma = MarketData()

        now_date = get_today_date()
        now_start_datetime = now_date * 1000000 + 90000
        now_end_datetime = now_date * 1000000 + 150000
        triggered_list = [] # 记录当天已经触发过的个股
        while(True):
            for stk_id in to_deal_list:
                time.sleep(10) # 防止频繁调用
                now_mddatetime = get_curr_datetime()
                if now_mddatetime > 145700:
                    return
                now_mdtime = str((now_mddatetime // 100) * 100000)  # 转成数据格式
                print('===========================================')
                print('当前时间：', now_mddatetime)
                if now_mddatetime < 93200:
                    continue
                # 实时横截面数据
                df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
                df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
                cross_info = df1.append(df2)
                cross_info = cross_info.set_index('HTSCSecurityID', drop=True)

                stk_code = trans_int2windcode(stk_id)
                md_kline_df = ma.getMDSecurityKLineDataFrame(stk_code, str(now_start_datetime), \
                                str(now_end_datetime), 10, 20)
                if len(md_kline_df) == 0:
                    continue

                if now_mdtime in list(md_kline_df['MDTime']):
                    # print('最近1分钟数据已更新')
                    # 获取最近一分钟的index序号
                    now_index = md_kline_df[md_kline_df['MDTime'] == now_mdtime].index[0]
                else:
                    # print('最近1分钟数据未更新，取最后一分钟数据')
                    now_index = md_kline_df.index.tolist()[-1]

                now_minute_info = md_kline_df.iloc[now_index]
                close_px = now_minute_info['ClosePx']
                vwap = md_kline_df['TotalValueTrade'].sum() / md_kline_df['TotalVolumeTrade'].sum()
                print(get_stock_name(stk_id), ' vwap：', vwap)
                pre_close = cross_info.at[stk_code, 'PreClosePx']
                # 日内条件一：买入价大于vwap
                if close_px < vwap:
                    continue
                # 日内条件二：涨跌幅大于0
                pctchg = md_kline_df['ClosePx'] / pre_close - 1
                now_pctchg = pctchg.iloc[-1]
                print(get_stock_name(stk_id), ' 当前涨跌幅：', now_pctchg)
                if now_pctchg < 0:
                    continue
                # 日内条件三：涨速满足条件
                pctchg_3m = pctchg - pctchg.shift(3)
                pctchg_3m_judge = pctchg_3m > 0.015
                print(get_stock_name(stk_id), ' 当前涨速：', pctchg_3m.iloc[-5:-1].max())
                if pctchg_3m_judge.iloc[-5:-1].sum() == 0:
                    continue
                # 日内条件四：买入时量比没有下降
                md_kline_amt_rolling10_mean = md_kline_df['TotalValueTrade'].iloc[:-1].rolling(10).mean()
                md_kline_amt_rolling2_mean = md_kline_df['TotalValueTrade'].iloc[:-1].rolling(2).mean()
                md_kline_amt_speed = md_kline_amt_rolling2_mean / md_kline_amt_rolling10_mean
                if md_kline_amt_speed.iloc[-1] < 0.8:  # 要求大于0.8，小于的直接跳过
                    continue
                print(stk_id, get_stock_name(stk_id), now_mdtime)

                print('判断板块')
                sub_concept_list = monitor_concept_df[monitor_concept_df['Unnamed: 0'] == trans_int2windcode(stk_id)][
                    '主题'].tolist()
                for sub_concept in sub_concept_list:
                    sub_concept_pool = monitor_concept_df[monitor_concept_df['主题'] == sub_concept]
                    sub_concept_stk_list = sub_concept_pool['Unnamed: 0'].tolist()

                    # 开始计算主题内所有个股涨速
                    pctchg_list = []
                    pctchg_3m_list = []
                    open_pctchg_list = []
                    for sub_concept_stk_code in sub_concept_stk_list:
                        sub_md_kline_df = ma.getMDSecurityKLineDataFrame(sub_concept_stk_code, str(now_start_datetime),
                                                                         str(now_end_datetime), 10, 20)
                        pre_close = cross_info.at[stk_code, 'PreClosePx']
                        pctchg = sub_md_kline_df['ClosePx'] / pre_close - 1
                        open_pctchg_list.append(pctchg.iloc[0])
                        pctchg_list.append(pctchg.iloc[-1])
                        pctchg_3m = (pctchg - pctchg.shift(2)).iloc[-1]
                        pctchg_3m_list.append(pctchg_3m)
                    print('DEBUG')
                    print(stk_id, get_stock_name(stk_id), now_mdtime)
                    print('开盘平均涨幅：', np.mean(open_pctchg_list))
                    print('实时平均涨幅：', np.mean(pctchg_list))
                    if (np.mean(open_pctchg_list) > -0.02) & (np.mean(pctchg_list) > 0):
                        if stk_id not in triggered_list:
                            triggered_list.append(stk_id)
                            send_message(['fengchi'], str(stk_id) + ' %s 触发' % get_stock_name(stk_id) + sub_concept)
                        else:
                            continue
                    else:
                        continue

if __name__ == '__main__':
    tomorrow_date = get_tomorrow_date()
    end_date = get_pre_trade_date(tomorrow_date, -20)
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
        yes_date = get_pre_trade_date(tomorrow_date)
        daily_cond_list = daily_cond.loc[yes_date][daily_cond.loc[yes_date]].index.tolist()
        monitor_list = fetch_man_made_monitor_list()
        to_deal_list = list(set(monitor_list).intersection(set(daily_cond_list)))
        to_deal_name_list = list(map(get_stock_name, to_deal_list))
        print('准备监控的个股：', ','.join(to_deal_name_list))

        message = '%d发生分歧的个股：' % yes_date + ','.join(to_deal_name_list)
        send_message(['fengchi'], message)

        save_pickle(to_deal_list, daily_monitor_path + '分歧转一致追涨/%d/' % tomorrow_date, 'to_deal_list.pkl')
        print('得出有可能交易的个股，耗时%ds' % (time.time() - t1))
