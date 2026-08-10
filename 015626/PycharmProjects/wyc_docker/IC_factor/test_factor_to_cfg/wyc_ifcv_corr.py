from factor_generator import FactorGenerator
from operators_wyc import *

def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_ifcv_corr(FactorGenerator):
    def __init__(self):
        required_columns=['close_if','volume_if']
        lookback_bars=2000
        super(wyc_ifcv_corr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        # factor = correlation(df.close_if, df.volume_if, 30)

        high = df['volume_if']
        close = df['close_if']
        s = high.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(30, min_periods=15).cov(close) / (s * f)

        factor = -1 * ts_mean(factor, 30)
        return factor