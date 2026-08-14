# coding: utf-8
# Author：fengchi863
# Date ：2021/4/9 9:59

from ShortTermTrading.dataApi import getData, stockList, tradeDate
from ShortTermTrading.conf.path_conf import dragon_monitor_path, man_made_concept_data_path
import pandas as pd, numpy as np
import time
from multiprocessing import Pool
from xquant.thirdpartydata.marketdata import MarketData
from ShortTermTrading.Util.tools import get_today_date, get_curr_datetime, \
    get_yesterday_date, get_stock_name
from ShortTermTrading.Util.System import workmate_dict
from ShortTermTrading.Util.tools import send_message
import datetime as dt

DEBUG = False
if DEBUG:
    workmate_list = [workmate_dict['冯炽']]
else:
    workmate_list = [workmate_dict['冯炽'],
                     workmate_dict['陈慧丽'],
                     workmate_dict['刘昌易'],
                     workmate_dict['陶鑫'],
                     workmate_dict['陆威玮'],
                     workmate_dict['邵柯楠']]

class DailyDragonMonitor:
    def __init__(self, monitor_address=None):
        # monitor_df = pd.read_excel(monitor_address)
        # self.duanban_dragon = monitor_df[monitor_df['Unnamed: 7'] == '断板龙头']['Unnamed: 0'].tolist()
        # self.lanban_dragon = monitor_df[monitor_df['Unnamed: 7'] == '烂板龙头']['Unnamed: 0'].tolist()
        # self.shouyin_dragon = monitor_df[monitor_df['Unnamed: 7'] == '龙头首阴']['Unnamed: 0'].tolist()

        self.duanban_dragon = [601127]
        self.lanban_dragon = [3043, 603721]
        self.shouyin_dragon = [600257]
        self.consis_dragon = [603518]
        self.duanban_dragon = list(map(stockList.trans_int2windcode, self.duanban_dragon))
        self.lanban_dragon = list(map(stockList.trans_int2windcode, self.lanban_dragon))
        self.shouyin_dragon = list(map(stockList.trans_int2windcode, self.shouyin_dragon))
        self.consis_dragon = list(map(stockList.trans_int2windcode, self.consis_dragon))

        man_made_df = pd.read_excel(man_made_concept_data_path)
        man_made_df = man_made_df[man_made_df['Unnamed: 0'] != 'A20132.SH']
        man_made_df['主题'] = man_made_df['概念板块'] + '_' + man_made_df['子主题']

        self.man_made_df = man_made_df


    def start_intra1(self, monitor_list):
        ma = MarketData()

        now_date = get_today_date()
        now_start_datetime = now_date * 1000000 + 90000
        now_end_datetime = now_date * 1000000 + 150000
        triggered_list = []  # 记录当天已经触发过的个股
        zt_triggered_list = [] # 记录当天已经触发过涨停的个股

        while True:
            now_mddatetime = get_curr_datetime()
            if now_mddatetime > 150000:
                break
            for stk_id in monitor_list:
                time.sleep(10)  # 防止频繁调用
                print('断板龙头弱转强')
                now_mddatetime = get_curr_datetime()
                now_datetime = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
                now_mdtime = str((now_mddatetime // 100) * 100000)  # 转成数据格式
                print('===========================================')
                print('当前时间：', now_mddatetime)
                if now_mddatetime < 93000: # 从9点30分开始
                    continue
                # 实时横截面数据
                df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
                df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
                cross_info = df1.append(df2)
                cross_info = cross_info.set_index('HTSCSecurityID', drop=True)

                stk_code = stockList.trans_int2windcode(stk_id)
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
                pre_close = cross_info.at[stk_code, 'PreClosePx']
                pctchg = md_kline_df['ClosePx'] / pre_close - 1
                now_pctchg = pctchg.iloc[-1]
                # 最近五分钟内存在过两分钟内涨速超过1.5%
                pctchg_2m = pctchg - pctchg.shift(2)
                pctchg_2m_judge = pctchg_2m > 0.015

                # 用于判断涨停
                minute_latest_info = md_kline_df.iloc[-1]
                latest_close_px = minute_latest_info['ClosePx']
                latest_pctchg = latest_close_px / pre_close - 1

                if now_pctchg > 0.03 and (stk_code not in triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                     ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('断板龙头弱转强')
                    message = '~~~~~~~~~\n' \
                              '断板龙头弱转强日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '弱转强时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    triggered_list.append(stk_code)
                if now_pctchg > -0.01 and pctchg_2m_judge.iloc[-5:-1].max() > 0 and \
                    (stk_code not in triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                            ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('断板龙头弱转强')
                    message = '~~~~~~~~~\n' \
                              '断板龙头弱转强监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '弱转强时间：%s\n' % now_mdtime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    triggered_list.append(stk_code)
                # 涨停监控
                if ((not stk_code.startswith('3')) and latest_pctchg > 0.098) | \
                        (stk_code.startswith('3') and latest_pctchg > 0.198):
                    if stk_code not in zt_triggered_list:
                        tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                         ma=ma, cross_info=cross_info)
                        tuples2str = self.parse_concept_ret(tuples)
                        print('断板龙头涨停')
                        message = '~~~~~~~~~\n' \
                                  '断板龙头涨停监控：\n' + \
                                  '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                                  '涨停时间：%s\n' % now_mdtime + \
                                  '所属主题以及涨跌幅：%s' % tuples2str
                        send_message(workmate_list, message)
                        zt_triggered_list.append(stk_code)

    # 烂板龙头弱转强的监控
    def start_intra2(self, monitor_list):
        ma = MarketData()

        now_date = get_today_date()
        now_start_datetime = now_date * 1000000 + 90000
        now_end_datetime = now_date * 1000000 + 150000
        triggered_list = []  # 记录当天已经触发过的个股
        zt_triggered_list = []

        while True:
            now_mddatetime = get_curr_datetime()
            if now_mddatetime > 150000:
                break
            for stk_id in monitor_list:
                time.sleep(10)  # 防止频繁调用
                print('烂板龙头弱转强')
                now_mddatetime = get_curr_datetime()
                now_datetime = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
                now_mdtime = str((now_mddatetime // 100) * 100000)  # 转成数据格式
                print('===========================================')
                print('当前时间：', now_mddatetime)
                if now_mddatetime < 93000: # 从9点30分开始
                    continue
                # 实时横截面数据
                df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
                df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
                cross_info = df1.append(df2)
                cross_info = cross_info.set_index('HTSCSecurityID', drop=True)

                stk_code = stockList.trans_int2windcode(stk_id)
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
                pre_close = cross_info.at[stk_code, 'PreClosePx']
                pctchg = md_kline_df['ClosePx'] / pre_close - 1
                now_pctchg = pctchg.iloc[-1]
                # 最近五分钟内存在过两分钟内涨速超过1.5%
                pctchg_2m = pctchg - pctchg.shift(2)
                pctchg_2m_judge = pctchg_2m > 0.015

                # 用于判断涨停
                minute_latest_info = md_kline_df.iloc[-1]
                latest_close_px = minute_latest_info['ClosePx']
                latest_pctchg = latest_close_px / pre_close - 1

                if now_pctchg > 0.03 and (stk_code not in triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                     ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('烂板龙头弱转强')
                    message = '~~~~~~~~~\n' + \
                              '烂板龙头弱转强日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '弱转强时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    triggered_list.append(stk_code)
                if now_pctchg > -0.01 and pctchg_2m_judge.iloc[-5:-1].max() > 0 and \
                        (stk_code not in triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                     ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('烂板龙头弱转强')
                    message = '~~~~~~~~~\n' + \
                              '烂板龙头弱转强日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '弱转强时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    triggered_list.append(stk_code)
                # 涨停监控
                if ((not stk_code.startswith('3')) and latest_pctchg > 0.098) | \
                        (stk_code.startswith('3') and latest_pctchg > 0.198):
                    if stk_code not in zt_triggered_list:
                        tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                         ma=ma, cross_info=cross_info)
                        tuples2str = self.parse_concept_ret(tuples)
                        print('烂板龙头涨停')
                        message = '~~~~~~~~~\n' + \
                                  '烂板龙头涨停日内监控：\n' + \
                                  '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                                  '涨停时间：%s\n' % now_datetime + \
                                  '所属主题以及涨跌幅：%s' % tuples2str
                        send_message(workmate_list, message)
                        zt_triggered_list.append(stk_code)

    # 龙头首阴的日内监控
    def start_intra3(self, monitor_list):
        ma = MarketData()

        now_date = get_today_date()
        now_start_datetime = now_date * 1000000 + 90000
        now_end_datetime = now_date * 1000000 + 150000
        triggered_list = []  # 记录当天已经触发过的个股
        zt_triggered_list = []
        speed_triggered_list = []

        while True:
            now_mddatetime = get_curr_datetime()
            if now_mddatetime > 150000:
                break
            for stk_id in monitor_list:
                time.sleep(10)  # 防止频繁调用
                print('龙头首阴日内监控')
                now_mddatetime = get_curr_datetime()
                now_datetime = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
                now_mdtime = str((now_mddatetime // 100) * 100000)  # 转成数据格式
                print('===========================================')
                print('当前时间：', now_mddatetime)
                if now_mddatetime < 93000:  # 从9点30分开始
                    continue
                # 实时横截面数据
                df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
                df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
                cross_info = df1.append(df2)
                cross_info = cross_info.set_index('HTSCSecurityID', drop=True)

                stk_code = stockList.trans_int2windcode(stk_id)
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
                pre_close = cross_info.at[stk_code, 'PreClosePx']
                pctchg = md_kline_df['ClosePx'] / pre_close - 1
                now_pctchg = pctchg.iloc[-1]

                # 最近五分钟内存在过两分钟内涨速超过1.5%
                pctchg_2m = pctchg - pctchg.shift(2)
                pctchg_2m_judge = pctchg_2m > 0.015

                # 用于判断涨停
                minute_latest_info = md_kline_df.iloc[-1]
                latest_close_px = minute_latest_info['ClosePx']
                latest_pctchg = latest_close_px / pre_close - 1

                # 首阴监控
                if now_pctchg < -0.01 and (stk_code not in triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                     ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('龙头首阴日内监控')
                    message = '~~~~~~~~~\n' + \
                              '龙头首阴日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '首阴时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    triggered_list.append(stk_code)

                # 拉升监控
                if pctchg_2m_judge.iloc[-5:-1].max() > 0 and (stk_code in triggered_list) and \
                    (stk_code not in speed_triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                     ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('龙头首阴快速拉升')
                    message = '~~~~~~~~~\n' + \
                              '龙头首阴快速拉升日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '拉升时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    speed_triggered_list.append(stk_code)

                # 涨停监控
                if (((not stk_code.startswith('3')) and (latest_pctchg > 0.098)) | \
                        (stk_code.startswith('3') and (latest_pctchg > 0.198))) and \
                        (stk_code in triggered_list) and (stk_code not in zt_triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                     ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('龙头首阴涨停')
                    message = '~~~~~~~~~\n' + \
                              '龙头首阴涨停日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '涨停时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    zt_triggered_list.append(stk_code)

    # 一致转分歧的盘中跟踪
    def start_intra4(self, monitor_list):
        ma = MarketData()

        now_date = get_today_date()
        now_start_datetime = now_date * 1000000 + 90000
        now_end_datetime = now_date * 1000000 + 150000
        triggered_list = []  # 记录当天已经触发过的个股
        zt_triggered_list = []

        last_6d = tradeDate.get_pre_trade_date(now_date, 5)
        last_1d = tradeDate.get_pre_trade_date(now_date, 1)
        last_5d_date_list = tradeDate.get_date_range(last_6d, last_1d)
        vol_last5d = getData.get_daily_1factor('volume', date_list=last_5d_date_list)

        while True:
            now_mddatetime = get_curr_datetime()
            if now_mddatetime > 150000:
                break
            for stk_id in monitor_list:
                time.sleep(10)  # 防止频繁调用
                print('一致转分歧日内监控')
                now_mddatetime = get_curr_datetime()
                now_datetime = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
                now_mdtime = str((now_mddatetime // 100) * 100000)  # 转成数据格式
                print('===========================================')
                print('当前时间：', now_mddatetime)
                if now_mddatetime < 93000: # 从9点30分开始
                    continue
                # 实时横截面数据
                df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
                df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
                cross_info = df1.append(df2)
                cross_info = cross_info.set_index('HTSCSecurityID', drop=True)

                stk_code = stockList.trans_int2windcode(stk_id)
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
                pre_close = cross_info.at[stk_code, 'PreClosePx']
                pctchg = md_kline_df['ClosePx'] / pre_close - 1
                now_pctchg = pctchg.iloc[-1]

                # 最近五分钟内存在过两分钟内涨速超过1.5%
                pctchg_2m = pctchg - pctchg.shift(2)
                pctchg_2m_judge = pctchg_2m > 0.015

                # 用于判断涨停
                minute_latest_info = md_kline_df.iloc[-1]
                latest_close_px = minute_latest_info['ClosePx']
                latest_pctchg = latest_close_px / pre_close - 1

                # 用于判断换手率
                total_vol = md_kline_df['TotalVolumeTrade'].sum() / 100
                vol_last5d_mean = vol_last5d.loc[:, stockList.trans_windcode2int(stk_id)].mean()

                # 成交量放大监控
                if total_vol > vol_last5d_mean * 2 and (stk_code not in triggered_list):
                    tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                         ma=ma, cross_info=cross_info)
                    tuples2str = self.parse_concept_ret(tuples)
                    print('一致转分歧放量')
                    message = '~~~~~~~~~\n' + \
                              '一致转分歧换手率放大日内监控：\n' + \
                              '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                              '时间：%s\n' % now_datetime + \
                              '所属主题以及涨跌幅：%s' % tuples2str
                    send_message(workmate_list, message)
                    triggered_list.append(stk_code)

                # 涨停监控
                if (((not stk_code.startswith('3')) and latest_pctchg > 0.098) | \
                        (stk_code.startswith('3') and latest_pctchg > 0.198)) and \
                        (stk_code in triggered_list) and (stk_code not in zt_triggered_list):
                    if stk_code not in zt_triggered_list:
                        tuples = self.get_concept_pctchg(stk_code, now_start_datetime, now_end_datetime,
                                                         ma=ma, cross_info=cross_info)
                        tuples2str = self.parse_concept_ret(tuples)
                        print('一致转分歧涨停')
                        message = '~~~~~~~~~\n' + \
                                  '一致转分歧涨停日内监控：\n' + \
                                  '个股：%s，%s\n' % (stk_code, get_stock_name(stk_code)) + \
                                  '涨停时间：%s\n' % now_datetime + \
                                  '所属主题以及涨跌幅：%s' % tuples2str
                        send_message(workmate_list, message)
                        zt_triggered_list.append(stk_code)

    def get_concept_pctchg(self, stk_code, start_datetime, end_datetime, ma=None, cross_info=None):
        ret = list()
        man_made_df = self.man_made_df.copy()
        if stk_code not in man_made_df['Unnamed: 0'].tolist():
            return ret
        sub_concept_list = man_made_df[man_made_df['Unnamed: 0'] == stk_code][
            '主题'].tolist()
        for sub_concept in sub_concept_list:
            sub_concept_pool = man_made_df[man_made_df['主题'] == sub_concept]
            sub_concept_stk_list = sub_concept_pool['Unnamed: 0'].tolist()

            # 开始计算主题内所有个股涨速
            pctchg_list = []
            pctchg_3m_list = []
            open_pctchg_list = []
            for sub_concept_stk_code in sub_concept_stk_list:
                sub_md_kline_df = ma.getMDSecurityKLineDataFrame(sub_concept_stk_code, str(start_datetime),
                                                                 str(end_datetime), 10, 20)
                pre_close = cross_info.at[stk_code, 'PreClosePx']
                pctchg = sub_md_kline_df['ClosePx'] / pre_close - 1
                open_pctchg_list.append(pctchg.iloc[0])
                pctchg_list.append(pctchg.iloc[-1])
                pctchg_3m = (pctchg - pctchg.shift(2)).iloc[-1]
                pctchg_3m_list.append(pctchg_3m)
            ret.append((sub_concept, np.mean(open_pctchg_list), np.mean(pctchg_list)))
        return ret

    def parse_concept_ret(self, tuples):
        ret_list = list()
        if len(tuples) == 0:
            return '无'
        for tuple in tuples:
            sub_concept, open_pctchg, pctchg = tuple
            ret_list.append(str(sub_concept + '(' + '%.2f' % (pctchg) + '%)'))
        return '，'.join(ret_list)

if __name__ == '__main__':
    yes_date = get_yesterday_date()
    if DEBUG:
        yes_date = 20210412
    ddm = DailyDragonMonitor(dragon_monitor_path + '涨停分类%d.xlsx' % yes_date)
    ddm.start_intra4(ddm.consis_dragon)
