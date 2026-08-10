from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 尾盘半小时tran因子
class factor_803_19(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_803_19, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            tran = df['transaction'][stk]
            tran = tran[(tran.TradeType == 0) & (tran.TradePrice > 0)]
            tran['trade_no'] = tran['TradeSellNo']
            tran.loc[tran.TradeBSFlag == 1, 'trade_no'] = tran['TradeBuyNo']

            tran1 = tran[tran['dt'].dt.time >= datetime.time(14, 30)]
            if len(tran1) == 0:
                continue

            openpx = tran1['TradePrice'].iloc[0]
            close = tran1['TradePrice'].iloc[-1]
            high = tran1['TradePrice'].max()
            low = tran1['TradePrice'].min()
            amplitude = (high - low) / low
            amplitude_adjust = amplitude * -1 if tran1['TradePrice'].idxmax() < tran1['TradePrice'].idxmin() else amplitude
            ret1 = close / openpx - 1
            ret2 = close / high - 1
            ret3 = close/ low - 1

            flist = [amplitude, amplitude_adjust, ret1, ret2, ret3]

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

                penetrate_num = (tran1_buy.groupby(['trade_no', 'TradePrice'])['TradeIndex'].count().reset_index().groupby('trade_no')['TradePrice'].count() - 1).sum()
                
                flist = flist + [tran1_buy_amount, fac_ba_ratio, big_amount, small_amount, big_amount_ratio, small_amount_ratio, penetrate_num]

            factor[stk] = flist         

        factor = pd.DataFrame(factor, index = [f'factor_803_{i}' for i in range(19)]).T

        return factor