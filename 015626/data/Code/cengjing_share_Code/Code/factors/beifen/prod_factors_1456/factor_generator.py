from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pandas as pd
import numpy as np
import os
from utils.sigutils import *
from utils.SIF_Factor_Test12_super import *

class FactorGenerator:
    __data__ = None
    __ticker__=None
    def __init__(self, factor_name = 'test', lookback_bars = 5000, required_columns = None,
                 savepath = '/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/IC_all_1456'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hot_data(inst, start_date, end_date, ticker='IC.CFE', datakind = 'insample'):
        inst.__ticker__=ticker
        start_date = IO.str_date_parser(start_date)
        end_date = udt.get_trading_day_offset(end_date,1)[0]
        insample_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/INSAMPLE_930_1456'
        outsample_path = '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE'
        if datakind == 'insample':
            index_data = read_pickle(os.path.join(insample_path, 'SPOT_DATA_insample.pkl'))
            futures_data = read_pickle(os.path.join(insample_path, 'FUTURE_DATA_insample.pkl'))
        elif datakind == 'outsample':
            index_data = read_pickle(os.path.join(outsample_path, 'SPOT_DATA_20201.pkl'))
            futures_data = read_pickle(os.path.join(outsample_path, 'FUTURE_DATA_20201.pkl'))
            
        data_dict = {**index_data,**futures_data}
        for key in data_dict.keys():
            data_dict[key] = data_dict[key].loc[start_date:end_date]
        inst.__data__ = data_dict

    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self, start_date,end_date):
        data = self.slicer()
        savepath = self.savepath
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        factor = self.on_bar(data)
        #assert len(factor) == data[self.required_columns[0]].shape[0]
        #factor['Ticker'] = self.__ticker__
        start_date = IO.str_date_parser(start_date)
        end_date = udt.get_trading_day_offset(end_date,1)[0]
        factor = factor.loc[start_date:end_date]
        #factor = factor.reset_index().set_index(['dt','Ticker'])
        pd_writer(factor, savepath)
#        if check_factor_into_lib(factor, ticker=self.__ticker__):
#            pd_writer(factor, savepath)
#            return factor.columns.tolist()[0]
#        else:
#            return 'notpass_' + factor.columns.tolist()[0]