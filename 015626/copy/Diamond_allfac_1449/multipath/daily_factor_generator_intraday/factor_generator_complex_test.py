import os
import pandas as pd
import datetime as dt
from multiprocessing import Pool
from joblib import Parallel, delayed
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils.help_functions_wsc import read_pickle, save_pickle, pd_writer, replace_zero


class FactorGeneratorComplex:
    __data__ = None
    __ticker__=None
    def __init__(self, factor_name='test', lookback_bars=5000, required_columns=None,
                 savepath='/data/user/017024/share/overnight/alpha_intraday'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hot_data(inst, start_date, end_date):
        start_date = str(start_date)
        end_date = str(end_date)

        print(dt.datetime.now(), '开始读取数据')
        data_dict = {}
        cfg_data_noon_zz500 = read_pickle('/data/user/015626/data/share/MD/CHINA_STOCK/prod_for_overnight/prod_pickle/IC_cfg_data_2020_for_overnight.pkl')
        cfg_data_noon_hs300 = read_pickle('/data/user/015626/data/share/MD/CHINA_STOCK/prod_for_overnight/prod_pickle/IF_cfg_data_2020_for_overnight.pkl')
        cfg_data_afternoon = pd.read_hdf(os.path.join('/data/user/017024/share/overnight/data/intraday/', end_date, end_date+'_cfg_afternoon.h5'))
        assert int(cfg_data_afternoon.index.levels[0][-1].strftime("%H%M")) >= 1449
        print(dt.datetime.now(), '开始计算分钟频')
        
        for i in cfg_data_noon_zz500.keys():
            cfg_data_noon_zz500[i] = cfg_data_noon_zz500[i][:'20210304 11:30:00']
        for i in cfg_data_noon_hs300.keys():
            cfg_data_noon_hs300[i] = cfg_data_noon_hs300[i][:'20210304 11:30:00']
        
        weight_mask_zz500 = cfg_data_noon_zz500['weight_boolean_zz500']
        weight_mask_hs300 = cfg_data_noon_hs300['weight_boolean_hs300']
        weight_zz500 = cfg_data_noon_zz500['weight_zz500']
        weight_hs300 = cfg_data_noon_hs300['weight_hs300']
        
        zz800_list = list(cfg_data_afternoon.index.levels[1])
        zz500_list_raw = weight_mask_zz500.iloc[-1][weight_mask_zz500.iloc[-1]==1].index
        zz500_list_raw = [i for i in zz500_list_raw if i[:9] in zz800_list]
        zz500_list = [i[:9] for i in zz500_list_raw]
        hs300_list_raw = weight_mask_hs300.iloc[-1][weight_mask_hs300.iloc[-1]==1].index
        hs300_list_raw = [i for i in hs300_list_raw if i[:9] in zz500_list]
        hs300_list = [i[:9] for i in hs300_list_raw]
        
        need_columns = cfg_data_afternoon.columns
        for i in need_columns:
            i_name1 = i + '_zz500'
            i_name2 = i + '_hs300'
            data_old1 = cfg_data_noon_zz500[i_name1]
            data_old2 = cfg_data_noon_hs300[i_name2]
            data_new = cfg_data_afternoon[i].unstack()
            data_new1 = data_new[zz500_list]
            data_new2 = data_new[hs300_list]
            data_new1.columns = zz500_list_raw
            data_new2.columns = hs300_list_raw
            # print(data_old1.shape, data_new1.shape)
            data_need1 = pd.concat([data_old1, data_new1], axis=0, sort=True)
            # print(data_need1.shape)
            # print(data_need1)
            data_dict[i_name1] = data_need1
            data_need2 = pd.concat([data_old2, data_new2], axis=0, sort=True)
            data_dict[i_name2] = data_need2
        
        print(dt.datetime.now(), '四个分钟频特殊字段')
        weight_mask_zz500 = weight_mask_zz500.reindex(data_dict['open_zz500'].index)
        weight_mask_zz500_old = weight_mask_zz500.loc[:pd.to_datetime(end_date)]
        weight_mask_zz500_new = weight_mask_zz500.loc[pd.to_datetime(end_date):]
        weight_mask_zz500_new = weight_mask_zz500_new.fillna(axis=0, method='ffill')
        data_dict['weight_boolean_zz500'] = pd.concat([weight_mask_zz500_old, weight_mask_zz500_new], axis=0, sort=True).astype('bool')

        weight_mask_hs300 = weight_mask_hs300.reindex(data_dict['open_hs300'].index)
        weight_mask_hs300_old = weight_mask_hs300.loc[:pd.to_datetime(end_date)]
        weight_mask_hs300_new = weight_mask_hs300.loc[pd.to_datetime(end_date):]
        weight_mask_hs300_new = weight_mask_hs300_new.fillna(axis=0, method='ffill')
        data_dict['weight_boolean_hs300'] = pd.concat([weight_mask_hs300_old, weight_mask_hs300_new], axis=0, sort=True).astype('bool')

        weight_zz500 = weight_zz500.reindex(data_dict['open_zz500'].index)
        weight_zz500_old = weight_zz500.loc[:pd.to_datetime(end_date)]
        weight_zz500_new = weight_zz500.loc[pd.to_datetime(end_date):]
        weight_zz500_new = weight_zz500_new.fillna(axis=0, method='ffill')
        data_dict['weight_zz500'] = pd.concat([weight_zz500_old, weight_zz500_new], axis=0, sort=True)

        weight_hs300 = weight_hs300.reindex(data_dict['open_hs300'].index)
        weight_hs300_old = weight_hs300.loc[:pd.to_datetime(end_date)]
        weight_hs300_new = weight_hs300.loc[pd.to_datetime(end_date):]
        weight_hs300_new = weight_hs300_new.fillna(axis=0, method='ffill')
        data_dict['weight_hs300'] = pd.concat([weight_hs300_old, weight_hs300_new], axis=0, sort=True)
        
        print(dt.datetime.now(), '开始计算日频')
        # 日频数据
        daily_amount_zz500 = data_dict['amount_zz500'].between_time('09:30', '14:49')
        data_dict['daily_amount_zz500'] = replace_zero(daily_amount_zz500.groupby(daily_amount_zz500.index.date).sum())
        daily_volume_zz500 = data_dict['volume_zz500'].between_time('09:30', '14:49')
        data_dict['daily_volume_zz500'] = replace_zero(daily_volume_zz500.groupby(daily_volume_zz500.index.date).sum())
        # daily_open_zz500 = data_dict['open_zz500'].between_time('09:30', '14:49')
        data_dict['daily_open_zz500'] = data_dict['open_zz500'].groupby(data_dict['open_zz500'].index.date).first()
        daily_high_zz500 = data_dict['high_zz500'].between_time('09:30', '14:49')
        data_dict['daily_high_zz500'] = daily_high_zz500.groupby(daily_high_zz500.index.date).max()
        daily_close_zz500 = data_dict['close_zz500'].between_time('09:30', '14:49')
        data_dict['daily_close_zz500'] = daily_close_zz500.groupby(daily_close_zz500.index.date).last()
        daily_low_zz500 = data_dict['low_zz500'].between_time('09:30', '14:49')
        data_dict['daily_low_zz500'] = daily_low_zz500.groupby(daily_low_zz500.index.date).min()                
        # daily_weight_zz500 = data_dict['weight_zz500'].between_time('09:30', '14:49')
        data_dict['daily_weight_zz500'] = data_dict['weight_zz500'].groupby(data_dict['weight_zz500'].index.date).first()
        data_dict['daily_weight_mask_zz500'] = data_dict['weight_boolean_zz500'].groupby(data_dict['weight_boolean_zz500'].index.date).first()
        
        daily_amount_hs300 = data_dict['amount_hs300'].between_time('09:30', '14:49')
        data_dict['daily_amount_hs300'] = replace_zero(daily_amount_hs300.groupby(daily_amount_hs300.index.date).sum())
        daily_volume_hs300 = data_dict['volume_hs300'].between_time('09:30', '14:49')
        data_dict['daily_volume_hs300'] = replace_zero(daily_volume_hs300.groupby(daily_volume_hs300.index.date).sum())
        # daily_open_hs300 = data_dict['open_hs300'].between_time('09:30', '14:49')
        data_dict['daily_open_hs300'] = data_dict['open_hs300'].groupby(data_dict['open_hs300'].index.date).first()
        daily_high_hs300 = data_dict['high_hs300'].between_time('09:30', '14:49')
        data_dict['daily_high_hs300'] = daily_high_hs300.groupby(daily_high_hs300.index.date).max()
        daily_close_hs300 = data_dict['close_hs300'].between_time('09:30', '14:49')
        data_dict['daily_close_hs300'] = daily_close_hs300.groupby(daily_close_hs300.index.date).last()
        daily_low_hs300 = data_dict['low_hs300'].between_time('09:30', '14:49')
        data_dict['daily_low_hs300'] = daily_low_hs300.groupby(daily_low_hs300.index.date).min()                
        # daily_weight_hs300 = data_dict['weight_hs300'].between_time('09:30', '14:49')
        data_dict['daily_weight_hs300'] = data_dict['weight_hs300'].groupby(data_dict['weight_hs300'].index.date).first()
        data_dict['daily_weight_mask_hs300'] = data_dict['weight_boolean_hs300'].groupby(data_dict['weight_boolean_hs300'].index.date).first()
        
        print(dt.datetime.now(), '数据index转换及切割')
        
        # save_pickle(data_dict, os.path.join('/data/user/017024/share/overnight/data/intraday/', end_date, end_date+'_cfg.pkl'))
        # save_pickle(data_dict, os.path.join('/data/user/017024/share/overnight/data/intraday/', end_date+'_cfg2.pkl'))
        
        for key in data_dict.keys():
            data_dict[key].index.name = 'dt'
            data_dict[key].index = pd.to_datetime(data_dict[key].index)
            data_dict[key] = data_dict[key].loc[start_date:end_date]
        inst.__data__ = data_dict
        
        print(dt.datetime.now(), '数据准备完毕')


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
