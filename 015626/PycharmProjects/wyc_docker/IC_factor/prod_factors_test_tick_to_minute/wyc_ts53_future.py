from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts53_future(FactorGenerator):
	def __init__(self):

		required_columns=['close','volume','position']
		lookback_bars=2000
		super(wyc_ts53_future, self).__init__(
								  required_columns=required_columns,
								  lookback_bars=lookback_bars)

	def on_bar(self, df):

		N = 10
		turnover = df.volume / df.position
		returns = df.close.pct_change(fill_method=None)

		# high = data['high_if']
		# close = data['close_if']
		s = turnover.rolling(N, min_periods=N//2).std()
		f = returns.rolling(N, min_periods=N//2).std()
		s[abs(s) < 1e-8] = np.nan
		f[abs(f) < 1e-8] = np.nan
		factor = -1 * turnover.rolling(N, min_periods=N//2).cov(returns) / (s * f)

		# factor = -1 * correlation(turnover,returns,N).replace([np.inf,-np.inf],np.nan)
		factor = ts_rank(factor, 15)
		factor = mean(factor, 100)

		factor = factor.to_frame()

		def rolling_normalize(df, x):
			def normalize(dd):
				a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
				b = (a - 0.5) * 2
				return b

			return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

		columnname = self.__class__.__name__
		factor.columns = [columnname]
		factor = factor.fillna(method='ffill')
		factor[columnname] = rolling_normalize(factor, 5 * 242)
		factor[factor<=-0.5] = np.nan
		return factor