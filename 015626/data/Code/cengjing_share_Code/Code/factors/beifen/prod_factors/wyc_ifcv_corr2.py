from factor_generator import FactorGenerator
from operators_wyc import *


class wyc_ifcv_corr2(FactorGenerator):
    def __init__(self):
        required_columns=['close_if','volume_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ifcv_corr2, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        # factor = correlation(df.close_if, df.volume_if, 30)
        mask = df['recent_month_mask']
        high = df['volume_if']
        close = df['close_if']
        s = high.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * mean(factor, 10)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 3 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]

        factor[factor<-0.5]=0
        return factor