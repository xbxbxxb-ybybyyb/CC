import pandas as pd
from multifactor.IO import IO
import os
import numpy as np

class FactorGenerator:
    data_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
    future_data = 'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5'
    spot_data = 'MD_STOCK_INDEX_SPOT_MINUTE.h5'

    ic_cfg_data = 'IC_cfg_data_insample.pkl'
    start_time = 20170101
    end_time = 20200101
    hot_data = None

    def __init__(self, required_columns=['close'], lookback_bars=50000000):
        self._required_columns = required_columns
        self._lookback_bars = lookback_bars

    @property
    def required_columns(self):
        return self._required_columns

    @property
    def lookback_bars(self):
        return self._lookback_bars

    @classmethod
    def prepare_hot_data(obj):
        print('read data')
        cfg_data = pd.read_pickle(os.path.join(obj.data_root_path, obj.ic_cfg_data))
        obj.hot_data = cfg_data

    def slicer(self):
        return self.hot_data.copy()
        # return self.hot_data[self.required_columns].copy()

    def __callback__(self):
        prepared_data = self.slicer()
        if np.all(['spot' in x for x in self.required_columns]):
            prepared_data = prepared_data.rename(columns = {x:x.replace('zz500','spot') for x in prepared_data.columns.tolist()})
        elif np.all(['_' not in x for x in self.required_columns]):
            prepared_data = prepared_data.rename(columns = {x: x.replace('_zz500', '') for x in prepared_data.columns.tolist()})
        else:
            return

        finaldf = pd.DataFrame()
        for stock in prepared_data.index.get_level_values(1).unique().tolist():
            stock_data = prepared_data.xs(stock, level = 1)
            stock_factor = self.on_bar(stock_data)
            columnname = stock_factor.columns[0]
            stock_factor.columns = [stock]
            finaldf = stock_factor if len(finaldf) == 0 else finaldf.join(stock_factor, how = 'outer')

        assert len(finaldf.dropna(axis = 0)) > 0
        savepath = '/data/user/015626/data/share/factor/1min/IC_factors/jiemian/mid_variable_20200928/'
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        finaldf.to_hdf(savepath + columnname +'_cfg.h5', key = columnname)



    def on_bar(self, data):
        raise NotImplementedErrror