from factor_generator import FactorGenerator
from operators_wyc import *


class wyc_ihcv_corr(FactorGenerator):
    def __init__(self):
        required_columns=['close_ih','volume_ih', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ihcv_corr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        # factor = correlation(df.close_ih, df.volume_ih, 30)
        mask = df['recent_month_mask']
        high = df['volume_ih']
        close = df['close_ih']
        N = 10
        s = high.rolling(N, min_periods=N//2).std()
        f = close.rolling(N, min_periods=N//2).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(N, min_periods=N//2).cov(close) / (s * f)
        factor = -1 * mean(factor, N)
        factor = factor.fillna(method='ffill')
        factor = ts_rank(factor, 2*237)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]

        factor[factor>=0.5]=0
        
        return factor