from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from arrow.naming_config import *
from arrow.utility import *
import re

class PrepareHotData:
    def __init__(self, ref_date=None, kind = 'history'):
        assert kind in ['history', 'today']
        if ref_date is None:
            ref_date = pd.Timestamp.now().date()
        self.ref_date = IO.str_date_parser(ref_date).strftime('%Y%m%d')
        univ = pd.read_pickle(universe_path).reset_index()
        self.universe = univ[univ['dt'] == self.ref_date].Ticker.tolist()

        self.kind = kind

        if self.kind == 'history':
            eod = IO.read_data([self.ref_date], columns = ['S_DQ_LIMIT', 'S_DQ_STOPPING'], alt = eod_path).reset_index(level = 0, drop = True)
            eod = eod.loc[self.universe]
            self.limit_price = eod['S_DQ_LIMIT'].dropna().to_dict()
            self.stop_price = eod['S_DQ_STOPPING'].dropna().to_dict()

    def get_all(self):
        
        if self.kind == 'history':
            _data_root = hot_data_root
            hot_data_savepath = os.path.join(hot_root, self.ref_date)
        else:
            _data_root = today_data_root
            hot_data_savepath = os.path.join(hot_today_root, self.ref_date)
        all_data_dict = {}
        for k,v in name_dict.items():
            data_dict = {}
            for stk in self.universe:
                csv_path = os.path.join(_data_root, v, stk, f'{self.ref_date}.parquet')
                # csv_path = os.path.join('/data/user/000072/share/for_wyc/auction_data/20230324/', v, stk, f'{self.ref_date}.csv')
                if not os.path.exists(csv_path):
                    stk_data = pd.DataFrame()
                    print(f'{csv_path} not exists')
                else:
                    try:
                        stk_data = pd.read_parquet(csv_path)
                    except:
                        stk_data = pd.DataFrame()
                        print(f'{csv_path} read with problem')
                if len(stk_data) > 0:
                    stk_data['dt'] = pd.to_datetime(stk_data['dt'])
                    stk_data = stk_data.set_index('dt').between_time(auction_start_time, auction_end_time).sort_index().reset_index()
                    if len(stk_data) > 0:
                        if k == 'transaction':
                            stk_data.loc[stk_data.TradeBuyNo > stk_data.TradeSellNo, 'TradeBSFlag'] = 1
                            stk_data.loc[stk_data.TradeBuyNo < stk_data.TradeSellNo, 'TradeBSFlag'] = 2
                        if k in ['order', 'order_raw']:
                            stk_data = stk_data[(stk_data['OrderType'].isin([1,2,3,10])) & stk_data['OrderBSFlag'].isin([1,2])]
                            if len(stk_data) == 0:
                                continue
                            if self.kind == 'history':
                                if stk in self.limit_price.keys():
                                    limit_px = self.limit_price[stk]
                                    stk_data.loc[(stk_data.OrderPrice > limit_px) & (stk_data.OrderType.isin([2, 10])) & (stk_data.OrderPrice != 0), 'OrderPrice'] = limit_px
                                if stk in self.stop_price.keys():
                                    stop_px = self.stop_price[stk]
                                    stk_data.loc[(stk_data.OrderPrice < stop_px) & (stk_data.OrderType.isin([2, 10])) & (stk_data.OrderPrice != 0), 'OrderPrice'] = stop_px
                            stk_data.loc[stk_data['OrderType'].isin([1,3]),'OrderPrice'] = np.nan
                            stk_data = stk_data[stk_data.OrderPrice != 0]
                            if len(stk_data) == 0:
                                continue
                            stk_data['temp_col'] = round(stk_data['OrderPrice'].rolling(10,min_periods = 5).mean(),2)
                            stk_data['OrderPrice'] = stk_data['OrderPrice'].fillna(stk_data['temp_col']).fillna(method = 'ffill')
                            stk_data = stk_data.drop(['temp_col'], axis = 1)
                        data_dict[stk] = stk_data
            all_data_dict[k] = data_dict
        
        if not os.path.exists(hot_data_savepath):
            os.makedirs(hot_data_savepath)
        diller(os.path.join(hot_data_savepath, 'hot.pkl'), all_data_dict)
