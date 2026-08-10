from diamond_vk.naming_config import *
from diamond_vk.utility import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import time, datetime
import pandas as pd
import numpy as np
import os
import sys

csvdf = pd.read_csv(kzz_stock_mapping_file, index_col=0)['stockcode']
kzz_stock_mapping_dict = csvdf.to_dict()

def prepare_mdconstant_dummy(ref_date):
    ref_date = IO.str_date_parser(ref_date)
    mdconstant = IO.read_data(ref_date, columns=['S_DQ_ADJFACTOR', 'S_DQ_PRECLOSE', 'S_DQ_LIMIT', 'S_DQ_STOPPING'], alt=alla_eod_path).loc[ref_date]
    mdconstant.columns = [item.replace('S_DQ_', '').lower() for item in mdconstant.columns]
    out_path = os.path.join(trade_root, 'hot_proof', ref_date.strftime('%Y%m%d'), 'mdconstant.h5')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    mdconstant.to_hdf(out_path, 'mdconstant', mode='w')
    return mdconstant

def prepare_minute_dummy(ref_date):
    ref_date = IO.str_date_parser(ref_date)
    minute_data = IO.read_data([ref_date.strftime('%Y%m%d'), ref_date.strftime('%Y%m%d')+'235959'], alt = kzz_stock_minute_path)
    clist = ['open','high','low','close','volume','amount']
    kzz_minute_data = minute_data[clist].reset_index(level = 1)
    stk_minute_data = minute_data[[x+'_stk' for x in clist]].reset_index(level = 1).rename(columns = {'Ticker':'kzz_code'})

    kzz_minute_data_v1 = kzz_minute_data.between_time(datetime.time(9,25), datetime.time(14,0)).reset_index().set_index(['dt','Ticker']).sort_index()
    kzz_minute_data_v2 = kzz_minute_data.between_time(datetime.time(14,1), datetime.time(14,49)).reset_index().set_index(['dt','Ticker']).sort_index()

    stk_minute_data = stk_minute_data.between_time(datetime.time(9,25), datetime.time(14,49))#1443
    stk_minute_data['Ticker'] = stk_minute_data.kzz_code.apply(lambda x:kzz_stock_mapping_dict[x])
    stk_minute_data = stk_minute_data.reset_index().set_index(['dt','Ticker']).drop(['kzz_code'], axis = 1)
    stk_minute_data = stk_minute_data.loc[~stk_minute_data.index.duplicated()]
    stk_minute_data.columns = [x.split('_')[0] for x in stk_minute_data.columns]

    out_path = os.path.join(trade_root, 'hot_proof', ref_date.strftime('%Y%m%d'))
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    kzz_minute_data_v1.to_hdf(os.path.join(out_path, 'ccbond_kline_1min_092500_140000.h5'), key = 'ccbond_kline_1min_092500_140000')
    kzz_minute_data_v2.to_hdf(os.path.join(out_path, 'ccbond_kline_1min_140000_144400.h5'), key = 'ccbond_kline_1min_140000_144400')
    stk_minute_data.to_hdf(os.path.join(out_path, 'ccbond_stock_kline_1min_092500_144300.h5'), key = 'ccbond_stock_kline_1min_092500_144300')
    return kzz_minute_data_v1, kzz_minute_data_v2, stk_minute_data

def prepare_hot_dummy(ref_date):
    prepare_mdconstant_dummy(ref_date)
    prepare_minute_dummy(ref_date)
    print('%s hot dummy done' % str(ref_date))


