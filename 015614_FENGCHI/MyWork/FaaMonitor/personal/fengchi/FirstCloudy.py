# coding: utf-8
# Author：fengchi863
# Date ：2021/6/1 15:01

'''
版本V3-20210624：
日间筛选：
1、	主题强，主题地位高（市场主流/次主流主题，关注度高），个股强势，存在分歧后转一致的预期【主观】
2、	T-1日首阴：首阴当天收盘价/盘中最高价-1<=-3%，即盘中出现冲高回落走势；
3、	T-1日成交量放量：如T-3日至T-2日平均成交量/过去10日成交量均值>=1.2，则T-1日成交量>=T-3日至T-2日平均成交量*0.7；否则 T-1日成交量 >= T-2日*0.9
4、	T-1日之前，用原定义：个股连续三日每日涨跌幅均超过3%以上并且收阳且市场排名排在前80位；或者 连续2日或以上出现涨停板（非创业板） // 1日或以上出现涨停板（创业板20cm）

日内条件：
1、	当前时刻（推送提示的时间）个股绝对涨幅>=1%
2、	涨速满足近5分钟内存在2分钟涨速>=0.8%，且该2分钟的平均成交量>=前10分钟平均成交量的1.2倍
'''

import pandas as pd
from FaaMonitor.dataApi import getData
from FaaMonitor.dataApi import tradeDate
from FaaMonitor.dataApi import stockList
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.conf.path_conf import realtime_date_path, man_made_concept_data_path
from realtimeApi.getdata_from_open import data_prepare, get_oneconcept_alldata, get_stock_factor
from FaaMonitor.Util.tools import send_message
from FaaMonitor.Util.System import workmate_dict
from multiprocessing import Pool
from FaaMonitor.Util.MyUtil import MyUtil
import time
from pprint import pprint

class FirstCloudy:
    def __init__(self):
        date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()
        shift_date = tradeDate.get_pre_trade_date(date, 160)
        date_list = tradeDate.get_date_range(shift_date, yes_date)
        daily_close = getData.get_daily_1factor('close', date_list=date_list)
        daily_high = getData.get_daily_1factor('high', date_list=date_list)
        daily_low = getData.get_daily_1factor('low', date_list=date_list)
        daily_open = getData.get_daily_1factor('open', date_list=date_list)
        daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list)
        limit_up = getData.get_daily_1factor('limit_up', date_list=date_list)
        daily_amt = getData.get_daily_1factor('amt', date_list=date_list)
        cur_limitup = data_prepare(str(date))['max_price']
        cur_limitup = cur_limitup.droplevel(0)
        cur_limitup.index = cur_limitup.index.map(stockList.trans_windcode2int)
        pre_close = data_prepare(str(date))['pre_close']
        pre_close = pre_close.droplevel(0)
        pre_close.index = pre_close.index.map(stockList.trans_windcode2int)

        self.start_monitor = False
        self.date = date
        self.shift_date = shift_date
        self.yes_date = yes_date
        self.daily_close = daily_close
        self.daily_high = daily_high
        self.daily_low = daily_low
        self.daily_open = daily_open
        self.daily_pctchg = daily_pctchg
        self.limit_up = limit_up
        self.pre_close = pre_close
        self.daily_amt = daily_amt

        self.daily_stock = None
        self.concept_df = None
        self.cover_concept = None

    # 获取日间满足条件的股票
    def calc_daily_stock(self):
        # 读取股票池，主题有龙头股，个股相对低位
        # man_stk_list = self.daily_close.columns.tolist()
        path = '/data/group/800442/800319/Concept_monitor/主题个股监控%d.xlsx' % self.yes_date
        df1 = pd.read_excel(path)
        df1 = df1.rename(columns={'Unnamed: 0': '股票代码'})
        man_stk_list = list(set(df1['股票代码'].tolist()))
        man_stk_list = list(map(stockList.trans_windcode2int, man_stk_list))

        inter_cond1_list = self.inter_cond1()
        inter_cond2_list = self.inter_cond2()
        inter_cond3_list = self.inter_cond3()
        inter_cond_list = list(set(inter_cond1_list).
                               intersection(set(inter_cond2_list)).
                               intersection(set(inter_cond3_list)))

        self.daily_stock = sorted(list(set(man_stk_list).intersection(inter_cond_list)))
        print('日间股票池已计算完成')

    def inter_cond1(self):
        # T-1日首阴（暂用原定义）：首阴当天收盘价/盘中最高价-1<=-3%（即盘中出现冲高回落走势）
        cond = (self.daily_close / self.daily_high - 1) < -0.03
        stk_list = cond.iloc[-1][cond.iloc[-1]].index.tolist()
        return stk_list

    def inter_cond2(self):
        # T-1日成交量放量：如T-3日至T-2日平均成交量/过去10日成交量均值>=1.2，则T-1日成交量>=T-3日至T-2日平均成交量*0.7；否则 T-1日成交量 >= T-2日*0.9
        cond1 = self.daily_amt.shift(1).rolling(2).mean() / self.daily_amt.shift(3).rolling(10).mean() > 1.2
        cond2 = self.daily_amt > self.daily_amt.shift(1).rolling(2).mean() * 0.7
        cond3 = self.daily_amt / self.daily_amt.shift(1) > 0.9
        cond = (cond1.iloc[-1] & cond2.iloc[-1]) | (~cond1.iloc[-1] & cond3.iloc[-1])
        stk_list = cond[cond].index.tolist()
        return stk_list

    def inter_cond3(self):
        # 个股连续三日每日涨跌幅均超过3%以上并且收阳且市场排名排在前80位；或者 连续2日或以上出现涨停板
        # 1、市场排名
        pct_3d = self.daily_close.shift(1) / self.daily_close.shift(4) - 1
        rank_pct = pct_3d.iloc[-1].rank(ascending=False) <= 80
        stk_list1 = rank_pct[rank_pct].index.tolist()
        # 2、每日涨跌幅
        cond = (self.daily_pctchg.shift(1) > 3).rolling(3).mean() == 3
        stk_list2 = cond.iloc[-1][cond.iloc[-1]].index.tolist()

        # 3、连续两日以上出现涨停板
        cond = (self.limit_up.shift(1).rolling(2).sum() == 2)
        tmp_stk_list1 = cond.iloc[-1][cond.iloc[-1]].index.tolist()

        cond2 = self.limit_up.shift(1) == 1
        tmp_stk_list2 = list(filter(lambda x: x // 100000 == 3 or x // 1000 == 688, cond2.iloc[-1][cond2.iloc[-1]].index.tolist()))

        stk_list3 = list(set(tmp_stk_list1).union(set(tmp_stk_list2)))

        stk_list = list((set(stk_list1).intersection(set(stk_list2))).union(set(stk_list3)))
        return stk_list

    def add2excel(self, df):
        self.calc_daily_stock()
        df['龙头首阴'] = df['股票代码'].apply(lambda x:
                        '是' if stockList.trans_windcode2int(x) in self.daily_stock else '否')
        return df

    def start_intra(self):
        has_send_message = list()
        pre_close = self.pre_close.loc[self.daily_stock]
        pre_close.index = pre_close.index.map(stockList.trans_int2windcode)
        while True:
            t1 = time.time()

            # 完善的退出机制
            if DtUtil.get_now_hm() > 1500:
                print('终于收盘了，辛劳的一天终于结束了，可以把资源释放出来了')
                break
            elif DtUtil.get_now_hm() < 930:
                continue

            daily_stock = list(map(stockList.trans_int2windcode, self.daily_stock))
            df = get_stock_factor(['ClosePx', 'TotalValueTrade'], daily_stock)

            pct_chg = df['ClosePx'] / pre_close - 1 # 绝对涨跌幅
            pct_chg_flag = pct_chg > 0.01

            pct_speed = (pct_chg - pct_chg.shift(2)) > 0.008
            pct_speed_flag = pct_speed.rolling(5).sum() > 0

            amt_cond = df['TotalValueTrade'].rolling(2).mean() / df['TotalValueTrade'].shift(2).rolling(10).mean()
            amt_cond = amt_cond > 1.2
            amt_flag = amt_cond.rolling(5).sum() > 0

            cond = pct_chg_flag.iloc[-1] & pct_speed_flag.iloc[-1] & amt_flag.iloc[-1]
            stk_list = cond[cond].index.tolist()

            for stk in stk_list:
                message = '=====龙头首阴监控=====\n' + \
                          '个股：%s\n' % MyUtil.get_tip_str(stk) + \
                          '拉升时间：%s' % DtUtil.get_standard_YmdHM()
                if stk not in has_send_message:
                    send_message([workmate_dict['冯炽']], message)
                    has_send_message.append(stk)
                    pprint(message)

            print('循环一轮消耗的时间为：%d，个股数量为：%d' % (time.time() - t1, len(self.daily_stock)))


if __name__ == '__main__':
    fc = FirstCloudy()
    fc.calc_daily_stock()
    print(fc.daily_stock)
    fc.start_intra()
