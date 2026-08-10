import os
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils.help_functions_wsc import read_pickle, save_pickle, pd_writer


class FactorGeneratorComplex:
    __data__ = None
    __ticker__=None
    def __init__(self, factor_name='test', lookback_bars=5000, required_columns=None,
                 savepath='/data/user/017024/share/overnight/alpha'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hot_data(inst, start_date, end_date, ticker = 'IC.CFE', datakind = 'insample'):
        start_date = str(start_date)
        end_date = str(end_date)
        
        inst.__ticker__ = ticker

        data_dict = {}
        if datakind in ['insample','insample_ago']:
            index_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/SPOT_DATA_120101_200901.pkl')
            daily_index_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/daily_index_data_120101_200901.pkl')
        elif datakind == 'outsample':
            index_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/SPOT_DATA_2020.pkl')
            daily_index_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/spot_daily_overnight.pkl')
        
        if ticker == 'IC.CFE':
            if datakind == 'insample':
                cfg_stocks_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IC_cfg_150416_200401_data.pkl')
                cfg_hf_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IC_cfg_hf_data_150301_200401.pkl')
                daily_cfg_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/daily_cfg_data_ic_150416_200401.pkl')
            elif datakind == 'outsample':        
                cfg_stocks_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IC_cfg_data_2020.pkl')
                cfg_hf_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IC_cfg_hf_data_2023.pkl')
                daily_cfg_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/ic_cfg_daily_overnight.pkl')
            elif datakind == 'insample_ago':
                cfg_stocks_data = read_pickle(os.path.join(insample_path,'IC_cfg_120101_150701_data.pkl'))
                cfg_hf_data = read_pickle(os.path.join(insample_path, 'IC_cfg_hf_data_130101_150701.pkl'))
        elif ticker == 'IF.CFE':
            if datakind == 'insample':
                cfg_stocks_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IF_cfg_130101_200401_data.pkl')
                cfg_hf_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IF_cfg_hf_data_150301_200401.pkl')
                daily_cfg_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/daily_cfg_data_if_130101_200401.pkl')
            elif datakind == 'outsample':        
                cfg_stocks_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IF_cfg_data_2020.pkl')
                cfg_hf_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IF_cfg_hf_data_2023.pkl')
                daily_cfg_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/if_cfg_daily_overnight.pkl')
            elif datakind == 'insample_ago':
                cfg_stocks_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IF_cfg_130101_200401_data.pkl')
                cfg_hf_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IF_cfg_hf_data_130101_150701.pkl')
                daily_cfg_data = read_pickle('/data/user/017024/share/overnight/data/daily_cfg_data_if_130101_200401.pkl')
               
        data_dict = {**index_data, **cfg_stocks_data, **cfg_hf_data, **daily_index_data, **daily_cfg_data}
        for key in data_dict.keys():
            data_dict[key] = data_dict[key].loc[start_date:end_date]
        inst.__data__ = data_dict


    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self, start_date, end_date):
        data = self.slicer()
        savepath = self.savepath
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        factor = self.on_bar(data)
        start_date = str(start_date)
        end_date = str(end_date)
        factor = factor.loc[start_date:end_date]
        pd_writer(factor, savepath)
