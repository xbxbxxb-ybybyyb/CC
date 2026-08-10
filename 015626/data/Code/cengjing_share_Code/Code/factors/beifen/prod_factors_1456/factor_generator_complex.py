from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pandas as pd
pd.set_option('display.width', 5000)
import numpy as np
import os
from utils.sigutils import *
from utils.SIF_Factor_Test12_super import *

class FactorGeneratorComplex:
    __data__ = None
    __ticker__=None
    def __init__(self, factor_name='test', lookback_bars=5000, required_columns=None,
                 savepath='/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/IC_all_1456'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    # def pd_writer(self, sig, savepath):
    # sig_name = sig.columns[0]
    # file_name = os.path.join(savepath, sig_name + '.h5')
    # if os.path.exists(file_name):
    # sigold = IO.read_data(alt=file_name)
    # sigold = sigold[~sigold.index.isin(sig.index)]
    # signew = pd.concat([sigold, sig], axis=0).sort_index()
    # override = True
    # else:
    # signew = sig
    # override = None
    # IO.pd_hdf5_writer(signew, file_name, sig_name, override=override, append=None)

    @classmethod
    def prepare_hot_data(inst, start_date, end_date, use_cache = False, save_cache = False,ticker='IC.CFE',datakind='insample'):
        start_date = IO.str_date_parser(start_date)
        end_date = udt.get_trading_day_offset(end_date, 1)[0]
        
        inst.__ticker__ = ticker
        if use_cache:
            cache_path = '/data/user/012398/data/cache'
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)
            cache_name = os.path.join(cache_path,'IC_complex.pkl')
            inst.__data__ = read_pickle(cache_name)
        else:
            data_dict = {}
            insample_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/INSAMPLE_930_1456'
            outsample_path = '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE'
            if datakind == 'insample':
                index_data = read_pickle(os.path.join(insample_path, 'SPOT_DATA_insample.pkl'))
            elif datakind == 'outsample':
                index_data = read_pickle(os.path.join(outsample_path, 'SPOT_DATA_20201.pkl'))
            
            if ticker == 'IC.CFE':
                if datakind == 'insample':
                    cfg_stocks_data = read_pickle(os.path.join(insample_path,'IC_cfg_data_insample.pkl'))
                    cfg_hf_data = read_pickle(os.path.join(insample_path, 'IC_cfg_hf_data_insample.pkl'))
                elif datakind == 'outsample':        
                    cfg_stocks_data = read_pickle(os.path.join(outsample_path,'IC_cfg_data_20201.pkl'))
                    cfg_hf_data = read_pickle(os.path.join(outsample_path, 'IC_cfg_hf_data_20201.pkl'))
            elif ticker == 'IF.CFE':
                if datakind == 'insample':
                    cfg_stocks_data = read_pickle(os.path.join(insample_path,'IF_cfg_130101_200401_data1.pkl'))
                    cfg_hf_data = read_pickle(os.path.join(insample_path, 'IF_cfg_hf_data_160101_2004011.pkl'))
                elif datakind == 'outsample':        
                    cfg_stocks_data = read_pickle(os.path.join(outsample_path,'IF_cfg_data_20201.pkl'))
                    cfg_hf_data = read_pickle(os.path.join(outsample_path, 'IF_cfg_hf_data_20201.pkl'))
                    
            data_dict = {**index_data,**cfg_stocks_data,**cfg_hf_data}
            for key in data_dict.keys():
                data_dict[key] = data_dict[key].loc[start_date:end_date]
            inst.__data__ = data_dict
            if save_cache:
                save_pickle(data_dict, cache_name)

    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self, start_date, end_date):
        data = self.slicer()
        savepath = self.savepath
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        factor = self.on_bar(data)
        #assert len(factor) == data[self.required_columns[0]].shape[0]
        #factor['Ticker'] = self.__ticker__
        start_date = IO.str_date_parser(start_date)
        end_date = udt.get_trading_day_offset(end_date, 1)[0]
        factor = factor.loc[start_date:end_date]
        #factor = factor.reset_index().set_index(['dt', 'Ticker'])
        pd_writer(factor, savepath)
#        if check_factor_into_lib(factor, ticker=self.__ticker__):
#            pd_writer(factor, savepath)
#            return factor.columns.tolist()[0]
#        else:
#            return 'notpass_' + factor.columns.tolist()[0]