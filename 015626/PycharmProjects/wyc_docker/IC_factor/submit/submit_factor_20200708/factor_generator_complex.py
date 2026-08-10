from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pandas as pd
pd.set_option('display.width', 5000)
import numpy as np
import os


class FactorGeneratorComplex:
    __data__ = None

    def __init__(self, factor_name='test', lookback_bars=5000, required_columns=None,
                 savepath='/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    def pd_writer(self, sig, savepath):
        sig_name = sig.columns[0]
        file_name = os.path.join(savepath, sig_name + '.h5')
        if os.path.exists(file_name):
            sigold = IO.read_data(alt=file_name)
            sigold = sigold[~sigold.index.isin(sig.index)]
            signew = pd.concat([sigold, sig], axis=0).sort_index()
            override = True
        else:
            signew = sig
            override = None
        IO.pd_hdf5_writer(signew, file_name, sig_name, override=override, append=None)

    @classmethod
    def prepare_hot_data(inst, start_date, end_date):
        data_dict = {}
        data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
        start_date = IO.str_date_parser(start_date)
        end_date = IO.str_date_parser(end_date)
        index_data = IO.read_data([start_date, end_date],alt=os.path.join(data_path,'MD_STOCK_INDEX_SPOT_MINUTE.h5')).xs('IC.CFE',level=1).sort_index()
        futures_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path,'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')).xs('IC.CFE', level=1).sort_index()
        tick2minute_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path,'MD_STOCK_INDEX_FUTURES_TICK_TO_MINUTE.h5')).xs('IC.CFE', level=1).sort_index()
        cfg_data = IO.read_data([start_date, end_date],alt=os.path.join(data_path,'MD_STOCK_INDEX_CFG_MINUTE.h5')).xs('IC.CFE', level=1).sort_index()
        cfg_stocks_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path, 'IC_STOCKS_MINUTE_DATA.h5')).unstack().sort_index()

        data = pd.concat([index_data, futures_data, tick2minute_data, cfg_data], axis=1).sort_index()
        cfg = cfg_stocks_data.reindex(data.index)

        plist = ['open', 'high', 'low', 'close',
                 'open_spot', 'high_spot', 'low_spot', 'close_spot',
                 'open_zz500', 'high_zz500', 'low_zz500', 'close_zz500']

        for d in [data, cfg]:
            for col in d.columns.get_level_values(0).unique():
                if col in plist:
                    d[col] = d[col].fillna(method='pad')
                data_dict[col] = d[col]

        inst.__data__ = data_dict

    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self, start_date, end_date):
        data = self.slicer()
        savepath = os.path.join(self.savepath, 'IC_prod')
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        factor = self.on_bar(data)
        assert len(factor) == data[self.required_columns[0]].shape[0]
        factor['Ticker'] = 'IC.CFE'
        start_date = IO.str_date_parser(start_date)
        end_date = udt.get_trading_day_offset(end_date, 1)[0]
        factor = factor.loc[start_date:end_date]
        factor = factor.reset_index().set_index(['dt', 'Ticker'])
        self.pd_writer(factor, savepath)