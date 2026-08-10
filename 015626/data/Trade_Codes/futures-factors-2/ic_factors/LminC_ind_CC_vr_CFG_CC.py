import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def section_rank_np(data, pct=False):
    # 基于numpy的截面排序，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis = 1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort
def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output
class LminC_ind_CC_vr_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        stk_close = data['close_preadj'][-216:].values
        stk_ret = stk_close[1:] / stk_close[:-1] - 1
        stk_volatility = bk.move_std(stk_ret, window = 30, min_count = 15, axis=0)
        
        mask = 2 * section_rank_np(stk_volatility, pct = True)[-185:] - 1
        lltc_ind_r = -1 * bk.move_min(data['low_preadj'][-185:].values, 180, min_count=90, axis = 0) / data['close_preadj'][-185:].values
        factor = np.nansum(lltc_ind_r*mask, axis = 1)[-5:]
        factor = np.nanmean(factor)
        return factor 