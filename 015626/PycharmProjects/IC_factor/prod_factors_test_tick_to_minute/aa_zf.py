from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
	sig_max = sig.rolling(window,min_periods=int(window/2)).max()
	sig_min = sig.rolling(window,min_periods=int(window/2)).min()
	return ((sig-sig_min)/(sig_max-sig_min))*2-1

class aa_zf(FactorGenerator):
	def __init__(self):
		required_columns = ['amount_spot']
		super(aa_zf, self).__init__(required_columns=required_columns)

	def on_bar(self, data):
		v1 = data['amount_spot'].rolling(3,min_periods=2).mean()
		v2 = data['amount_spot'].rolling(20,min_periods=10).mean()
		v2[abs(v2)<1e-8] = np.nan
		vra = v1/v2
		vra1 = vra.rolling(3,min_periods=2).mean()
		vra2 = vra.rolling(20,min_periods=10).mean()
		vra2[vra2<1e-8] = np.nan
		sig = vra2/vra1
		sig = sig.rolling(28,min_periods=5).mean()
		sig = pd.Series(bk.move_rank(sig.values,242*4, 121,axis=0),index=sig.index)
		sig.name = self.__class__.__name__
		return pd.DataFrame(sig)