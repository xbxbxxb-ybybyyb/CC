# @Time : 2020/7/15 11:13
# @Author : Zhichen Lu
# @File : UniversalStrategyDemo.py
import pandas as pd
from backtest.StrategyBackTest.StrategyBase import StrategyBases
import datetime
from dataApi.tradeDate import trans_int2datetime,trade_months
class StrategyDemo(StrategyBases):

    def __init__(self):
        super().__init__()
        self.signal = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/junkClassification/predict_signal_xgb_model_rise_down_zero_5min_v_whole_mkt_20200713.pkl')
        self.signal = self.signal[:242*60]
        self.signal.index = [datetime.datetime.strptime(str(x[0] * 10000 + x[1]),'%Y%m%d%H%M') for x in self.signal.index]

    def monthly_update(self,month):
        super().monthly_update(month)
        self.data['signal'] = self.signal.loc[:self.data['close'].index[-1]]


    def bar_handler(self,stk,date_time,status):
        date_time = str(date_time[0]*10000+date_time[1])
        # if date_time not in self.data['signal'].index:
        #     return [],status
        # if stk not in self.data['signal'].columns:
        #     return [],status
        # signal = self.data['signal'].loc[date_time,stk]
        print(date_time)
        return [],status

if __name__=="__main__":
    SD = StrategyDemo()
    SD.backtest(SD.signal.columns.tolist(),20170703,20191231)
