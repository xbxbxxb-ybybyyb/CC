from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
	sig_max = sig.rolling(window,min_periods=int(window/2)).max()
	sig_min = sig.rolling(window,min_periods=int(window/2)).min()
	return ((sig-sig_min)/(sig_max-sig_min))*2-1

class rtt_zf(FactorGenerator):
	def __init__(self):
		required_columns = ['close_spot','low_spot']
		super(rtt_zf, self).__init__(required_columns=required_columns)

	def on_bar(self, data):
		sig = data['close_spot']/data['low_spot'].shift(1).rolling(60, min_periods=30).min()
		sig = pd.Series(bk.move_rank(sig.values,242*2, 121,axis=0),index=sig.index)
		sig = sig.rolling(5,min_periods=2).mean()
		sig[sig<-0.8]=np.nan
		sig.name = 'rtt'
		sig.name = self.__class__.__name__
		return pd.DataFrame(sig)
