from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
import pandas as pd
import numpy as np
from collections import Counter
import math

def get_Benford(v):
    val = v.values.reshape((1, v.shape[0]*v.shape[1]))[0]
    freq = dict(Counter(val))
    xlist = [str(i) for i in range(1,10)]
    numsum = 0
    for x,y in freq.items():
        if x not in xlist:
            continue
        numsum += y
    raw = 0
    for x,y in freq.items():
        if x not in xlist:
            continue
        raw += (y/numsum - (math.log10(int(x)+1) - math.log10(int(x)))) ** 2
        
    return raw


class wyc_on33_BenFord_cfg(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=10, **kwargs)


    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        zz500_stock_list = self.get_mdconstant('zz500_stock_list')
        cfgvolume = df['volume_alla'][zz500_stock_list].between_time(futures_data_morning_begin, trade_stop_time)
        cfgvolume = cfgvolume.astype('str')

        firstnum = pd.DataFrame()
        for x in cfgvolume.columns:
            firstnum[x] = cfgvolume[x].apply(lambda x:x[0])

        factor = firstnum.groupby(firstnum.index.date).apply(lambda x:get_Benford(x))
        factor = factor.to_frame()
        
        factor.index.name = 'dt'
        factor.index = pd.to_datetime(factor.index)
        factor.columns = [columnname]
        return factor