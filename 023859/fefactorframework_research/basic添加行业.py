import pandas as pd
import numpy as np
import os
from h5data.IO import IO
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

dic_change_ticker = {
    '000043.SZ': '001914.SZ',
    '000022.SZ': '001872.SZ',
    '200022.SZ': '201872.SZ',
    '601313.SH': '601360.SH',
    '300114.SZ': '302132.SZ',
}

basic_df = pd.read_hdf('/data/user/023859/factor_zooZZmkt/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5')
sw_col_dict = {}
for dt in tqdm(basic_df.index.get_level_values(0).unique()):
    date = dt.strftime('%Y%m%d')
    if date < '20211213':
        flag = 'SW'
    else:
        flag = 'SW2021'

    ZZ1000_sw1 = s.hsi(list(basic_df.xs(dt,level=0).index), date, flag, 1).set_index('stock')
    for old_ticker in dic_change_ticker.keys():
        if old_ticker in ZZ1000_sw1.index and ZZ1000_sw1.loc[old_ticker,'industry_code'] is np.nan:
            new_ticker = dic_change_ticker[old_ticker]
            df_sw1_new = s.hsi([new_ticker], date, flag, 1).set_index('stock')
            ZZ1000_sw1.loc[old_ticker,'industry_code'] = df_sw1_new.loc[new_ticker,'industry_code']
            ZZ1000_sw1.loc[old_ticker,'industry_name'] = df_sw1_new.loc[new_ticker,'industry_name']

    sw_col_dict[dt] = pd.to_numeric(ZZ1000_sw1['industry_code']).astype('Int64')

sw_col_series = pd.concat(sw_col_dict, axis=0).sort_index()
sw_col_series.index.names = ['dt','Ticker']
basic_df = basic_df.join(sw_col_series.rename('industry_code'),how='left')

basic_df['industry_code'] = basic_df['industry_code'].fillna(-1)
local_factor_path_basic = '/data/user/023859/factor_zooZZmkt/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5'
if not os.path.exists(local_factor_path_basic):
    IO.pd_hdf5_writer(basic_df, hdf5=local_factor_path_basic, dataset='neptunelong')
else:
    IO.pd_hdf5_writer(basic_df, hdf5=local_factor_path_basic, dataset='neptunelong', override=True)

public_factor_path_basic = '/dfs/group/800463/public/projectZZmkt_public/factor_lib/Basic_closed_hf_finish_20160101_20201231.h5'
if not os.path.exists(public_factor_path_basic):
    IO.pd_hdf5_writer(basic_df.loc[:pd.Timestamp('20201231')], hdf5=public_factor_path_basic, dataset='neptunelong')
else:
    IO.pd_hdf5_writer(basic_df.loc[:pd.Timestamp('20201231')], hdf5=public_factor_path_basic, dataset='neptunelong', override=True)