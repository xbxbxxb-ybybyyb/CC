# coding: utf-8
# Author：fengchi863
# Date ：2022/7/2 18:46
'''
几个参数：
回落比例：threshold 0.99
'''

from dataApi import tradeDate, stockList, getData
# from ShortTermTrading.ConceptApi.ConceptApi import get_basic_values
from ShortTermTrading.path_conf import junk_path
from dataApi.sendInfo import send_file, send_message
from LucienUtil.StockUtil import StockUtil
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from datetime import datetime
import ftplib
import talib
import time


class DailyZhaBan:

    def __init__(self):
        today_date = tradeDate.get_today(dividing_point=15)
        date_list = tradeDate.get_date_range(20200730, today_date)[-10:]
        close_badj = getData.get_daily_1factor('close_badj', date_list=date_list)
        high_badj = getData.get_daily_1factor('high_badj', date_list=date_list)
        open_badj = getData.get_daily_1factor('open_badj', date_list=date_list)
        low_badj = getData.get_daily_1factor('low_badj', date_list=date_list)
        stock_pool = stockList.clean_stock_list(least_live_days=5,
                                                start_date=date_list[0],
                                                end_date=date_list[-1],
                                                trade_mode=True,
                                                no_pause=False,
                                                least_recover_days=1,
                                                no_pause_limit=0.5,
                                                no_pause_stats_days=0)

        self.today_date = today_date
        self.date_list = date_list
        self.str_date_list = list(map(str, date_list))
        self.close_badj = close_badj
        self.high_badj = high_badj
        self.open_badj = open_badj
        self.low_badj = low_badj
        self.stock_pool = stock_pool
        self.basic_data_path = '/data/group/800442/800319/Temporary_Data/RawData/BasicData/'

    def calc_daily_zhaban(self):
        zhaban_df = get_basic_values('Open_Board_stock', start_date=self.date_list[0],
                                     end_date=self.date_list[-1], read_path=self.basic_data_path)
        limit_max = get_basic_values('Limit_price', read_path=self.basic_data_path).loc[self.date_list[-1]]
        adjfactor = getData.get_daily_1factor('adjfactor',
                                              code_list=limit_max.index.tolist(),
                                              date_list=[self.date_list[-1]]).T[self.date_list[-1]]
        limit_max_badj = limit_max * adjfactor
        while (zhaban_df.index[-1] != self.date_list[-1]) or (zhaban_df.iloc[-1].sum() == 0):
            time.sleep(120)
            print('等待120秒再读取一次')
            zhaban_df = get_basic_values('Open_Board_stock', start_date=self.date_list[0], end_date=self.date_list[-1],
                                         read_path=self.basic_data_path)
            if datetime.now().hour > 20:
                send_message("炸板组合今日日期出现问题，或者无炸板个股")
                return

        stock_list = list(set(zhaban_df.columns.tolist()).intersection(
            set(self.stock_pool.columns.tolist())).intersection(
            set(self.open_badj.columns.tolist())))
        stock_list = [x for x in stock_list if x // 1000 != 688]

        # 参数上影线, 开盘价小于收盘价
        cond1 = (self.open_badj[stock_list] < self.close_badj[stock_list]) & \
                (zhaban_df[stock_list]) & self.stock_pool[stock_list] & (
                ((self.high_badj - self.close_badj) / (self.high_badj - self.low_badj))[stock_list] < 0.3)

        # 计算当天的炸板股
        zhaban_list = cond1.iloc[-1][cond1.iloc[-1]].index.tolist()
        zhaban_uplimit_time = []

        if len(zhaban_list) > 0:
            for stk in zhaban_list:
                limitup_price = limit_max.at[stk]
                limitup_price_badj = limit_max_badj.at[stk]
                min_factors = getData.get_minute_1stock(stk, start_datetime=self.date_list[-1] * 10000 + 925,
                                                        end_datetime=self.date_list[-1] * 10000 + 1500,
                                                        factor_list=['vol', 'amt', 'close', 'low'])
                zt_time = (min_factors['close'] == limitup_price).sum()
                # 涨停时间参数
                if zt_time >= 15:
                    if stk // 100000 == 3:
                        threshold = 0.98
                    else:
                        threshold = 0.99
                    # 价格参数
                    if (self.close_badj.at[self.date_list[-1], stk] < limitup_price_badj * threshold) and \
                            (self.close_badj.at[self.date_list[-1], stk] >= 5):
                        zhaban_uplimit_time.append(stk)

            if len(zhaban_uplimit_time) > 0:
                zhaban_list = [stockList.trans_int2windcode(x) for x in zhaban_uplimit_time]
                zhaban_excel = pd.DataFrame(index=zhaban_list)
                zhaban_excel['股票名称'] = zhaban_excel.index.map(StockUtil.get_1stock_name)
                zhaban_excel.index = zhaban_excel.index.map(stockList.trans_windcode2int)
                nextday = tradeDate.get_pre_trade_date(offset=-1)
                zhaban_excel.to_excel(junk_path + '炸板次日待触发表格%s.xlsx' % nextday)
                send_message("今日炸板股：%s" % ('，'.join(zhaban_excel['股票名称'].tolist())))
                send_file(junk_path + '炸板次日待触发表格%s.xlsx' % nextday)
            else:
                send_message("炸板组合生成完毕,日内涨停时间不够，不触发")
        else:
            send_message("今日无炸板股票")

    def calc_index_macd(self):
        s = FactorData()
        index_data = s.get_factor_value(
            "WIND_AIndexEODPrices",
            s_info_windcode=['399005.SZ', '399001.SZ', '000001.SH'],
            factors=['s_info_windcode', 'trade_dt', 's_dq_close', 's_dq_open', 's_dq_high', 's_dq_low', 's_dq_amount'],
            trade_dt=self.date_list
        )
        close_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE').loc[self.str_date_list]
        close_index.index = close_index.index.map(int)
        open_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_OPEN').loc[self.str_date_list]
        open_index.index = open_index.index.map(int)
        high_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_HIGH').loc[self.str_date_list]
        high_index.index = high_index.index.map(int)
        low_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_LOW').loc[self.str_date_list]
        low_index.index = low_index.index.map(int)
        ma5_index = close_index.rolling(5).mean() < close_index
        ma5_sum = ma5_index.sum(axis=1)
        a1, a2, a3 = talib.MACD(np.array(close_index['000001.SH']), fastperiod=12, slowperiod=26, signalperiod=9)
        macd = pd.Series(a3, index=self.date_list)

        index_signal = 0
        if (ma5_sum.at[self.date_list[-1]] >= 2) and (
                macd.at[self.date_list[-1]] > macd.at[self.date_list[-2]]):
            index_signal = 1

        if index_signal == 1:
            send_message(['015614'], "参考一下即可：大盘条件符合要求")
        else:
            send_message(['015614'], "参考一下即可：大盘条件不符合要求")

    @staticmethod
    def upload_excel(path, name):
        ftp = ftplib.FTP()
        ftp.encoding = 'gbk'
        ftp.connect('168.8.2.60')
        ftp.login(user='zsd', passwd='zsd')
        ftp.cwd('015614')
        fp = open(path, 'rb')
        buf_size = 1024
        ftp.storbinary("STOR {}".format(name), fp, buf_size)
        fp.close()
        ftp.quit()
        print('上传成功')


if __name__ == '__main__':
    # threshold = 0.99    # 回落比例
    dzb = DailyZhaBan()
    dzb.calc_daily_zhaban()
    dzb.calc_index_macd()
