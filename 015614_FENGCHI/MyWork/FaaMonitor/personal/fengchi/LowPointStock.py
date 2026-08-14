# coding: utf-8
# Author：fengchi863
# Date ：2021/5/26 19:17

'''
版本V1-20210607：
低位股盘中拉升半路低吸
日间刻画【符合条件的，在主题跟踪表中打下标签】：
1、T日处于160/140/120/100/80个交易日 价格区间的40%分位之下（交易日参数符合其中任意一个）【算法 吴雨璘有】
2、计算上述价格区间最低价，T日价格大于最低价
3、T-4至T日，每天涨跌幅>=-5%
4、T日均线距离  1-20均线距离<=0.1   【算法 吴雨璘有】

T+1日盘中：
1、主题中有个股涨停（分钟级别）
2、符合上述日间刻画的个股 且  条件1涨停时间前后30min个股出现过快速拉升(定义：2分钟涨速>=0.8%，且该2分钟的平均成交量>=前10分钟平均成交量的1.2倍 ) 且 当前时刻（推送提示的时间）个股绝对涨幅>=1%

9:10分以后执行，涨停数据9:10分更新
'''

import pandas as pd
from FaaMonitor.dataApi import getData
from FaaMonitor.dataApi import tradeDate
from FaaMonitor.dataApi import stockList
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.Util.MyUtil import MyUtil
from FaaMonitor.conf.path_conf import realtime_date_path, man_made_concept_data_path
from realtimeApi.getdata_from_open import data_prepare, get_oneconcept_alldata
from FaaMonitor.Util.tools import send_message
from FaaMonitor.Util.System import workmate_dict
from multiprocessing import Pool
import time
from pprint import pprint

class LowPointStock:
    def __init__(self):
        date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()
        shift_date = tradeDate.get_pre_trade_date(date, 160)
        date_list = tradeDate.get_date_range(shift_date, yes_date)
        daily_close = getData.get_daily_1factor('close',date_list=date_list)
        daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list)
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
        self.daily_pctchg = daily_pctchg
        self.daily_stock = None

    # 获取日间满足条件的股票
    def calc_daily_stock(self):
        inter_cond1_list = self.inter_cond1()
        inter_cond2_list = self.inter_cond2()
        inter_cond3_list = self.inter_cond3()
        inter_cond4_list = self.inter_cond4()
        self.daily_stock = sorted(list(set(inter_cond1_list).intersection(set(inter_cond2_list)).\
                                       intersection(inter_cond3_list).intersection(inter_cond4_list)))
        print('日间股票池已计算完成')

    # T日处于160/140/120/100/80个交易日 价格区间的40%分位之下（交易日参数符合其中任意一个）
    def inter_cond1(self):
        rank_pct_ret_80 = self.daily_close.iloc[-80:].apply(lambda x: self.ranks(x))
        rank_pct_ret_100 = self.daily_close.iloc[-100:].apply(lambda x: self.ranks(x))
        rank_pct_ret_120 = self.daily_close.iloc[-120:].apply(lambda x: self.ranks(x))
        rank_pct_ret_140 = self.daily_close.iloc[-140:].apply(lambda x: self.ranks(x))
        rank_pct_ret_160 = self.daily_close.iloc[-160:].apply(lambda x: self.ranks(x))
        stk_list_80 = rank_pct_ret_80[rank_pct_ret_80 < 0.4].index.tolist()
        stk_list_100 = rank_pct_ret_80[rank_pct_ret_100 < 0.4].index.tolist()
        stk_list_120 = rank_pct_ret_80[rank_pct_ret_120 < 0.4].index.tolist()
        stk_list_140 = rank_pct_ret_80[rank_pct_ret_140 < 0.4].index.tolist()
        stk_list_160 = rank_pct_ret_80[rank_pct_ret_160 < 0.4].index.tolist()
        stk_list = sorted(list(set(stk_list_80 + stk_list_100 + stk_list_120 + stk_list_140 + stk_list_160)))
        return stk_list

    def inter_cond2(self):
        low_price = self.daily_close.rolling(120).min()
        not_low = self.daily_close > low_price
        stk_list = not_low.iloc[-1][not_low.iloc[-1]].index.tolist()
        return stk_list

    def inter_cond3(self):
        cond = self.daily_pctchg <= -5
        cond = cond.rolling(4).sum() == 0
        stk_list = cond.iloc[-1][cond.iloc[-1]].index.tolist()
        return stk_list

    def inter_cond4(self):
        dis_20 = self.distance(self.daily_close, 20)
        return sorted(dis_20.loc[:, dis_20.iloc[-1] < 0.1].columns.tolist())

    def add_concept_stock(self):
        man_made_concept_df = pd.read_excel(man_made_concept_data_path)
        man_made_concept_df = man_made_concept_df.rename(columns={'Unnamed: 0': '股票代码'})
        man_made_concept_df['是否属于低位股'] = man_made_concept_df['股票代码'].apply(lambda x:
          True if stockList.trans_windcode2int(x) in self.daily_stock else False)
        # TODO: 加到了股票池里，下一步操作是什么？

    def add2excel(self, df):
        self.calc_daily_stock()
        df['低位股'] = df['股票代码'].apply(lambda x:
                        '是' if stockList.trans_windcode2int(x) in self.daily_stock else '否')
        return df

    def start_intra_monitor(self, concept_name):
        limitup_record = dict()
        has_send_message = list()
        while True:
            t1 = time.time()

            # 完善的退出机制
            if DtUtil.get_now_hm() > 1500:
                print('终于收盘了，辛劳的一天终于结束了，可以把资源释放出来了')
                break
            elif DtUtil.get_now_hm() < 930:
                continue

            realtime_data = get_oneconcept_alldata(concept_name=concept_name)
            last_px = realtime_data['ClosePx']
            amt = realtime_data['TotalValueTrade']

            # 二次检测，是否更新到了最新的时间
            if last_px.index[-1] != DtUtil.get_now_hm():
                print('%s板块实时界面数据有延迟，现在时间为%d，截面最新时间为%d' % (concept_name, DtUtil.get_now_hm(), last_px.index[-1]))

            last_px.columns = last_px.columns.map(stockList.trans_windcode2int) # 对股票代码作转换
            amt.columns = amt.columns.map(stockList.trans_windcode2int)
            stk_list = last_px.columns.tolist() # 该主题内股票池
            is_limitup = (last_px == self.cur_limitup.loc[stk_list])
            is_limitup_list = is_limitup.iloc[-1][is_limitup.iloc[-1]].index.tolist()
            for stk in is_limitup_list:
                if stk not in limitup_record.values():
                    limitup_record.update({DtUtil.get_now_hm(): stk})

            # 获取最新的涨停时间
            lastest_limitup_time = sorted(list(limitup_record.keys()))[-1]
            time_30 = DtUtil.get_pre_minute(lastest_limitup_time, -30)

            # 扫描前面有没有这样的拉升,并且直到到了那个时间为止，这样等于说是把前面30分钟的和后面30分钟都扫描了
            if DtUtil.get_now_hm() <= time_30:
                cond1 = (last_px / last_px.shift(2) - 1) > 0.08
                cond2 = amt.rolling(2).mean() / amt.shift(2).rolling(10).mean() > 1.2
                cond3 = (last_px / self.pre_close.loc[stk_list] - 1) > 0.01
                all_cond = (cond1 & cond2 & cond3).iloc[-30:].sum()
                alarm_list = all_cond[all_cond > 0].index.tolist()

            # 与日间低位个股做拼接
            alarm_list = sorted(list(set(alarm_list).intersection(set(self.daily_stock))))

            for stk in alarm_list:
                message = '==========\n' + \
                    '%s出现日内低吸机会' % MyUtil.get_tip_str(stk)
                if message not in has_send_message:
                    send_message([workmate_dict['冯炽']], message)
                    pprint(message)
                    has_send_message.append(message)

            print('循环一个主题消耗的时间为：', time.time() - t1)

    @staticmethod
    def distance(close, n):
        pre = close
        dis = pd.DataFrame(0, index=close.index, columns=close.columns)
        for i in range(1, n + 1):
            cur = close.rolling(i).mean()
            dis += abs(pre - cur) / pre
            pre = cur
        return dis

    @staticmethod
    def ranks(x):
        return pd.Series(x).rank(pct=True, axis=0).values[-1]

if __name__ == '__main__':
    lps = LowPointStock()
    lps.calc_daily_stock()
    lps.add_concept_stock()

    # 监控一个
    lps.start_intra_monitor('次新股')

    # 监控多个
    # concept_list = list()
    # pool = Pool(10) # 暂定用10个核
    # for concept in concept_list:
    #     pool.apply_async(lps.start_intra_monitor, concept)
    # pool.join()
    # pool.close()







