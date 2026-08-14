import os
import sys

'''
参数寻优
'''
from tqdm import _monitor
# sys.path.append("/data/user/015630/pycharmproject/StrongStock/")
# sys.path.append("/data/user/015630/pycharmproject/StrongStock/StrongStockModel/")
# from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
# from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.StockStrategyBase import StockStrategyBase
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.UniverseEvaluation_zxf import UniverseEvaluation
sys.path.append('/data/group/800442/800319/')
# sys.path.append('/data/group/800442/800319/Daily_ConCept/')
from dataApi import tradeDate, stockList, dividend, indName, getData
from ShortTermTrading.ConceptApi.ConceptApi import get_basic_values

from xquant.factordata import FactorData
import pandas as pd
import numpy as np
import time
# import talib
from datetime import datetime, timedelta
import requests
import json

s = FactorData()

# pickle_path = '/data/group/800442/800319/Faamonitor/factors/zxf/wvad_30/'

def send_file(users, file):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.7.124.15:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']

    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)
class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        # self.signal = pd.read_pickle('/data/user/015630/factors/kdj_30/%s.pkl'%stk)
        if self.market_flow is None:
            return

        self.last_buy_time = None
        self.last_buy_price = None
        self.stock = stk

    def daily_update(self):
        self.min_factors = getData.get_minute_1stock(self.stock, start_datetime=self.trading_day * 10000 + 925,
                                                     end_datetime=self.trading_day * 10000 + 1500,
                                                     factor_list=['vol', 'amt', 'close', 'low', 'high'])
        self.min_factors['amt_cumsum'] = self.min_factors['amt'].cumsum()
        self.min_factors['vol_cumsum'] = self.min_factors['vol'].cumsum()
        self.min_factors['speed'] = self.min_factors['close'].pct_change(2)
        self.min_factors['liangbi'] = self.min_factors['vol'].rolling(2).sum() / self.min_factors['vol'].rolling(
            10).sum()
        self.min_factors['vwap'] = self.min_factors['amt'] / self.min_factors['vol']
        self.min_factors['yellow_vwap'] = self.min_factors['amt_cumsum'] / self.min_factors['vol_cumsum']
        self.min_factors['close_up_vwap'] = (self.min_factors['close'] / self.min_factors['vwap']) > 1
        self.min_factors['length'] = np.arange(242) + 1
        self.min_factors['close_up_vwap_ratio'] = self.min_factors['close_up_vwap'].cumsum() / self.min_factors[
            'length']
        self.min_factors['maxdrawdown'] = (1 - self.min_factors['close'] / self.min_factors['close'].cummax()).cummax()
        self.min_factors['cummax'] = self.min_factors['high'].cummax()
        self.min_factors['cummin'] = self.min_factors['low'].cummin()
        self.sell_flag = 0

        return

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义

        if (self.position['available'] > 0):
            if self.min_factors.at[self.datetime, 'close'] > self.pre_close:
                if self.min_factors.at[self.datetime, 'maxdrawdown'] > 0.035:
                    self.sell()
                    self.sell_flag = 1
        if (self.position['available'] > 0) and (self.datetime[1] > 1450):
            if self.min_factors.at[self.datetime, 'close'] < (
                    np.floor(self.pre_close * 1.1 * 100 + 0.5) / 100 - 0.0001):
                self.sell()
                self.sell_flag = 1
        if (self.position['available'] > 0):
            if self.datetime[1] >= 930:
                if self.min_factors.at[self.datetime, 'close'] < (self.pre_close * 0.94):
                    self.sell()
                    self.sell_flag = 1
        if (self.position['available'] > 0) and (self.datetime[1] > 1450):
            if self.min_factors.at[self.datetime, 'close'] < (
                    self.min_factors.at[(self.trading_day, 925), 'close'] * 0.94):
                self.sell()
                self.sell_flag = 1

        if (self.sell_flag == 0) and (self.position['holding'] == 0) and (
                self.min_factors.at[(self.trading_day, 925), 'close'] / self.pre_close > 0.94):
            if self.datetime[1] >= 930:             
                self.buy()


def send_message(users, msg):
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)


def get_share_data(date_range):
    close = getData.get_daily_1factor('close', date_list=date_range)
    high = getData.get_daily_1factor('high', date_list=date_range)
    opn = getData.get_daily_1factor('open', date_list=date_range)
    low = getData.get_daily_1factor('low', date_list=date_range)
    preclose = getData.get_daily_1factor('pre_close', date_list=date_range)[close.columns]
    limit_up_price = get_basic_values('Limit_price').loc[date_range]
    return close, high, opn, low, preclose, limit_up_price


def zhaban_select(tradingdaysint, opn, close, limit_up_price):
    zhaban_origin = (get_basic_values('Open_Board_stock').loc[tradingdaysint])
    stocks = stockList.clean_stock_list(least_live_days=5, trade_mode=True, no_pause=False, least_recover_days=1,
                                        no_pause_limit=0.5, no_pause_stats_days=0)
    stocklist = list(set(zhaban_origin.columns.tolist()).intersection(set(stocks.columns.tolist())).intersection(
        set(opn.columns.tolist())).intersection(set(limit_up_price.columns.tolist())))
    stocklist = [x for x in stocklist if x // 1000 != 688]
    stocklist.sort()
    zhaban_origin = zhaban_origin[stocklist] & stocks.loc[zhaban_origin.index, stocklist]
    zhaban = zhaban_origin & (opn[stocklist] < close[stocklist])
    return zhaban, stocklist


def zhaban_time(zhaban, time, tradingdaysint, stocklist):
    close_min = getData.get_minute_1factor('close', start_datetime=tradingdaysint[0] * 10000 + 925,
                                           end_datetime=tradingdaysint[-1] * 10000 + 1500)
    stocklist_inner = list(set(close_min.columns.tolist()).intersection(set(stocklist)))
    stocklist_inner.sort()
    zhaban = zhaban[stocklist_inner]
    limit_up_price = (get_basic_values('Limit_price').loc[tradingdaysint, stocklist_inner])
    close_min = close_min[stocklist_inner]
    limit_up_price_min = pd.DataFrame(np.array(limit_up_price.loc[close_min.index.get_level_values('date')]),
                                      index=close_min.index, columns=limit_up_price.columns)
    zt_match = limit_up_price_min == close_min
    zt_time_sum = zt_match.reset_index().drop('time', axis=1).groupby('date').sum()
    zt_time = zt_time_sum > time
    zhaban_zt_time = zhaban & zt_time
    return zhaban_zt_time


def syx_select(zhaban, high, close, low, ratio, stocklist):
    temp = ((high[stocklist] - close[stocklist]) / (high[stocklist] - low[stocklist])) < ratio
    return zhaban & temp


def limit_select(zhaban, ratio, close, limit_up_price, stocklist):
    temp = close[stocklist] < (limit_up_price[stocklist] * ratio)
    return zhaban & temp

def price_select(zhaban,close,price,stocklist):
    return  zhaban& (close[stocklist] >= price)

def backtest(qiangshigu, date_range, output_path,n):
    qiangshigu.index = qiangshigu.index.map(lambda x: int(x))
    qiangshigu = (qiangshigu.shift(1).fillna(0)).astype(bool)

    is_valid = qiangshigu
    stk_list = qiangshigu.columns.tolist()
    stk_list = [x for x in stk_list if x // 1000 != 688]
    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=is_valid)
    #e = time.time()
    print('强势股回测开始:',n)

    strats.one_wave_run(stk_list, date_range[0], date_range[-1], kernel=10, output_path=output_path, mode='multi')
    #print('strategy time:', time.time() - e)
    #send_message(['015630'], '表格名字%s' % output_path)
    return output_path


if __name__ == '__main__':
    now = datetime.now()
    if datetime.now().strftime("%H:%M:%S") < "15:00:00":
        now = now - timedelta(days=1)
    today = now.year * 10000 + now.month * 100 + now.day
    index_date_rangestr = s.tradingday(20190101, today)[-500:-5]
    index_date_rangeint = [int(x) for x in index_date_rangestr]
    #####你需要多少天的历史数据
    backtest_date_rangestr = s.tradingday(20190101, today)[-200:-5]
    backtest_date_rangeint = [int(x) for x in backtest_date_rangestr]

    syx_ratio_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    limit_ratio_list = [0.95, 0.96, 0.97, 0.98, 0.99]
    time_list = [1, 5, 10, 15, 20]
    price_list = [5,10,15]
    backtest_date = backtest_date_rangeint
    close, high, opn, low, preclose, limit_up_price = get_share_data(backtest_date)
    zhaban_origin, stocklist = zhaban_select(backtest_date, opn, close, limit_up_price)
    length = len(syx_ratio_list) * len(limit_ratio_list) * len(time_list)*len(price_list)
    params_df = pd.DataFrame(index=range(length),
                             columns=['上影线比例', '回落限制比例','价格下限', '涨停时间', '收益率', '胜率', '日胜率', '盈亏比', '触发数量'])
    n = 0
    for syx_ratio in syx_ratio_list:
        zhaban_syx = syx_select(zhaban_origin, high, close, low, syx_ratio, stocklist)
        if zhaban_syx.sum().sum() == 0:
            continue
        for limit_ratio in limit_ratio_list:
            zhaban_limit = limit_select(zhaban_syx, limit_ratio, close, limit_up_price, stocklist)
            for price in price_list:
                zhaban_limit = price_select(zhaban_limit,close,price,stocklist)
                if zhaban_limit.sum().sum() == 0:
                    continue
                for t in time_list:
                    zhaban_zt_time = zhaban_time(zhaban_limit, t, backtest_date, stocklist)
                    if zhaban_zt_time.sum().sum() == 0:
                        continue
                    now = datetime.now().strftime("%Y%m%d%H%M")
                    output_path = '/data/group/800442/800319/Faamonitor/zhaban_xunyou_syx_zt_time_%s.xlsx' % now
                    try:
                        backtest(zhaban_zt_time, backtest_date, output_path,n)
                    except:
                        print('output error')
                    if os.path.exists(output_path):
                        try:
                            params_df.at[n, '上影线比例'] = syx_ratio
                            params_df.at[n, '回落限制比例'] = limit_ratio
                            params_df.at[n, '价格下限'] = price
                            params_df.at[n, '涨停时间'] = t
                            result_excel1 = pd.read_excel(output_path, index_col=0, sheet_name='逐笔持仓综合统计')
                            params_df.at[n, '收益率'] = result_excel1.at['收益率', '全时段']
                            params_df.at[n, '胜率'] = result_excel1.at['胜率', '全时段']
                            params_df.at[n, '盈亏比'] = result_excel1.at['盈亏比(收益率)', '全时段']
                            params_df.at[n, '触发数量'] = result_excel1.at['交易次数', '全时段'] / 2
                            result_excel2 = pd.read_excel(output_path, index_col=0, sheet_name='持仓综合统计')
                            params_df.at[n, '日胜率'] = result_excel2.at['日胜率', '全时段']
                            #send_message(['015630'], '第%s组参数测试完成' % n)
                            # os.remove('/data/group/800442/800319/Faamonitor/zhaban_xunyou_syx_zt_time_%s.xlsx' % now)
                        except:
                            send_message(['015614'], '%s有问题,上影线比例为%s,回落限制比例为%s,价格下限为%s,涨停时间为%s,'%(output_path,syx_ratio,limit_ratio,price,t))
                    else:
                        send_message(['015614'], '程序出错啦,表格输出失败')
                    n += 1
    params_df.to_excel('/data/group/800442/800319/Faamonitor/上影线参数更新列表%s.xlsx' % backtest_date_rangestr[-1])
    send_file(['015614'], '/data/group/800442/800319/Faamonitor/上影线参数更新列表%s.xlsx' % backtest_date_rangestr[-1])