import sys

'''
每天生成组合
'''
sys.path.append('/data/group/800442/800319/')
from dataApi import tradeDate, stockList, getData
from ShortTermTrading.ConceptApi.ConceptApi import get_basic_values
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import send_file, send_message
from FaaMonitor.Util.MyUtil import MyUtil
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from datetime import datetime, timedelta
import ftplib
import talib
import time

s = FactorData()


def upload_excel(path, name):
    ftp = ftplib.FTP()
    ftp.encoding = 'gbk'
    ftp.connect('168.8.2.60')
    ftp.login(user='zsd', passwd='zsd')
    ftp.cwd('015630')
    ftp.cwd('行业监控')
    fp = open(path, 'rb')
    buf_size = 1024
    ftp.storbinary("STOR {}".format(name), fp, buf_size)
    fp.close()
    ftp.quit()
    print('上传成功')


now = datetime.now()
if datetime.now().strftime("%H:%M:%S") < "16:30:00":
    now = now - timedelta(days=1)
today = now.year * 10000 + now.month * 100 + now.day
tradingdaysstr = s.tradingday(20200730, today)[-5:]
tradingdaysint = [int(x) for x in tradingdaysstr]
flag = 0
zhaban_df = get_basic_values('Open_Board_stock', start_date=tradingdaysint[0], end_date=tradingdaysint[-1],
                             read_path='/data/group/800442/800319/Temporary_Data/RawData/BasicData/')

while (zhaban_df.index[-1] != tradingdaysint[-1]) or (zhaban_df.iloc[-1].sum() == 0):
    time.sleep(60)
    zhaban_df = get_basic_values('Open_Board_stock', start_date=tradingdaysint[0], end_date=tradingdaysint[-1],
                                 read_path='/data/group/800442/800319/Temporary_Data/RawData/BasicData/')
    if datetime.now().hour > 20:
        if flag == 0:
            send_message(['015614'], "炸板组合今日日期出现问题,或者无炸板个股")
            flag = 1

close = getData.get_daily_1factor('close', date_list=tradingdaysint)
high = getData.get_daily_1factor('high', date_list=tradingdaysint)
opn = getData.get_daily_1factor('open', date_list=tradingdaysint)
low = getData.get_daily_1factor('low', date_list=tradingdaysint)
stocks = stockList.clean_stock_list(least_live_days=5, trade_mode=True, no_pause=False, least_recover_days=1,
                                    no_pause_limit=0.5, no_pause_stats_days=0)
stocklist = list(
    set(zhaban_df.columns.tolist()).intersection(set(stocks.columns.tolist())).intersection(set(opn.columns.tolist())))
stocklist = [x for x in stocklist if x // 1000 != 688]
stocklist.sort()
# 参数上影线
zhaban_final = (opn[stocklist] < close[stocklist]) & (zhaban_df[stocklist]) & stocks[stocklist] & (
            ((high - close) / (high - low))[stocklist] < 0.3)
limit_up_price = get_basic_values('Limit_price', read_path='/data/group/800442/800319/Temporary_Data/RawData/BasicData/').loc[tradingdaysint[-1]]

tradingdaysstr_index = s.tradingday(20200101, today)
tradingdaysint_index = [int(x) for x in tradingdaysstr_index]
zhaban_today = zhaban_final.loc[tradingdaysint[-1]]
index_data = s.get_factor_value(
    "WIND_AIndexEODPrices",
    s_info_windcode=['399005.SZ', '399001.SZ', '000001.SH'],
    factors=['s_info_windcode', 'trade_dt', 's_dq_close', 's_dq_open', 's_dq_high', 's_dq_low', 's_dq_amount'],
    trade_dt=tradingdaysstr_index
)
close_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE').loc[tradingdaysstr_index]
close_index.index = close_index.index.map(int)
open_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_OPEN').loc[tradingdaysstr_index]
open_index.index = open_index.index.map(int)
high_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_HIGH').loc[tradingdaysstr_index]
high_index.index = high_index.index.map(int)
low_index = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_LOW').loc[tradingdaysstr_index]
low_index.index = low_index.index.map(int)
ma5_index = close_index.rolling(5).mean() < close_index
ma5_sum = ma5_index.sum(axis=1)
a1, a2, a3 = talib.MACD(np.array(close_index['000001.SH']), fastperiod=12, slowperiod=26, signalperiod=9)
macd = pd.Series(a3, index=tradingdaysint_index)
# open_close = open_index < ((close_index.shift(1)) * 0.99)
# open_close_sum = open_close.sum(axis=1)

index_signal = 0
if (ma5_sum.at[tradingdaysint_index[-1]] >= 2) and (
        macd.at[tradingdaysint_index[-1]] > macd.at[tradingdaysint_index[-2]]):
    index_signal = 1

zhabanlist = zhaban_today[zhaban_today].index.tolist()
zhaban_uplimit_time = []
# 回落比例
threshold = 0.99

zhaban_origin_series = zhaban_df.iloc[-1].dropna()
zhaban_origin_list = zhaban_origin_series[zhaban_origin_series].index.tolist()
zhaban_origin_list = [stockList.trans_int2windcode(x) for x in zhaban_origin_list]
zhaban_origin_df = pd.DataFrame(index=zhaban_origin_list)
zhaban_origin_df['股票名称'] = zhaban_origin_df.index.map(MyUtil.get_1stock_name)


if len(zhabanlist) > 0:
    for stk in zhabanlist:
        limitupprice = limit_up_price.at[stk]
        min_factors = getData.get_minute_1stock(stk, start_datetime=tradingdaysint[-1] * 10000 + 925,
                                                end_datetime=tradingdaysint[-1] * 10000 + 1500,
                                                factor_list=['vol', 'amt', 'close', 'low'])
        zt_time = (min_factors['close'] == limitupprice).sum()
        # 涨停时间参数
        if zt_time >= 15:
            if stk // 100000 == 3:
                threshold = 0.98
            # 价格参数
            if (close.at[tradingdaysint[-1], stk] < limitupprice * threshold) and (
                    close.at[tradingdaysint[-1], stk] >= 5):
                zhaban_uplimit_time.append(stk)
    if len(zhaban_uplimit_time) > 0:
        zhabanlist = [stockList.trans_int2windcode(x) for x in zhaban_uplimit_time]
        zhaban_excel = pd.DataFrame(index=zhabanlist)
        zhaban_excel['股票名称'] =zhaban_excel.index.map(MyUtil.get_1stock_name)
        nextday = tradeDate.get_pre_trade_date(offset=-1)
        zhaban_excel.to_excel(junk_path + '炸板次日待触发表格%s.xlsx' % nextday)
        upload_excel(junk_path + '炸板次日待触发表格%s.xlsx' % nextday, '炸板次日待触发表格%s.xlsx' % nextday)
        send_message(['015614'], "炸板组合生成完毕")
        send_file(['015614'], junk_path + '炸板次日待触发表格%s.xlsx' % nextday)
    else:
        send_message(['015614'], "炸板组合生成完毕,日内涨停时间不够，不触发")
    if index_signal == 1:
        send_message(['015614'], "大盘条件符合要求")
    else:
        send_message(['015614'], "大盘条件不符合要求")
else:
    send_message(['015614'], "今日无炸板股票")

# 以下没用，看了下属于仿真上线的部分
# today_file = None
# yesterday_file = None
# vampire_file = pd.DataFrame(index=range(1000),columns=['证券代码','买入交易账户','卖出交易账户','买入证券数量','卖出证券数量'])
# n=0
# try:
#    today = tradeDate.get_pre_trade_date(offset=0)
#    yestoday_file = pd.read_excel('/data/user/015630/baochedan/炸板次日待触发表格%s.xlsx'%nextday)

# try:
#    nextday = tradeDate.get_pre_trade_date(offset=-1)
#    today_file = pd.read_excel('/data/user/015630/baochedan/炸板次日待触发表格%s.xlsx'%nextday)
#    today_file.columns = ['证券代码','股票名称']
#    for i in today_file.index:
#        vampire_file.at[i,'证券代码'] = today_file.at[i,'证券代码']
#        vampire_file.at[i,'买入交易账户'] = 201002
#        vampire_file.at[i,'卖出交易账户'] = 201002
#        vampire_file.at[i,'买入证券数量'] = 1000000
#        vampire_file.at[i,'卖出证券数量'] = 0
