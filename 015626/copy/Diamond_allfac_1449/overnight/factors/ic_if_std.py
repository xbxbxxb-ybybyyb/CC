import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class ic_if_std(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns = ['close_IC.CFE', 'close_IF.CFE', 'recent_month_mask']

        super(ic_if_std, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

        
    def on_bar(self, data):
        columnname = self.__class__.__name__
        ic_std = ts_std(data['close_IC.CFE'].pct_change(), 30)[data['recent_month_mask']].mean(axis = 1)
        if_std = ts_std(data['close_IF.CFE'].pct_change(), 30)[data['recent_month_mask']].mean(axis = 1)
        ic_if_std = pd.concat([ic_std, if_std], axis = 1).mean(axis = 1)
        factor = ic_if_std.groupby(ic_if_std.index.date).mean().to_frame()

        factor.index.name = 'dt'

        factor.columns = [columnname]
        factor.index = pd.to_datetime(factor.index)
        return factor