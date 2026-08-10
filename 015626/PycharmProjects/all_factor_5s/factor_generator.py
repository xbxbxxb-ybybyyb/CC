import pandas as pd
from multifactor.IO import IO
import os

class FactorGenerator:
    data_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/5s/'
    future_data = 'MD_STOCK_INDEX_FUTURES_5S_MAIN.h5'
    spot_data = 'MD_STOCK_INDEX_SPOT_5S.h5'

    start_time = 20170101
    end_time = 20190801
    hot_data = None

    def __init__(self, required_columns, lookback_bars):
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
        data1 = IO.read_data([obj.start_time, obj.end_time], alt = os.path.join(obj.data_root_path, obj.future_data))
        data1 = data1.xs('IC.CFE', level = 1)
        data2 = IO.read_data([obj.start_time, obj.end_time], alt=os.path.join(obj.data_root_path, obj.spot_data))
        data2 = data2.xs('IC.CFE', level=1)
        obj.hot_data = data1.join(data2)
        print(obj.hot_data)
        print('read data finished')

    def slicer(self):
        return self.hot_data[self.required_columns].copy()
        # return self.hot_data[self.required_columns].copy()

    def __callback__(self):
        prepared_data = self.slicer()
        df = self.on_bar(prepared_data)
        columnname = df.columns.tolist()[0]
        if len(df.dropna(axis = 0)) == 0:
            print(columnname,'*************')
        df.to_hdf('/data/user/015626/data/share/factor/5s/5s_factor_20200710/stage1/' + columnname +'.h5', key = columnname)
        return df


    def on_bar(self, data):
        raise NotImplementedErrror