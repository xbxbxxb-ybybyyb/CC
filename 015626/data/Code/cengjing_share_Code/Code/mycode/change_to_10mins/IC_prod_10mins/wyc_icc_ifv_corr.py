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
        N = 30
        s = high.rolling(N, min_periods=N//2).std()
        f = close.rolling(N, min_periods=N//2).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(N, min_periods=N//2).cov(close) / (s * f)
        factor = -1 * factor
        factor = rolling_norm(factor, 3 * 230)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')

        return factor