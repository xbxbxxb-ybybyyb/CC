from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import re

class HistoryData:
    def __init__(self, date, hisdays=40):
        self.date = date
        self.hisdays = hisdays
        self.start_date = udt.get_trading_day_offset(date, -1 * hisdays)[0].strftime('%Y%m%d')
        self.tdays_list = [x.date() for x in udt.get_trading_date_range(self.start_date, self.date)]
        self.next_tdate = udt.get_trading_day_offset(date, 1)[0].strftime('%Y%m%d')
        self.raw_model_start_date = udt.get_trading_day_offset(date, -1 * factor_raw_histdays)[0].strftime('%Y%m%d')

        csvdf = pd.read_csv(kzz_stock_mapping_file, index_col=0)['stockcode']
        self.collector = {'kzz_stock_mapping_dict':csvdf.to_dict()}
        self.all_kzz_ticker_list = csvdf.index.tolist()

    def update_collector(self, data):
        assert isinstance(data, dict)
        assert len(set(data.keys()) & set(self.collector.keys())) == 0
        self.collector.update(data)

    def get_kzz_and_stock_hisdata(self):
        minute_data = IO.read_data([self.start_date, str(self.date)+'235959'], alt = kzz_stock_minute_path)
        clist = minute_data.columns.tolist()
        clist.remove('NumTrades')
        minute_data = minute_data.unstack()
        target_data = {}
        for x in clist:
            target_data[x] = minute_data[x]
        return target_data

    def get_kzz_onret(self):
        data = IO.read_data([self.start_date, self.date], columns = ['long_ret_930_1450'], alt = kzz_onret_path)
        data = data.unstack()['long_ret_930_1450']
        return {'kzz_onret': data}

    def get_kzz_dailyinfo(self):
        target_data = {}
        
        from xquant.factordata import FactorData
        s = FactorData()
        # 债券余额
        _temp = s.get_factor_value('WIND_CBondAmount',factors=['S_INFO_WINDCODE','S_INFO_ENDDATE','B_INFO_OUTSTANDINGBALANCE'], 
            S_INFO_ENDDATE=['<=%s' % '20210101'])
        cbondamount = _temp.append(s.get_factor_value('WIND_CBondAmount',factors=['S_INFO_WINDCODE','S_INFO_ENDDATE','B_INFO_OUTSTANDINGBALANCE'], 
            S_INFO_ENDDATE=['>20210101', '<=%s' % self.date]))
        cbondamount = cbondamount.rename(columns = {'S_INFO_WINDCODE':'Ticker', 'S_INFO_ENDDATE':'dt'})
        cbondamount['dt'] = pd.to_datetime(cbondamount['dt'])
        cbondamount = cbondamount[cbondamount.Ticker.isin(self.all_kzz_ticker_list)]
        cbondamount = cbondamount.set_index(['dt','Ticker']).sort_index()
        cbondamount = cbondamount.unstack()['B_INFO_OUTSTANDINGBALANCE']
        cbondamount.loc[pd.to_datetime(self.next_tdate).date()] = np.nan
        cbondamount = cbondamount.shift(1).fillna(method = 'ffill') * 1e8
        cbondamount.index = pd.to_datetime(cbondamount.index)
        cbondamount = cbondamount.loc[self.tdays_list + [pd.to_datetime(self.next_tdate).date()]]
        target_data['B_INFO_OUTSTANDINGBALANCE'] = cbondamount

        # 转股价
        ccbondvaluation = s.get_factor_value('WIND_CCBondValuation',factors=['S_INFO_WINDCODE','TRADE_DT','CB_ANAL_CONVPRICE'], 
            TRADE_DT=['>=%s'%self.start_date, '<=%s' % self.date])
        ccbondvaluation = ccbondvaluation.rename(columns = {'S_INFO_WINDCODE':'Ticker', 'TRADE_DT':'dt'})
        ccbondvaluation['dt'] = pd.to_datetime(ccbondvaluation['dt'])
        ccbondvaluation = ccbondvaluation[ccbondvaluation.Ticker.isin(self.all_kzz_ticker_list)]
        ccbondvaluation = ccbondvaluation.set_index(['dt','Ticker']).sort_index()
        ccbondvaluation = ccbondvaluation.unstack()['CB_ANAL_CONVPRICE']
        ccbondvaluation = ccbondvaluation.loc[self.tdays_list]
        ccbondvaluation.loc[pd.to_datetime(self.next_tdate).date()] = np.nan
        ccbondvaluation = ccbondvaluation.shift(1)
        target_data['CB_ANAL_CONVPRICE'] = ccbondvaluation
        return target_data

    def get_raw_model(self):
        model = IO.read_data([self.raw_model_start_date, self.date], alt = kzz_model_value_path)
        clist = model.columns.tolist()
        model = model.unstack()
        model_dict = {}
        for x in clist:
            model_dict[x] = model[x]
        return {'model_raw':model_dict}

    def get_model_file(self):
        model_file = diller(kzz_model_file_path)
        return {'model_file':model_file}

    def get_universe(self):
        univ = IO.read_data([20170101, self.date], columns = ['overnight_v1'], alt = kzz_universe_path)
        univ = univ[univ.overnight_v1 == True]
        adate = univ.index.get_level_values(0).unique().tolist()[-1]
        univ = univ.loc[adate]
        return {'universe' : univ.index.tolist()}

    def get_all(self):
        self.update_collector(self.get_kzz_and_stock_hisdata())
        self.update_collector(self.get_kzz_onret())
        self.update_collector(self.get_kzz_dailyinfo())
        self.update_collector(self.get_raw_model())
        self.update_collector(self.get_model_file())
        self.update_collector(self.get_universe())
     
class HotData:
    def __init__(self, ref_date=None):
        if ref_date is None:
            ref_date = pd.Timestamp.now().date()
        self.ref_date = IO.str_date_parser(ref_date).strftime('%Y%m%d')
        self.collector = dict()

    def get_all(self):
        kzz1 = pd.read_hdf(os.path.join(hot_root, self.ref_date, 'ccbond_kline_1min_092500_140000.h5'))
        kzz2 = pd.read_hdf(os.path.join(hot_root, self.ref_date, 'ccbond_kline_1min_140000_144400.h5'))
        stk_minute = pd.read_hdf(os.path.join(hot_root, self.ref_date, 'ccbond_stock_kline_1min_092500_144300.h5')).add_suffix('_stk')
        const = pd.read_hdf(os.path.join(hot_root, self.ref_date, 'mdconstant.h5'))
        kzz_minute = kzz1.append(kzz2)
        return kzz_minute, stk_minute, const
