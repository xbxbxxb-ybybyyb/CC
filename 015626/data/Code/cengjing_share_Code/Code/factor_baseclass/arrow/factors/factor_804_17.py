from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 尾盘3分钟tran因子
class factor_804_17(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_804_17, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            tran = df['transaction'][stk]
            tran = tran[(tran.TradeType == 0) & (tran.TradePrice > 0)]
            tran['trade_no'] = tran['TradeSellNo']
            tran.loc[tran.TradeBSFlag == 1, 'trade_no'] = tran['TradeBuyNo']

            tran1 = tran[tran['dt'].dt.time >= datetime.time(14, 57)]
            tran2 = tran[tran['dt'].dt.time <= datetime.time(14, 56)]
            if len(tran1) == 0 or len(tran2) == 0:
                continue

            ret1 = tran1.iloc[-1]['TradePrice'] / tran2.iloc[-1]['TradePrice'] - 1

            flist = [ret1]

            tran1_amount = tran1.TradeMoney.sum()

            for k in [1, 2]:
                tran1_buy = tran1[tran1.TradeBSFlag == k]
                tran1_buy_amount = tran1_buy.TradeMoney.sum()
                fac_ba_ratio = tran1_buy_amount / tran1_amount

                unique_trade = tran1_buy.groupby('trade_no').TradeMoney.sum()
                big_amount = unique_trade[unique_trade >= 100000].sum() 
                small_amount = tran1_buy_amount - big_amount
                big_amount_ratio = big_amount / tran1_amount
                small_amount_ratio = small_amount / tran1_amount
                
                super_amount = unique_trade[unique_trade >= 1000000].sum()
                super_amount_ratio = super_amount / tran1_amount
                    
                flist = flist + [tran1_buy_amount, fac_ba_ratio, big_amount, small_amount, big_amount_ratio, small_amount_ratio, super_amount, super_amount_ratio]
            
            factor[stk] = flist         

        factor = pd.DataFrame(factor, index = [f'factor_804_{i}' for i in range(17)]).T

        return factor