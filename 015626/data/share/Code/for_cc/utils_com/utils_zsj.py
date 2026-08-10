
import numpy as np
import pandas as pd
import talib as ta
import bottleneck as bk


def place_back_format(dat_mat,dat_orig):
    if isinstance(dat_orig,pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat,index=dat_orig.index,columns=dat_orig.columns)
    elif isinstance(dat_orig,pd.Series):
        dat_fmt = pd.Series(dat_mat,index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_corr(x1, x2, window):
    corr_np = ta.CORREL(x1.values, x2.values, timeperiod=window)
    corr = place_back_format(corr_np,x1)
    return corr

def calc_ts_pct(ts,ts_pct_win=20,min_pct=0.9,force_range=False):
    min_win = int(min_pct*ts_pct_win)
    ts_pct_np = bk.move_rank(ts,ts_pct_win,min_win)
    if force_range:
        ts_pct_np = (ts_pct_np + 1)/2
    ts_pct = place_back_format(ts_pct_np,ts)
    return ts_pct


def calc_ts_norm(ts,roll_win=20,norm_type='min_max',min_pct=0.9):
	if len(ts)<roll_win:
		print ('calc_ts_pct error: ts len too short: %d/%d'%(len(ts),roll_win))
		raise Exception
	min_periods = int(min_pct*roll_win)
	if norm_type == 'pct':
		ts_norm = calc_ts_pct(ts,roll_win,min_pct)
	elif norm_type == 'min_max':
		ts_max =  ts.rolling(roll_win,min_periods=min_periods).max()
		ts_min =  ts.rolling(roll_win,min_periods=min_periods).min()
		ts_norm = (ts-ts_min)/(ts_max - ts_min)
	elif norm_type == 'zscore':
		ts_mean =  ts.rolling(roll_win,min_periods=min_periods).mean()
		ts_std =  ts.rolling(roll_win,min_periods=min_periods).std()
		ts_norm = (ts - ts_mean)/ts_std
	return ts_norm


######### calc factor helper
def calc_change_helper(score_raw,short_win,long_win,ts_pct_win,sign=1,min_pct=0.9):
	score_change_raw = sign*(score_raw.rolling(short_win,int(min_pct*short_win)).mean() - score_raw.rolling(long_win,int(min_pct*long_win)).mean())
	score_change = calc_ts_pct(score_change_raw,ts_pct_win)
	return score_change

def calc_std_helper(score_raw,std_win,ts_pct_win,min_pct=0.9):
	score_std_raw = score_raw.rolling(std_win,int(min_pct*std_win)).std()
	score_std = calc_ts_pct(score_std_raw,ts_pct_win)
	return score_std

def calc_ma_helper(score_raw,ma_win,ts_pct_win,min_pct=0.9):
	score_ma_raw = score_raw.rolling(ma_win,int(min_pct*ma_win)).mean()
	score_ma = calc_ts_pct(score_ma_raw,ts_pct_win)
	return score_ma


########## technical operator

def REF(x, n):
	res = x.shift(n)
	return res


def IF(cond, a, b):
	if isinstance(b, int):
		b = pd.Series([b] * len(a), index=a.index)
	res = b.copy()
	res[cond] = a
	return res


def SUM(x, n):
	res = x.rolling(n, 1).sum()
	return res


def CUMSUM(x):
	res = x.cumsum()
	return res


def MAX(x, n):
	if isinstance(n, int) and n > 0:
		res = x.rolling(n, 1).max()
	else:
		res = x.copy()
		res[n > x] = n
	return res


def MIN(x, n):
	if isinstance(n, int) and n > 0:
		res = x.rolling(n, 1).min()
	else:
		res = x.copy()
		res[n < x] = n
	return res


def ABS(x):
	res = np.abs(x)
	return res


def MA(x, n):
	res = x.rolling(n, 1).mean()
	return res


def EMA(x, n):
	res = pd.Series(ta.EMA(x.values, n), index=x.index)
	# res = x.rolling(n,int(n*0.5)).apply(lambda x: pd.Series(x).ewm(halflife=half_life).mean().values[-1])
	return res


def SMA(x, n, m):
	"""
    Y(t) = (A(t)*m + Y(t-1)*(n-m))/n
    fill value"""
	x1 = x.copy()
	x = pd.DataFrame(x)
	mask_mat = np.isfinite(x).values
	tmp_mat = x.fillna(method='ffill').values
	x_num = x.shape[0]
	res_mat = np.full_like(x, fill_value=np.nan)
	res_mat[0, :] = tmp_mat[0, :]
	for i in range(1, x_num):
		mask_i = mask_mat[i, :]
		mask_i_prev = mask_mat[i - 1, :]
		res_mat[i, :] = (tmp_mat[i, :] * m + res_mat[i - 1, :] * (n - m)) / n
		res_mat[i, ~mask_i] = tmp_mat[i - 1, ~mask_i]  # no current use prev
		res_mat[i, ~mask_i_prev] = tmp_mat[i, ~mask_i_prev]  # no prev use current
	if isinstance(x1, pd.DataFrame):
		res = pd.DataFrame(res_mat, index=x.index, columns=x.columns)
	else:
		res = pd.Series(res_mat.flatten(), index=x.index)
	return res


def WMA(x, n):
	res = pd.Series(ta.SMA(x.values, n), index=x.index)
	return res


def DMA(x, n):
	res = pd.Series(ta.DMA(x.values, n), index=x.index)
	return res


#############


