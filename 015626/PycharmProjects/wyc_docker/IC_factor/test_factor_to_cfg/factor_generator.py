import pandas as pd
from multifactor.IO import IO
import os
import numpy as np

class FactorGenerator:
    data_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
    future_data = 'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5'
    spot_data = 'MD_STOCK_INDEX_SPOT_MINUTE.h5'

    ic_cfg_data = 'IC_cfg_data_insample.pkl'
    if_cfg_data = 'IF_cfg_data_insample.pkl'
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
        cfg_data = pd.read_pickle(os.path.join(obj.data_root_path, obj.if_cfg_data))
        obj.hot_data = cfg_data

    def slicer(self):
        data_dict = {}
        for col in self.required_columns:
            for key in ['open','high','low','close','vwap','share','volume','amount','turnover','weight']:
                if key in col:
                    data_dict[col] = self.hot_data[key + '_hs300'].copy()
            if 'position' in col:
                data_dict[col] = self.hot_data['volume' + '_hs300'].copy()
        return data_dict

    def __callback__(self):
        prepared_data = self.slicer()

        finaldf = self.on_bar(prepared_data)
        factorname = self.__class__.__name__
        savepath = '/data/user/015626/data/share/factor/1min/IC_factors/jiemian/if_mid_variable_20201009/'
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        finaldf.to_hdf(savepath + factorname +'_cfg.h5', key = factorname)



    def on_bar(self, data):
        raise NotImplementedErrror