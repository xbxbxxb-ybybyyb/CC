import pandas as pd
import numpy as np
from StrategyBase import *
import datetime
import DataFlowInfo
import Broker
from xquant.marketdata import MarketData
from xquant.factordata import FactorData
import time
import os
s = FactorData()
mdp = MarketData()
root_path = '/data/group/800319/junkData/'

class MA_strategy(StrategyBase):
    def __init__(self,start:int,end:int,initial_cash:float,universe:list,MA_df:pd.DataFrame,\
                 trading_percent:float, benchmark='ZZ500',cost_rate = 0.0012, slippage=0.001):
        super().__init__(start,end,initial_cash,universe,benchmark,cost_rate)
        self.MA = MA_df
        self.universe = MA_df.columns.tolist()
        self.trading_percent_per_stk = trading_percent/len(self.universe)


    def bar_handle(self,date_time,position):
        if date_time not in self.MA.index:
            return []
        order_list = []
        temp_close = self.broker.dataflow.data.loc[:, date_time, 'close']
        temp_target_vol = (position.cash * self.trading_percent_per_stk / temp_close).apply(lambda x: 100 * int(x / 100) if not np.isnan(x) else x)
        MA_rank = self.MA.loc[date_time,self.available_stk].dropna().sort_values()
        MA = pd.concat([pd.Series(1,MA_rank.index[:50]),pd.Series(-1,MA_rank.index[-50:])])
        for stk in MA.index:
            if MA[stk] == 1:
                if stk in self.position.holding:
                    if self.position.holding[stk]>0:
                        continue
                flag = 'B'
                target_vol = temp_target_vol[stk]
                target_vol = int(target_vol/100)*100
                if target_vol<100:
                    continue
            elif MA[stk] == -1:
                if stk not in self.position.holding:
                    continue
                if stk not in self.position.tradable_holding:
                    continue
                if self.position.tradable_holding[stk] == 0:
                    continue
                flag = 'S'
                target_vol = self.position.tradable_holding[stk]
            else:
                continue
            if np.isnan(np.isnan(target_vol)):
                continue
            order_list.append((date_time,stk,target_vol,temp_close[stk],flag))#(date_time,stk_id,stk_num,price)
        return order_list

    def daily_update(self,date):
        super().daily_update(date)


    def run_strategy(self):
        return super().run_strategy(self.bar_handle)

def test():
    factor = pd.read_pickle('/data/group/800319/junkData/temp_daily_by_lzc/MA_factor_values.pkl')
    factor = factor
    strategy = MA_strategy(20160401, 20160630, 1000000, factor.columns.tolist(), factor, 0.4)
    record, result = strategy.run_strategy()
    print(strategy.evaluation_result)
    print(strategy.running_time)
    strategy.output_result(root_path + 'temp_daily_by_lzc/', 'MA_result')
    pd.to_pickle(record, '%s/temp_daily_by_lzc/MA_record.pkl' % root_path)
if __name__=="__main__":
    test()
"""
# 开发用数据初始化
stk_list = set([])
date_list = s.tradingday(20191201,20191231,frequency='DAY', dayType=None, dateType='TRADINGDAYS')
for date in date_list:
    hs300_stk_list = s.hset('INDEX',str(date),'HS300')
    stk_list = stk_list | set(hs300_stk_list['stock'])

for stk in stk_list:
    temp_Klines =  mdp.get_data_by_year_month("Kline1M4ZT", stk, "201912")
    temp_Klines['datetime'] =( temp_Klines['MDDate'].astype(str) +\
                              temp_Klines['MDTime'].astype(str)).apply(lambda x : x[:12]).astype(int)
    temp_Klines = temp_Klines.drop(['MDDate','MDTime'],axis=1).set_index('datetime')
    pd.to_pickle(temp_Klines,'%s/MarketData/Minutes/%d.pkl'%(root_path,int(stk[:-3])))
    print(int(stk[:-3]))
"""



# os.mkdir('%s/MarketData/Tick/'%root_path)
"""
#test for DataFlow

e = time.time()
hs300_stk_list = s.hset('INDEX',str(20191203),'HS300')
hs300_stk_list = hs300_stk_list['stock'].apply(lambda x : int(x[:-3]))
dataflow = DataFlowInfo.DataFlowInfo(20191203,hs300_stk_list)
dataflow.update_date(20191204)
print(time.time()-e)
print('end')
"""



