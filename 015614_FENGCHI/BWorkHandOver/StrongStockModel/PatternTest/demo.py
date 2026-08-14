# import sys
#
# sys.path.append('/data/user/015628/')
# sys.path.append('/data/user/015628/suibianba/')
# sys.path.append('/data/user/015628/suibianba/StrongStockModel/')
# from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
# import pandas as pd
# import numpy as np
# import time
# from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
# import os
# from dataApi import tradeDate, stockList, dividend, indName, getData
#
#
# class StockStrategyDemo(StockStrategyBase):
#
#     def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
#                  isin_pool_flag=None):
#         super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
#                          isin_pool_flag)
#         # self.signal = pd.read_pickle('/data/user/015630/factors/kdj_30/%s.pkl'%stk)
#         self.signal = pd.read_pickle('/data/group/800319/Faamonitor/factors/ac_30_2/%s.pkl' % stk).loc[
#                       start_date:end_date]
#         # signal = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_2018all_mkt_origin_nodrop_factor_20200706/%d.pkl' % stk)
#         # if len(signal) == 2:
#         #     self.signal = signal[0]
#         # else:
#         #     self.signal = None
#         self.stock = stk
#
#     def daily_update(self):
#         # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
#         # 每天额外更新数据
#         if self.trading_day in self.signal.index:
#             self.dataflow['signal'] = self.signal.loc[(self.trading_day, 925):(self.trading_day, 1500)]
#         else:
#             self.dataflow['signal'] = None
#
#     def bar_handler(self):
#         # 每只股票每分钟信号逻辑定义
#
#         if self.dataflow['signal'] is None:
#             return
#         # self.datetime (20170103,930)
#         if not self.datetime in self.dataflow['signal'].index:
#             return
#
#         signal = self.dataflow['signal'].at[self.datetime, 'prediction']
#         if signal == 1 and self.position['holding'] == 0:
#             # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
#             self.buy()
#         if signal == -1 and self.position['available'] > 0:
#             # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
#             self.sell()
#
#
# def main2():
#     """
#     示例2：一波全回测评估并输出
#     :return:
#     """
#     qiangshigu = pd.read_pickle('/data/group/800319/Faamonitor/强势个股2014-2019.pkl')
#     qiangshigu.index = qiangshigu.index.map(lambda x: int(x))
#     qiangshigu.columns = qiangshigu.columns.map(lambda x: stockList.trans_windcode2int(x))
#     qiangshigu = (qiangshigu.shift(1).fillna(0)).astype(bool)
#     qiangshigu = qiangshigu.astype(int).replace(0, np.nan).dropna(how='all', axis=1).replace(np.nan, 0).astype(bool)
#
#     # file_list = os.listdir('/data/user/015630/factors/kdj_30/')
#     file_list = os.listdir('/data/group/800319/Faamonitor/factors/ac_30_2/')
#     file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
#     stk_list = [int(x.strip('.pkl')) for x in file_list]
#
#     strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=qiangshigu)
#     #    strats1 = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=yaogu)
#
#     # strats.backtest_one_stock(2989, 20130101, 20191231)
#     e = time.time()
#     # 并行回测
#     output_path = '/data/user/015628/市场监控/固定交易模式选股/ta_index/backtest/ac_30_2_qsg_v2.xlsx'
#     #    output_path1 = '/data/user/015628/市场监控/固定交易模式选股/ta_index/backtest/cci_30_2_yg.xlsx'
#     strats.one_stk_wraper(300364,20140101,20181231)
#     # strats.one_wave_run(stk_list, 20140101, 20181231, kernel=24, output_path=output_path, mode='multi')
#     #    strats1.one_wave_run(stk_list, 20140101, 20181231, kernel=24, output_path=output_path1, mode='multi')
#
#     # pd.to_pickle(strats.record._getvalue(), '/data/group/800319/Faamonitor/factors/record_zxf_code_excute_by_lzc.pkl')
#     # strats.one_wave_run(stk_list, 20100101, 20200728, kernel=10, output_path='/data/group/800319/Faamonitor/kdj_result_multi.xlsx', mode='multi')
#     print('strategy time:', time.time() - e)
#     # print(output_path1)
#
#
# if __name__ == "__main__":
#     # main_check()
#     main2()
from xquant.thirdpartydata.marketdata import MarketData as Market3Data
from xquant.factordata import FactorData
from functools import reduce
import pandas as pd
from decimal import Decimal
import requests
import json
import time
from datetime import datetime, timedelta

m3d = Market3Data()
s = FactorData()

now = datetime.now()
if datetime.now().strftime("%H:%M:%S") < "15:30:00":
    now = now - timedelta(days=1)
today = now.year * 10000 + now.month * 100 + now.day
trading_day = s.tradingday(20160104, today)

zuhe = pd.read_excel('/data/user/015630/baochedan/持仓/组合跟踪/收益跟踪%s.xlsx' % trading_day[-1],index_col=0)
zuhe_clean = zuhe[zuhe['次日持仓'] >= 100]
sw2 = s.hsi(zuhe_clean.index.tolist(), trading_day[-1], 'SW', 2).set_index('stock')

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


send_message([ '015630', '015628','003186','016385'], '盘中监控开始啦!')
users_check = ['015630', '015628','003186','016385']
users = ['hanxu', '015630', '011670', '003376', '003186', '011669']

monitor = pd.DataFrame(index=zuhe_clean.index)
monitor['证券名称'] = zuhe_clean.loc[monitor.index, '证券名称']
monitor['持仓'] = zuhe_clean.loc[monitor.index, '次日持仓']
monitor['申万二级行业'] = sw2.loc[monitor.index, 'industry_name']
monitor['成本'] = zuhe_clean.loc[monitor.index, '当前成本']
monitor['flag4'] = True
monitor['flag4_5'] = True
monitor['flag5'] = True

while time.gmtime()[3] < 7:

    t = time.time()

    df = pd.concat([m3d.getMDSecurityRecordBySourceTypes(securityIDSource=101),
                    m3d.getMDSecurityRecordBySourceTypes(securityIDSource=102)]).iloc[:, [0, 5, 8, 9, 10]]
    df.columns = ['code', 'close', 'high', 'low', 'pre_close']
    df = df.set_index('code')
    df = df[df['pre_close'] > 0.1]

    monitor['close'] = df.loc[monitor.index,'close']
    monitor['pct'] = monitor['close'] * monitor['持仓'] / monitor['成本'] - 1
    for i in monitor.index:
        if -0.045 < monitor.loc[i,'pct'] <= -0.04 and monitor.loc[i, 'flag4']:
            message =time.strftime("%H:%M:%S", time.localtime())+ ' %s, %s, %s, 距离成本%s' % (i, monitor.loc[i, '证券名称'], monitor.loc[i,'申万二级行业'], str(round(monitor.loc[i, 'pct']*100,2))+'%')
            send_message(users_check, message)
            print(message)
            monitor.loc[i, 'flag4'] = False
        elif -0.05 < monitor.loc[i,'pct'] < -0.045 and monitor.loc[i, 'flag4_5']:
            message =time.strftime("%H:%M:%S", time.localtime())+ ' %s, %s, %s, 距离成本%s' % (i, monitor.loc[i, '证券名称'], monitor.loc[i,'申万二级行业'], str(round(monitor.loc[i, 'pct']*100,2))+'%')
            send_message(users_check, message)
            monitor.loc[i, 'flag4_5'] = False
            print(message)
        elif monitor.loc[i,'pct'] <= -0.05 and monitor.loc[i, 'flag5']:
            message =time.strftime("%H:%M:%S", time.localtime())+ ' %s, %s, %s, 距离成本%s' % (i, monitor.loc[i, '证券名称'], monitor.loc[i,'申万二级行业'], str(round(monitor.loc[i, 'pct']*100,2))+'%')
            send_message(users_check, message)
            monitor.loc[i, 'flag5'] = False
            print(message)



