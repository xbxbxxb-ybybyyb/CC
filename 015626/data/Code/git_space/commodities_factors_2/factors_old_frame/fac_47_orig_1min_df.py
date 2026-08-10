import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *


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
class fac_47_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'volume', 'high', 'low', 'main_mask']

        super(fac_47_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        # 长江金工高频因子2：结构化反转因子
        # 因子主体由三部分组成：对数收益率，成交量倒数和收益波动率
        # 对数收益率代表动量，成交量倒数的逻辑是当多空力量悬殊时，股价会以很小的成交量迅速到达一个合理价位（这部分内容见研报），收益波动率的逻辑是只有当市场成交活跃时，趋势才强
        aaa = 75
        bbb = 15
        ccc = 20
        ddd = 30
        norm_price = (data['close'] + data['high'] + data['low']) / 3
        index_close = norm_price.rolling(2, min_periods = 1).mean()
        mask = data['main_mask']
        index_volume = data['volume'].rolling(2, min_periods = 1).mean()[mask].mean(axis = 1)
        
        log_ret = (index_close - index_close.shift(1))
        ret_std = ts_std(log_ret, aaa)[mask].mean(axis = 1)
        log_ret_weight = log_ret[mask].mean(axis = 1) / r(index_volume) * ret_std
        factor_raw = ts_sum(log_ret_weight, bbb)
        factor_mean = ts_truncated_ema_1(factor_raw, ccc*3, 1/(ccc+1))
        factor = ts_rank(factor_mean, 300 * ddd)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
