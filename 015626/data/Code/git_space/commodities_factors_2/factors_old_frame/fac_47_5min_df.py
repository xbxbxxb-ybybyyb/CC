import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from rolling_adj import *

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))



# wsc_1_spot_if
class fac_47_5min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'volume', 'high', 'low', 'main_mask', 'BidAskSpreadMean']

        super(fac_47_5min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        # 长江金工高频因子2：结构化反转因子
        # 因子主体由三部分组成：对数收益率，成交量倒数和收益波动率
        # 对数收益率代表动量，成交量倒数的逻辑是当多空力量悬殊时，股价会以很小的成交量迅速到达一个合理价位（这部分内容见研报），收益波动率的逻辑是只有当市场成交活跃时，趋势才强
        aaa = 3
        bbb = 10
        ccc = 70
        ddd = 10

        mask = data['main_mask']
        coef_temp = (data['close'].diff().rolling(30,min_periods = 1).std() / r(data['BidAskSpreadMean'].rolling(30,min_periods = 1).mean().copy()))[data['main_mask']].mean(axis = 1)
        coef = coef_temp.copy()
        coef[coef_temp > 10] =0.1
        coef[(coef_temp > 6) & (coef_temp <= 10)] = 0.3
        coef[(coef_temp <= 6) & (coef_temp > 4)] = 1
        coef[(coef_temp <= 4) & (coef_temp > 3)] = 2
        coef[(coef_temp <= 3)] = 5
        
        norm_price = (data['close'] + data['high'] + data['low']) / 3
        index_close = norm_price.rolling(2, min_periods = 1).mean()
        index_volume = data['volume'].rolling(2, min_periods = 1).mean().sum(axis = 1)
        
        log_ret = (index_close - index_close.shift(1)).mean(axis = 1)
        ret_std = ts_std(log_ret, aaa)
        log_ret_weight = log_ret / r(index_volume) * ret_std
        factor_raw = irr_ma(log_ret_weight, bbb)
        factor_mean = rolling_mean2_adj(factor_raw, np.sqrt(coef), ccc) + ts_truncated_ema_1(factor_raw, ccc*3, 1/(ccc+1))
        
        
        factor = ts_rank(factor_mean, 300 * ddd)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
