from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
	sig_max = sig.rolling(window,min_periods=int(window/2)).max()
	sig_min = sig.rolling(window,min_periods=int(window/2)).min()
	return ((sig-sig_min)/(sig_max-sig_min))*2-1

def ts_rank(test, n=1200):
		a = bk.move_rank(test.iloc[:,0], n, min_count=1)
		aa = pd.DataFrame(a)
		aa.index = test.index
		aa.columns = test.columns
		return aa
		
class vv_zf(FactorGenerator):
	def __init__(self):
		required_columns = ['amount_spot']
		super(vv_zf, self).__init__(required_columns=required_columns)
	
	
	def on_bar(self, data):
		v1 = data['amount_spot'].rolling(3,min_periods=2).mean()
		v2 = data['amount_spot'].rolling(20,min_periods=10).mean()
		sig = v1-v2
		sig = rolling_normalize(sig, 30)
		sig = ts_rank(sig.to_frame())
		sig = sig.iloc[:, 0]
		sig = -sig.rolling(15,min_periods=5).mean()
		sig.name = self.__class__.__name__
		return pd.DataFrame(sig)
