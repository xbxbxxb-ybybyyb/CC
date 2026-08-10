import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
from multifactor.IO import IO
import pandas as pd
import numpy as np

def get_univ_1(start_date, end_date):
    data = IO.read_data(alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5')
    multip = pd.read_csv('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/INFO/multiplier.csv',index_col=0)
    data_new = data.reset_index()
    data_new = data_new[data_new['Ticker'].isin(multip.index)].set_index('Ticker')
    data_new = data_new.join(multip)
    data_new['amt'] = data_new['settle']*data_new['volume']*data_new['multiplier']
    data_new = data_new[data_new['amt'] > 1e10]
    univ = data_new.reset_index().set_index(['dt','Ticker'])['close'].sort_index()
    univ.loc[:] = True
    univ = univ.unstack().shift(1).stack()
    univ.name = 'amt_1e10'
    univ = univ.to_frame()
    univ.to_hdf('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/UNIV/test.h5',key = 'univtest')
    return

def get_univ_2(start_date, end_date):
    data_all = IO.read_data([start_date, end_date],alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_CHINA_FUTURE_DAILY.h5')
    amt_max = data_all.groupby(['dt','prod_id'])['amount'].max()
    univ = amt_max[amt_max > 1e6]
    univ.loc[:] = True
    univ = univ.unstack().shift(1)
    univ.columns.name = 'Ticker'
    univ = pd.DataFrame(univ.stack(),columns = ['amt_1e10'])
    univ.to_hdf('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/UNIV/test_amt10.h5',key = 'test_amte10')
    return

if __name__ == '__main__':
    get_univ_2(20100101,20250501)