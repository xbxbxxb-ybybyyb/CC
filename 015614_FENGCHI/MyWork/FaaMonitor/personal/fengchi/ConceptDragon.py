# coding: utf-8
# Author：fengchi863
# Date ：2021/5/28 9:23

'''
版本V1-20210527：
主题龙头股 盘中拉升半路低吸
日间【人工筛选】
1、主题龙头
2、断板横盘震荡
日内
1、龙头快速放量拉升
定义：2分钟涨速>=0.8%，且该2分钟的平均成交量>=前10分钟平均成交量的1.2倍 且当前时刻（推送提示的时间）个股绝对涨幅>=1%
2、当前时刻前10分钟，主题存在其他个股出现上述拉升（推送出个股数量 代码名称）
'''

import pandas as pd
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

class ConceptDragon:
    def __init__(self):
        date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()
        shift_date = tradeDate.get_pre_trade_date(date, 160)
        date_list = tradeDate.get_date_range(shift_date, yes_date)
        daily_close = getData.get_daily_1factor('close', date_list=date_list)
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
        self.cur_limitup = cur_limitup
        self.pre_close = pre_close
        self.daily_stock = None
        self.concept_df = None
        self.cover_concept = None

    def fetch_daily_concept(self):
        # 获取每日人工定义的股票池，其中是主题龙头，并且断板横盘震荡
        concept_df = pd.read_excel(man_made_concept_data_path)
        concept_df = concept_df.rename(columns={'Unnamed: 0': '股票代码'})
        # TODO: 获取股票代码
        stk_list = list([601688])
        self.daily_stock = stk_list
        concept_df['主题'] = concept_df['概念板块'] + '_' + concept_df['子主题']
        self.concept_df = concept_df
        concept_df['今日是否覆盖'] = concept_df['股票代码'].apply(lambda x: True if \
          stockList.trans_windcode2int(x) in stk_list else False)
        cover_concept = concept_df[concept_df['今日是否覆盖']]['主题'].tolist()
        self.cover_concept = cover_concept

    def start_intra_monitor(self, concept_name):
        has_send_message = list()
        while True:
            t1 = time.time()

            # 完善的退出机制
            if DtUtil.get_now_hm() > 1500:
                print('终于收盘了，辛劳的一天终于结束了，可以把资源释放出来了')
                break
            elif DtUtil.get_now_hm() < 930:
                continue

            # 按照主题运行，这样能够获得最快的速度，否则要所有龙头的横截面数据（等效于全市场）更耗时
            realtime_data = get_oneconcept_alldata(concept_name=concept_name)
            last_px = realtime_data['ClosePx']
            amt = realtime_data['TotalValueTrade']
            last_px.columns = last_px.columns.map(stockList.trans_windcode2int)  # 对股票代码作转换
            amt.columns = amt.columns.map(stockList.trans_windcode2int)

            cond1 = (last_px / last_px.shift(2) - 1) > 0.08
            cond2 = amt.rolling(2).mean() / amt.shift(2).rolling(10).mean() > 1.2
            cond3 = (last_px / self.pre_close - 1) > 0.01

            all_cond = (cond1.iloc[-1] & cond2.iloc[-1] & cond3.iloc[-1])
            alarm_list = all_cond[all_cond].index.tolist()
            rockup_stk = sorted(set(alarm_list).intersection(set(self.daily_stock)))

            all_cond_before_10m = (cond1.iloc[-10:] & cond2.iloc[-10:] & cond3.iloc[-10:]).sum() > 0
            other_stk = all_cond_before_10m[all_cond_before_10m].index.tolist()
            for stk in rockup_stk:
                message = '=====主题龙头股盘中拉升半路低吸=====\n' + \
                          '个股：\n' % MyUtil.get_tip_str(stk) + \
                          '拉升时间：%s\n' % DtUtil.get_standard_YmdHM()
                tip_stk = other_stk.remove(rockup_stk)
                other_str = MyUtil.get_tip_str(tip_stk)
                message += '%s内其他拉升个股有：%s' % (concept_name, other_str)
                if message not in has_send_message:
                    send_message([workmate_dict['冯炽']], message)
                    has_send_message.append(message)
                    pprint(message)

            print('循环一个主题消耗的时间为：', time.time() - t1)

if __name__ == '__main__':
    cd = ConceptDragon()
    cd.fetch_daily_concept()
    cd.start_intra_monitor('次新股')

    # 监控多个
    # pool = Pool(10) # 暂定用10个核
    # for concept in cd.cover_concept:
    #     pool.apply_async(cd.start_intra_monitor, concept)
    # pool.join()
    # pool.close()
