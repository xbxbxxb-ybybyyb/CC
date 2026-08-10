from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
	sig_max = sig.rolling(window,min_periods=int(window/2)).max()
	sig_min = sig.rolling(window,min_periods=int(window/2)).min()
	return ((sig-sig_min)/(sig_max-sig_min))*2-1

class ss1_zf(FactorGenerator):
	def __init__(self):
		required_columns = ['close_spot','high_spot']
		super(ss1_zf, self).__init__(required_columns=required_columns)

	def on_bar(self, data):
		rtn = data['close_spot']/data['close_spot'].shift(1)-1
		vol = rtn.rolling(60,min_periods=30).std()
		ret = data['close_spot']/(data['high_spot'].shift(1).rolling(60,min_periods=30).max())-1
		sig = ret/vol
		sig = pd.Series(bk.move_rank(sig.values,242*5, 121,axis=0),index=sig.index)
		sig = rolling_normalize(sig,242*5)
		sig.name = self.__class__.__name__
		return pd.DataFrame(sig)