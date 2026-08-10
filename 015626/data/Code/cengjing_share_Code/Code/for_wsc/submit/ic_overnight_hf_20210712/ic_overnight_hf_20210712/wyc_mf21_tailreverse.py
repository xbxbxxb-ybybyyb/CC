from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf21_tailreverse(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        required_columns=['BuyTradeMoney_500','SellTradeMoney_500','close_spot']
        lookback_bars=2000
        super(wyc_mf21_tailreverse, self).__init__(*args, required_columns=required_columns,
                                  lookback_bars=lookback_bars, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        # 14点前下跌，14点后反转，14点后资金净流入。或14点前上涨，14点后不下跌，14点后资金净流入。
        close_spot3 = df['close_spot']
        close_spot_pm = close_spot3.loc[close_spot3.index.time == datetime.time(14,49)]
        close_spot_14 = close_spot3.loc[close_spot3.index.time == datetime.time(14,0)]
        close_spot_am = close_spot3.loc[close_spot3.index.time == datetime.time(9,30)]
        close_spot_ret1 = close_spot_14.groupby(close_spot_14.index.date).sum() / close_spot_am.groupby(close_spot_am.index.date).sum() - 1
        close_spot_ret2 = close_spot_pm.groupby(close_spot_pm.index.date).sum() / close_spot_14.groupby(close_spot_14.index.date).sum() - 1


        BuyTradeMoney_500 = df['BuyTradeMoney_500']
        SellTradeMoney_500 = df['SellTradeMoney_500']

        BuyTradeMoney_500 = BuyTradeMoney_500.loc[(BuyTradeMoney_500.index.time >= datetime.time(14,0)) & (BuyTradeMoney_500.index.time <= datetime.time(14,49))]
        SellTradeMoney_500 = SellTradeMoney_500.loc[(SellTradeMoney_500.index.time >= datetime.time(14,0)) & (SellTradeMoney_500.index.time <= datetime.time(14,49))]

        netmoney = BuyTradeMoney_500 - SellTradeMoney_500
        netmoney = netmoney.sum(axis = 1).groupby(netmoney.index.date).sum()
        
        close_spot_ret1 = close_spot_ret1.to_frame()
        close_spot_ret2 = close_spot_ret2.to_frame()

        close_spot_ret1.columns = ['close_spot_ret1']
        close_spot_ret2.columns = ['close_spot_ret2']
        netmoney = np.sign(netmoney).to_frame()
        netmoney.columns = ['netmoney']

        mdf = close_spot_ret1.join(close_spot_ret2).join(netmoney, how = 'inner')
        mdf.loc[(mdf.close_spot_ret1<-0.005) & (mdf.close_spot_ret2>0.001) & (mdf.netmoney==1) ,'signal'] = 1
        mdf.loc[(mdf.close_spot_ret1 > 0.005) & (mdf.close_spot_ret2>0) & (mdf.netmoney==1),'signal'] = 1
        mdf['signal'] = mdf['signal'].fillna(value = 0)

        factor = mdf[['signal']]
        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor