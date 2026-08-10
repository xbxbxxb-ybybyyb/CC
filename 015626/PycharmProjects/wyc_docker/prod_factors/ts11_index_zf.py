from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk
from statsmodels.stats.weightstats import DescrStatsW

def weighted_stats_along_axis(raw, weight, method, axis=0):
	assert raw.shape[axis] == len(weight)
	if isinstance(raw, pd.DataFrame):
		return raw.apply(nan_weighted_stats, axis=axis, w=weight, method=method)
	elif isinstance(raw, np.ndarray):
		return np.apply_along_axis(nan_weighted_stats, axis, raw, w=weight, method=method)

def rolling_ewm(pd_raw, window, half_life, method='mean', min_weight=0.5):
	# Fixed window rolling ewma along axis 0 for DataFrame
	if isinstance(pd_raw, pd.DataFrame):
		x_mat = pd_raw.values
	elif isinstance(pd_raw, np.ndarray):
		x_mat = pd_raw
		assert len(x_mat.shape) == 2
	else:
		raise NotImplementedError
	weight = weight_decay(half_life, window)
	row_num, col_num = x_mat.shape
	y_mat = np.full_like(x_mat, fill_value=np.nan, dtype=np.double)
	dummy_weight = (np.ones([window, col_num]).T * weight).T
	for i in range(window, row_num+1):
		x_sliced = x_mat[i-window:i, :]
		x_mask = np.isfinite(x_sliced)
		col_weight = (x_mask * dummy_weight).sum(axis=0)
		col_mask = col_weight >= min_weight
		if not np.all(~col_mask):
			y_mat[i-1, col_mask] = weighted_stats_along_axis(x_sliced[:, col_mask],
															 weight=weight, method=method, axis=0)
	if isinstance(pd_raw, pd.DataFrame):
		res = pd.DataFrame(y_mat, index=pd_raw.index, columns=pd_raw.columns)
	else:
		res = y_mat
	return res

def weight_decay(half_life, total_len):
	# return exponential weights with last element the biggest
	res = np.array([0.5 ** ((total_len - i) / half_life) for i in range(total_len)])
	return res / np.sum(res)

def nan_weighted_stats(x, w, method=None):
	# weighted statistics cannot be simply computed by numpy
	x = np.ma.masked_invalid(x)
	_x = x.data[~x.mask]
	_w = w[~x.mask]
	assert not np.isnan(_w).any()
	_w = _w * (len(_w) / np.sum(_w))
	inst = DescrStatsW(_x, weights=_w)
	if method is None:
		return inst
	else:
		if len(_x) == 0:
			return np.nan
		else:
			return getattr(inst, method)

def rolling_normalize(sig, window = 100):
	sig_max = sig.rolling(window,min_periods=int(window/2)).max()
	sig_min = sig.rolling(window,min_periods=int(window/2)).min()
	return ((sig-sig_min)/(sig_max-sig_min))*2-1

def mean(A,d):
	output = A.rolling(d,min_periods=int(round(d/2))).mean()
	output.iloc[:d-1] = np.nan
	return output

def delay(A,n):
	return A.shift(periods=n)

class ts11_index_zf(FactorGenerator):
	def __init__(self):
		required_columns = ['close_spot']
		super(ts11_index_zf, self).__init__(required_columns=required_columns)

	def on_bar(self, data):
		tmp = data['close_spot'] - delay(data['close_spot'], 10)
		factor = rolling_ewm(pd.DataFrame(tmp),300,half_life=12.5)
		factor = factor[factor.columns[0]]
		factor = mean(factor, 15)
		factor = rolling_normalize(factor,window=242*4)
		factor[factor<0]=np.nan
		factor.name = self.__class__.__name__
		return pd.DataFrame(factor)

		