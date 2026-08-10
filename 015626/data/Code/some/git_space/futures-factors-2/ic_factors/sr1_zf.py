import bottleneck as bk
import numpy as np
from future_factor import FutureFactor

class sr1_zf(FutureFactor):
	'''
	期货类因子
	'''
	data_type = 'Future'
	days_past = 3
	data_dict = dict()
	data_dict['Index_Id'] = {'000905.SH':['close','low']}
	normalize_size = 0 # normalize所用历史数据长度
	normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#	num_range = '(-0.5,1]'

	def calculate(self, data):
		close = data['close_000905.SH'].values
		rtn = close[1:]/close[:-1]-1
		vol_ts = bk.move_std(rtn,window = 60, min_count = 30, ddof = 1)
		vol_ts[abs(vol_ts)<1e-8] = np.nan
		low = data['low_000905.SH'].values
		low = low[:-1]
		lowmin = bk.move_min(low, window = 60, min_count = 30)
		ret = close[1:]/lowmin-1
		sig = ret/vol_ts
		sig = bk.move_rank(sig, window = 242*2, min_count = 242)[-5:]
		sig = np.nanmean(sig)
		return sig