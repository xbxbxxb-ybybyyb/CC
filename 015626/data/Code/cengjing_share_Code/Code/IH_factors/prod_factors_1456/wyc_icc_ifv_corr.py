from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_icc_ifv_corr(FactorGenerator):
    def __init__(self):
        required_columns=['close','volume_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_icc_ifv_corr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        high = df['volume_if']
        close = df['close']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(60, min_periods=30).cov(close) / (s * f)
        factor = -1 * factor
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')

        return factor