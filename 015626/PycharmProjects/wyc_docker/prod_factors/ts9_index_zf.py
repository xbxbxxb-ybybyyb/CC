from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
	sig_max = sig.rolling(window,min_periods=int(window/2)).max()
	sig_min = sig.rolling(window,min_periods=int(window/2)).min()
	return ((sig-sig_min)/(sig_max-sig_min))*2-1

def sma(A,n,m):
	output = A.ewm(alpha=m/n,adjust=False).mean()
	return output

def delay(A,n):
	return A.shift(periods=n)

class ts9_index_zf(FactorGenerator):
	def __init__(self):
		required_columns = ['close_spot']
		super(ts9_index_zf, self).__init__(required_columns=required_columns)

	def on_bar(self, data):
		factor = sma(data['close_spot'] / delay(data['close_spot'], 20), 20, 1)
		factor = rolling_normalize(factor,242*4)
		factor[factor<0]=np.nan
		factor.name = self.__class__.__name__
		return pd.DataFrame(factor)