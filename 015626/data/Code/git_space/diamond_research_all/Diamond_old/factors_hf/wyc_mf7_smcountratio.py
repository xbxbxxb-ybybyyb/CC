from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf7_smcountratio(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        required_columns=['buy_superorder_count_500','sell_superorder_count_500','buy_bigorder_count_500','sell_bigorder_count_500',
        'buy_midorder_count_500','sell_midorder_count_500','buy_smallorder_count_500','sell_smallorder_count_500']
        lookback_bars=2000
        super(wyc_mf7_smcountratio, self).__init__(*args, required_columns=required_columns,
                                  lookback_bars=lookback_bars, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        #  小单中单笔数占每天总的交易笔数的比例
        buy_superorder_count_500 = df['buy_superorder_count_500']
        sell_superorder_count_500 = df['sell_superorder_count_500']
        buy_bigorder_count_500 = df['buy_bigorder_count_500']
        sell_bigorder_count_500 = df['sell_bigorder_count_500']
        buy_midorder_count_500 = df['buy_midorder_count_500']
        sell_midorder_count_500 = df['sell_midorder_count_500']
        buy_smallorder_count_500 = df['buy_smallorder_count_500']
        sell_smallorder_count_500 = df['sell_smallorder_count_500']

        buy_superorder_count_500 = buy_superorder_count_500.loc[buy_superorder_count_500.index.time <= datetime.time(14,49)]
        sell_superorder_count_500 = sell_superorder_count_500.loc[sell_superorder_count_500.index.time <= datetime.time(14,49)]
        buy_bigorder_count_500 = buy_bigorder_count_500.loc[buy_bigorder_count_500.index.time <= datetime.time(14,49)]
        sell_bigorder_count_500 = sell_bigorder_count_500.loc[sell_bigorder_count_500.index.time <= datetime.time(14,49)]
        buy_midorder_count_500 = buy_midorder_count_500.loc[buy_midorder_count_500.index.time <= datetime.time(14,49)]
        sell_midorder_count_500 = sell_midorder_count_500.loc[sell_midorder_count_500.index.time <= datetime.time(14,49)]
        buy_smallorder_count_500 = buy_smallorder_count_500.loc[buy_smallorder_count_500.index.time <= datetime.time(14,49)]
        sell_smallorder_count_500 = sell_smallorder_count_500.loc[sell_smallorder_count_500.index.time <= datetime.time(14,49)]

        smallcount = sell_smallorder_count_500.groupby(sell_smallorder_count_500.index.date).sum().sum(axis = 1)
        smallcount += buy_smallorder_count_500.groupby(buy_smallorder_count_500.index.date).sum().sum(axis = 1)

        midcount = sell_midorder_count_500.groupby(sell_midorder_count_500.index.date).sum().sum(axis = 1)
        midcount += buy_midorder_count_500.groupby(buy_midorder_count_500.index.date).sum().sum(axis = 1)

        bigcount = sell_bigorder_count_500.groupby(sell_bigorder_count_500.index.date).sum().sum(axis = 1)
        bigcount += buy_bigorder_count_500.groupby(buy_bigorder_count_500.index.date).sum().sum(axis = 1)

        supercount = sell_superorder_count_500.groupby(sell_superorder_count_500.index.date).sum().sum(axis = 1)
        supercount += buy_superorder_count_500.groupby(buy_superorder_count_500.index.date).sum().sum(axis = 1)

        factor = smallcount + midcount + bigcount + supercount

        factor = (smallcount + midcount) / factor
        factor = factor.to_frame()

        factor = ts_rank(factor, 30)
        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor