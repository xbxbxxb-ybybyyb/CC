import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime

class wsc17_cfg_ret_as_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # 长江金工高频因子八，偏度因子
        # 计算close的偏度，偏度＞0时，大于价格均值的价格比小于价格均值的价格少，个股成交集中在价格相对较低的水平，反之亦然，因此认为偏度越小的股票未来价格更可能上升。
        # 取当分钟rolling_skew前50%的股票，计算它们的过去一分钟return，作为因子值，再套相应的mask，因为每期选出的票都不一样，所以为了时序上可比，要做一定的归一化处理。
        stk_close = data['close_preadj'][-75:]
        stk_amount = data['amount'][-45:]
        stk_ret = stk_close.pct_change()
        stk_skew = stk_close.rolling(30, min_periods=15).skew()
        skew_long = stk_skew.gt(stk_skew.quantile(0.5, axis=1), axis=0)
        factor_init = stk_ret[skew_long]

        factor_raw = (factor_init[-45:] * stk_amount).sum(axis=1).values / (stk_amount * skew_long[-45:]).sum(axis=1).replace(0, np.nan).values
        factor = np.nanmean(factor_raw)
     
        return factor