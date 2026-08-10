import pandas as pd
from multifactor.IO import IO
import os

class FactorGenerator:
    data_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
    future_data = 'MD_STOCK_INDEX_FUTURES_TICK_TO_MINUTE.h5'
    spot_data = 'MD_STOCK_INDEX_SPOT_MINUTE.h5'
    # cfg_data = 'MD_STOCK_INDEX_CFG_MINUTE.h5'
    # if_data = 'MD_IF_MINUTE_MAIN.h5'
    # ih_data = 'MD_IH_MINUTE_MAIN.h5'
    # ic_data = 'MD_IC_MINUTE_MAIN.h5'
    start_time = 20160101
    end_time = 20200901
    hot_data = None

    def __init__(self, required_columns, factor_name = 'test', lookback_bars=5000):
        self._required_columns = required_columns
        self._lookback_bars = lookback_bars

    @property
    def required_columns(self):
        return self._required_columns

    @classmethod
    def prepare_hot_data(obj):
        print('read data')
        future_data = IO.read_data([obj.start_time, obj.end_time],columns=['open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'vwap','twap','share'],
                                   alt = os.path.join(obj.data_root_path, obj.future_data))
        fic = future_data.xs('IC.CFE', level = 1)
        fif = future_data.xs('IF.CFE', level=1)
        fclist = fif.columns.tolist()
        nlist = [x + '_if' for x in fclist]
        fif.columns = nlist

        fih = future_data.xs('IH.CFE', level=1)
        hclist = fih.columns.tolist()
        nlist = [x + '_ih' for x in hclist]
        fih.columns = nlist


        spot_data = IO.read_data([obj.start_time, obj.end_time], alt=os.path.join(obj.data_root_path, obj.spot_data))
        sic = spot_data.xs('IC.CFE', level=1)
        sif = spot_data.xs('IF.CFE', level=1)
        sclist = sif.columns.tolist()
        nlist = [x + '_if' for x in sclist]
        sif.columns = nlist

        sih = spot_data.xs('IH.CFE', level=1)
        sclist = sih.columns.tolist()
        nlist = [x + '_ih' for x in sclist]
        sih.columns = nlist

        obj.hot_data = fic.join(fif).join(sic).join(sif).join(fih).join(sih)
        print(obj.hot_data)
        print('read data finished')

    def slicer(self):
        return self.hot_data[self.required_columns].copy()
        # return self.hot_data[self.required_columns].copy()

    def __callback__(self):
        prepared_data = self.slicer()
        df = self.on_bar(prepared_data)
        columnname = df.columns.tolist()[0]
        print(columnname, '       done')
        if len(df.dropna(axis = 0)) == 0:
            print(columnname,'*************')
        spath = '/data/user/015626/data/share/factor/1min/IC_factors/tick_to_minute_20200907/'
        if not os.path.exists(spath):
            os.makedirs(spath)
        df.to_hdf(spath + columnname +'.h5', key = columnname)
        return df


    def on_bar(self, data):
        raise NotImplementedErrror