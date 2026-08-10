import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *


def ts_max(data, d, mc = 1):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_max(data, window=d, min_count=mc, axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_max(data, window=d, min_count=mc, axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_max(data, window=d, min_count=mc, axis=0),
                               index=data.index, name=data.name)
    return output

def ts_min(data, d, mc = 1):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_min(data, window=d, min_count=mc, axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_min(data, window=d, min_count=mc, axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_min(data, window=d, min_count=mc, axis=0),
                               index=data.index, name=data.name)
    return output


#MinuteLongTerm
class fac_17(FactorGenerator):
    def __init__(self):
        required_columns=['close','tday']

        super(fac_17, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, ccc):
 
        tday_list = sorted(list(set(data['tday'].values)))
        di = pd.DataFrame(tday_list, index = tday_list).shift(int(sqrt(aaa)))
        di.iloc[0] = di.index[0]
        di = di.fillna(method = 'ffill')
        di = di.to_dict()[0]
        tday_new = data['tday'].apply(lambda x: di[x])
        templi = sorted(list(set(data['tday'])))
        di2 = {x: [data['close'].loc[data['tday'] == x].iloc[0], data['close'].loc[data['tday'] == x].index[0]] for x in templi}
        open_price = tday_new.apply(lambda x: di2[x][0])
        temp_index = pd.DataFrame(data['close'].index, index = data['close'].index)
        temp_len = pd.concat([temp_index, tday_new.apply(lambda x: di2[x][1])], axis = 1)
        length_temp = [len(data['close'].loc[item[1]: item[0]]) for item in temp_len.values]
        length = pd.Series(length_temp, index = data['close'].index)
        ret = (data['close'] - open_price) / length
        factor = ts_rank(ret, ccc * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return -factor