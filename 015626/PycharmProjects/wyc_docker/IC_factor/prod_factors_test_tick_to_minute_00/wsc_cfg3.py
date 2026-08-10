import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_cfg3(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg3, self).__init__(required_columns=['close_zz500', 'close_spot', 'weight_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股数量
        index_return = data['close_spot'].pct_change(periods=60, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=60, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))  # .skew(axis=1)
        excess_return_weight = data['weight_zz500'][excess_return < 0].sum(axis=1)
        excess_return_weight = excess_return_weight.rolling(10, min_periods=5).mean()

        factor = excess_return_weight.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 1200)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
