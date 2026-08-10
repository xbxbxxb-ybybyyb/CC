import pandas as pd
from multifactor.IO import IO

class FactorGenerator:
    def __init__(self, factor_name, required_columns, lookback_bars):
        self._factor_name = factor_name
        self._required_columns = required_columns
        self._lookback_bars = lookback_bars
        self._hot_data = None

    @property
    def factor_name(self):
        return self._factor_name

    @property
    def required_columns(self):
        return self._required_columns

    @property
    def lookback_bars(self):
        return self._lookback_bars

    @property
    def hot_data(self):
        return self._hot_data

    def prepare_hot_data(self, h5_path='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_IC_MAIN_FUTURES_AND_SPOT_MINUTE.h5'):
        self._hot_data = IO.read_data([20160101, 20200601], alt = h5_path).xs('IC.CFE', level = 1)

    def slicer(self):
        return self.hot_data[self.required_columns].iloc[-self.lookback_bars:, :].copy()

    def __callback__(self):
        prepared_data = self.slicer()
        return self.on_bar(prepared_data)

    def on_bar(self, data):
        raise NotImplementedErrror


# demo
class Wyc(FactorGenerator):
    def __init__(self):
        factor_name='Wyc'
        required_columns=['close', 'open']
        lookback_bars=100
        super(Wyc, self).__init__(factor_name=factor_name,
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, data):
        return (data['close'] + data['open']).to_frame()
