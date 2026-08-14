# coding: utf-8
# Author：fengchi863
# Date ：2021/5/31 13:57

'''
版本V2-20210602：
活跃主题 补涨/中位股 盘中拉升半路低吸
日间刻画
1、目前为市场活跃主题 主题有龙头股【人工】
2、个股T-1日为十字星(上影 下影线>=2%)
3、均线：10MA>20MA（量化） 且个股相对低位（人工）

T日盘中刻画
1、个股出现快速拉升
定义：2分钟涨速>=0.8%，且该2分钟的平均成交量>=前10分钟平均成交量的1.2倍（如开盘不足12分钟，不判断该条件） 且当前时刻（推送提示的时间）个股绝对涨幅>=1%
2、当前时刻前10分钟，主题存在其他个股出现上述拉升（推送出个股数量 代码名称）
'''

import pandas as pd, numpy as np
from FaaMonitor.dataApi import getData
from FaaMonitor.dataApi import tradeDate
from FaaMonitor.dataApi import stockList
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.conf.path_conf import realtime_date_path, man_made_concept_data_path
from realtimeApi.getdata_from_open import data_prepare, get_oneconcept_alldata
from FaaMonitor.Util.tools import send_message
from FaaMonitor.Util.System import workmate_dict
from multiprocessing import Pool
from FaaMonitor.Util.MyUtil import MyUtil
import time
from pprint import pprint

class MiddlePoint:
    def __init__(self, end_date):
        shift_date = tradeDate.get_pre_trade_date(end_date, 160)
        date_list = tradeDate.get_date_range(shift_date, end_date)
        daily_close = getData.get_daily_1factor('close', date_list=date_list)
        daily_high = getData.get_daily_1factor('high', date_list=date_list)
        daily_low = getData.get_daily_1factor('low', date_list=date_list)
        daily_open = getData.get_daily_1factor('open', date_list=date_list)
        daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list)
        limit_up = getData.get_daily_1factor('limit_up', date_list=date_list)
        pre_close = data_prepare(str(end_date))['pre_close']
        pre_close = pre_close.droplevel(0)
        pre_close.index = pre_close.index.map(stockList.trans_windcode2int)

        self.start_monitor = False
        self.shift_date = shift_date
        self.daily_close = daily_close
        self.daily_high = daily_high
        self.daily_low = daily_low
        self.daily_open = daily_open
        self.daily_pctchg = daily_pctchg
        self.limit_up = limit_up
        self.pre_close = pre_close

        self.daily_stock = None
        self.concept_df = None
        self.cover_concept = None

    # 获取日间满足条件的股票
    def calc_daily_stock(self):
        # 读取股票池，主题有龙头股，个股相对低位
        man_stk_list = self.daily_close.columns.tolist()

        inter_cond1_list = self.inter_cond1()
        inter_cond2_list = self.inter_cond2()
        inter_cond_list = list(set(inter_cond1_list).
                               intersection(set(inter_cond2_list)))

        self.daily_stock = sorted(list(set(man_stk_list).intersection(inter_cond_list)))
        print('日间股票池已计算完成')

    # 根据股票选出要监控的主题
    def fetch_concept_list(self):
        # 获取每日人工定义的股票池，其中是主题龙头，并且断板横盘震荡
        concept_df = pd.read_excel(man_made_concept_data_path)
        concept_df = concept_df.rename(columns={'Unnamed: 0': '股票代码'})
        concept_df['主题'] = concept_df['概念板块'] + '_' + concept_df['子主题']
        self.concept_df = concept_df
        concept_df['今日是否覆盖'] = concept_df['股票代码'].apply(lambda x: True if \
            stockList.trans_windcode2int(x) in self.daily_stock else False)
        cover_concept = concept_df[concept_df['今日是否覆盖']]['主题'].tolist()
        self.cover_concept = cover_concept

    def inter_cond1(self):
        # open > close 的十字星
        cond1 = self.daily_open > self.daily_close
        cond2 = (self.daily_high - self.daily_open) / self.daily_open
        cond3 = (self.daily_close - self.daily_low) / self.daily_open
        ret1 = cond1 & (cond2 > 0.02) & (cond3 > 0.02)

        # open <= close 的十字星
        cond1 = ~cond1
        cond2 = (self.daily_high - self.daily_close) / self.daily_open
        cond3 = (self.daily_open - self.daily_low) / self.daily_open
        ret2 = cond1 & (cond2 > 0.02) & (cond3 > 0.02)

        ret = ret1 | ret2
        ret_list = ret.iloc[-1][ret.iloc[-1]].index.tolist()
        return ret_list

    def inter_cond2(self):
        ma10 = self.daily_close.rolling(10).mean()
        ma20 = self.daily_close.rolling(20).mean()
        cond = ma10 > ma20
        stk_df = cond
        stk_list = stk_df.iloc[-1][stk_df.iloc[-1]].index.tolist()
        return stk_list

    def add2excel(self, df):
        self.calc_daily_stock()
        df['补涨/中位股'] = df['股票代码'].apply(lambda x:
                        '是' if stockList.trans_windcode2int(x) in self.daily_stock else '否')
        return df

if __name__ == '__main__':
    mp = MiddlePoint()
    mp.calc_daily_stock()
    mp.fetch_concept_list()