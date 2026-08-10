from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_60(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(factor_60, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime < 92600000000]
            b5amt = data.Buy1Price.values[-1] * data.Buy1OrderQty.values[-1] +\
                    data.Buy2Price.values[-1] * data.Buy2OrderQty.values[-1] +\
                    data.Buy3Price.values[-1] * data.Buy3OrderQty.values[-1] +\
                    data.Buy4Price.values[-1] * data.Buy4OrderQty.values[-1] +\
                    data.Buy5Price.values[-1] * data.Buy5OrderQty.values[-1] +\
                    data.Buy6Price.values[-1] * data.Buy6OrderQty.values[-1] +\
                    data.Buy7Price.values[-1] * data.Buy7OrderQty.values[-1] +\
                    data.Buy8Price.values[-1] * data.Buy8OrderQty.values[-1] +\
                    data.Buy9Price.values[-1] * data.Buy9OrderQty.values[-1] +\
                    data.Buy10Price.values[-1] * data.Buy10OrderQty.values[-1]
            s5amt = data.Sell1Price.values[-1] * data.Sell1OrderQty.values[-1] +\
                    data.Sell2Price.values[-1] * data.Sell2OrderQty.values[-1] +\
                    data.Sell3Price.values[-1] * data.Sell3OrderQty.values[-1] +\
                    data.Sell4Price.values[-1] * data.Sell4OrderQty.values[-1] +\
                    data.Sell5Price.values[-1] * data.Sell5OrderQty.values[-1] +\
                    data.Sell6Price.values[-1] * data.Sell6OrderQty.values[-1] +\
                    data.Sell7Price.values[-1] * data.Sell7OrderQty.values[-1] +\
                    data.Sell8Price.values[-1] * data.Sell8OrderQty.values[-1] +\
                    data.Sell9Price.values[-1] * data.Sell9OrderQty.values[-1] +\
                    data.Sell10Price.values[-1] * data.Sell10OrderQty.values[-1]
            factor[stk] = b5amt / (b5amt + s5amt)
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor