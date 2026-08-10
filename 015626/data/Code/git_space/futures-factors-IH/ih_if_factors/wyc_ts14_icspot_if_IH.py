import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

class wyc_ts14_icspot_if_IH(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1210 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
   
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        close = df['close_000016.SH'][-141:]
        factor = np.where(close > close.shift(1), ts_std(close, 50), 0)[-90:]
        factor = bk.move_rank(factor, 60, 30, axis = 0)[-30:]
        factor = np.nanmean(factor)
        return factor