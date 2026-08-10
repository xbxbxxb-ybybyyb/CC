import pandas as pd
from multifactor.IO import IO
import os

class FactorGenerator:
    data_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
    future_data = 'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5'
    spot_data = 'MD_STOCK_INDEX_SPOT_MINUTE.h5'
    start_time = 20190101
    end_time = 20200101
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
        data = IO.read_data([obj.start_time, obj.end_time], alt = os.path.join(obj.data_root_path, obj.future_data))
        data = data.xs('IC.CFE', level = 1)
        obj.hot_data = data

    def slicer(self):
        return self.hot_data[self.required_columns].iloc[-self.lookback_bars:, :].copy()

    def __callback__(self):
        prepared_data = self.slicer()
        return self.on_bar(prepared_data)

    def on_bar(self, data):
        raise NotImplementedErrror