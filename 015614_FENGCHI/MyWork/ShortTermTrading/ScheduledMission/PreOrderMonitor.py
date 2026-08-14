# coding: utf-8
# Author：fengchi863
# Date ：2021/1/21 14:33
'''
超预期竞价第二版：
区分了三类个股，其中高开和涨停的要超过三只
'''

from ShortTermTrading.Util.tools import *
from ShortTermTrading.dataApi import stockList
from ShortTermTrading.dataApi import getData
from xquant.thirdpartydata.marketdata import MarketData
from ShortTermTrading.conf.path_conf import man_made_concept_data_path, pre_order_monitor_path
import time
from tqdm import tqdm

class PreOrderMonitor:
    def __init__(self, date=None):
        if date is None:
            date = get_curr_datetime()
        monitor_concept_df = pd.read_excel(man_made_concept_data_path)
        monitor_concept_df = monitor_concept_df[monitor_concept_df['Unnamed: 0'] != 'A20132.SH']
        # 光伏除硅以外的其他子主题合并
        monitor_concept_df['主题'] = monitor_concept_df['概念板块'] + '_' + monitor_concept_df['子主题']
        monitor_concept_df['主题'] = monitor_concept_df['主题'].apply(lambda x: '光伏_其它' if (x.startswith('光伏')) and (x!='光伏_硅') else x)

        self.monitor_concept_df = monitor_concept_df
        self.has_send_concept = list()
        self.date = date

    def calc_monitor(self, concept):
        ma = MarketData()
        now_date = self.date
        now_start_datetime = now_date * 1000000 + 90000
        now_end_datetime = now_date * 1000000 + 150000
        if concept not in self.monitor_concept_df['主题'].tolist():
            return
        concept_stk_list = self.monitor_concept_df[self.monitor_concept_df['主题']==concept]['Unnamed: 0'].tolist()
        time.sleep(0.1)
        if self.date == get_today_date():
            df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
            df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
            cross_info = df1.append(df2)
            cross_info = cross_info.set_index('HTSCSecurityID', drop=True)
        else:
            cross_info = getData.get_daily_1factor('pre_close')

        cond1 = [] # 932涨幅涨速满足要求的个股
        cond2 = [] # 平开或小低开且涨速满足要求的个股，涨速大于千6
        cond3 = [] # 涨停的个股

        for stk_code in concept_stk_list:
            time.sleep(0.1)
            md_kline_df = ma.getMDSecurityKLineDataFrame(stk_code, str(now_start_datetime), \
                                                         str(now_end_datetime), 10, 20)
            if len(md_kline_df) == 0:
                continue

            minute925_info = md_kline_df.iloc[0]
            if len(md_kline_df) < 4:
                minute932_info = md_kline_df.iloc[-1]
            else:
                minute932_info = md_kline_df.iloc[3]
            if self.date == get_today_date():
                pre_close = cross_info.at[stk_code, 'PreClosePx']
            else:
                pre_close = cross_info.at[self.date, stockList.trans_windcode2int(stk_code)]
            open_close_px = minute925_info['ClosePx']
            close_px932 = minute932_info['ClosePx']
            pctchg925 = open_close_px / pre_close - 1
            pctchg932 = close_px932 / pre_close - 1
            md_minute_pctchg_speed = md_kline_df['ClosePx'].pct_change(1)
            if len(md_minute_pctchg_speed) < 4:
                md_minute_pctchg_speed_mean = md_minute_pctchg_speed.mean()
            else:
                md_minute_pctchg_speed_mean = md_minute_pctchg_speed.iloc[:4].mean()

            if pctchg925 >= -0.01 and md_minute_pctchg_speed_mean > 0.006:
                cond2.append(stk_code)
            if pctchg925 > 0.02 and pctchg932 >= 0.02 and md_minute_pctchg_speed_mean > 0.002:
                cond1.append(stk_code)
            if (not stk_code.startswith('3')) and pctchg932 > 0.098:
                cond3.append(stk_code)
            if stk_code.startswith('3') and pctchg932 > 0.198:
                cond3.append(stk_code)

        # 开始判断是否满足发送条件
        print('======================')
        cond2 = list(set(cond2).difference(set(cond1)))
        cond1 = list(map(lambda x: get_stock_name(x), cond1))
        cond2 = list(map(lambda x: get_stock_name(x), cond2))
        cond3 = list(map(lambda x: get_stock_name(x), cond3))

        print(concept, len(cond1), len(cond2), len(cond3))
        cond_all = list(set(cond1 + cond2 + cond3))
        cond_judge = list(set(cond1 + cond3))
        # if len(cond_all) >= 3:
        #     print(concept, '超预期竞价，满足的个股：', '，'.join(cond_all))
        #     message = '==========\n超预期竞价监控' + \
        #               '主题：%s\n' % concept + \
        #               '个股：' + ','.join(cond_all)
        #     send_message(['fengchi'], message)
        #     self.has_send_concept.append(concept)
        if len(cond_all) >= 3 and len(cond_judge) >= 2:
            print(concept, '超预期竞价，满足的个股：', '，'.join(cond_all))
            message = '==========\n超预期竞价监控' + \
                      '主题：%s\n' % concept + \
                      '高开个股：' + ','.join(cond1) + \
                      '\n低平开个股：' + ','.join(cond2) + \
                      '\n涨停个股：' + ','.join(cond3)
            # send_message(['fengchi', '003186', '011669', '011670', '015628', '015630', '003376', '015624'], message)
            send_message(['fengchi'], message)
            self.has_send_concept.append(concept)

    def start_intra(self, concept_list):
        # concept_list = ['快手_快手'] # 20210121 测试用
        for concept in tqdm(concept_list):
            self.calc_monitor(concept)
        if len(self.has_send_concept) == 0:
            message = '今日无超预期竞价主题'
            # send_message(['fengchi', '003186', '011669', '011670', '015628', '015630', '003376', '015624'], message)
            send_message(['fengchi'], message)

if __name__ == '__main__':
    pom = PreOrderMonitor(date=get_today_date())
    # concept_list = list(set(pom.monitor_concept_df['主题'].tolist()))
    concept_list_df = pd.read_excel(pre_order_monitor_path + '竞价超预期0402.xlsx')
    concept_list_df['主题'] = concept_list_df['概念板块'] + '_' + concept_list_df['子主题']
    concept_list = list(set(concept_list_df['主题'].tolist()))
    while(True):
        now_mdtime = get_curr_datetime()
        if now_mdtime > 93200:
            pom.start_intra(concept_list)
        break