import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.getData import get_recent_trade_date
from dataApi.stockList import trans_windcode2int
from xquant.factordata import FactorData
import pandas as pd
import numpy as np
import gc


class AddPreClose(object):
    def __init__(self, date=None, root_path='/data/group/800442/800319/strategy_HFfactor/'):
        date = date if date else get_recent_trade_date(dividing_point=7)
        code_list = pd.read_pickle(f'{root_path}/{date}/DateCode/code_list.pkl')
        fd = FactorData()
        df = fd.get_factor_value('Basic_factor', None, [
            str(date)], ['mdc_pre_close'])['mdc_pre_close'].dropna().rename(
            'pre_close').reset_index().set_index('stock').drop('mddate', axis=1).iloc[:, 0]
        df.index = df.index.map(trans_windcode2int)
        df = df.reindex(code_list).values[None, :]
        np.save(f'{root_path}/{date}/TmrLowFreq/pre_close.npy', df)
        del fd
        gc.collect()
