# utility


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

def calc_ts_pct(ts_dat,roll_win=20,min_pct=1,force_range=True):
	min_win = int(min_pct*roll_win)
	ts_dat_pct_np = bk.move_rank(ts_dat,window=roll_win,min_count=min_win,axis=0)
	if force_range:
		ts_dat_pct_np = (ts_dat_pct_np + 1)/2
	ts_dat_pct = place_back_format(ts_dat_pct_np,ts_dat)
	return ts_dat_pct

def calc_change_helper(score_raw,short_win,long_win,ts_pct_win,sign=1,min_pct=0.9):
	score_change_raw = sign*(score_raw.rolling(short_win,int(min_pct*short_win)).mean() - score_raw.rolling(long_win,int(min_pct*long_win)).mean())
	score_change = calc_ts_pct(score_change_raw,ts_pct_win,min_pct=min_pct)
	return score_change

def calc_std_helper(score_raw,std_win,ts_pct_win,min_pct=0.9):
	score_std_raw = score_raw.rolling(std_win,int(min_pct*std_win)).std()
	score_std = calc_ts_pct(score_std_raw,ts_pct_win)
	return score_std

def calc_ma_helper(score_raw,ma_win,ts_pct_win,min_pct=0.9):
	score_ma_raw = score_raw.rolling(ma_win,int(min_pct*ma_win)).mean()
	score_ma = calc_ts_pct(score_ma_raw,ts_pct_win,min_pct=min_pct)
	return score_ma


#############
## prep data 

stk_ret = stk_close/stk_close.shift(1) - 1
up_mask = stk_ret>0
down_mask = stk_ret<0
stk_up_cnt = up_mask.sum(axis=1)
stk_down_cnt = down_mask.sum(axis=1)

cut_line = stk_amt.median(axis=1)
active_mask = stk_amt.subtract(cut_line,axis=0)>=0
inactive_mask = stk_amt.subtract(cut_line,axis=0)<0

#############

# 1.
# vol_a2p
factor_name = 'volatility_a2p'
ma_win = 20
ts_pct_win = 2400
min_pct = 0.92

roll_win = 15
min_periods = int(roll_win*0.5)
stk_vol = stk_ret.rolling(roll_win,min_periods).std()
vol_active_raw = stk_vol[active_mask].mean(axis=1)
vol_inactive_raw = stk_vol[inactive_mask].mean(axis=1)
volatility_a2p_raw = vol_active_raw - vol_inactive_raw
volatility_a2p = calc_ma_helper(volatility_a2p_raw,ma_win,ts_pct_win,min_pct)
ts_factor_quick(volatility_a2p,price,factor_name,layers=5)

# 2.
factor_name = 'stk2idx_trade_strength'
roll_win = 30
ma_win = 40
ts_pct_win = 4800
min_pct = 0.8
min_periods = int(min_pct*roll_win)
abs_dis = np.abs(stk_close - stk_close.shift(1))
stk_tot_dis = abs_dis.rolling(roll_win,min_periods).sum()
stk_final_dis = stk_close - stk_close.shift(roll_win)
stk_trade_strength = stk_final_dis / stk_tot_dis
stk2idx_trade_strength_raw = stk_trade_strength.mean(axis=1)
stk2idx_trade_strength = calc_ma_helper(stk2idx_trade_strength_raw,ma_win,ts_pct_win,min_pct)
ts_factor_quick(stk2idx_trade_strength,price,factor_name,layers=5)

# 3. 
factor_name = 'trade_strength_a2p'
ma_win = 30
ts_pct_win = 4800
min_pct = 0.9
ts_active_raw = stk_trade_strength[active_mask].mean(axis=1)
ts_inactive_raw = stk_trade_strength[inactive_mask].mean(axis=1)
ts_a2p_raw = ts_active_raw - ts_inactive_raw
trade_strength_a2p = calc_ma_helper(ts_a2p_raw,ma_win,ts_pct_win,min_pct)
ts_factor_quick(trade_strength_a2p,price,factor_name,layers=5)

# 4.
factor_name = 'high_low_diff_stk2idx'
roll_win = 30
ma_win = 30
ts_pct_win = 2400
min_periods = int(0.5*roll_win)
high_open_diff = stk_high - stk_open
open_low_diff = stk_open - stk_low
high_low_diff_stk = high_open_diff.rolling(roll_win,min_periods).sum() - open_low_diff.rolling(roll_win,min_periods).sum()
high_low_diff_stk2idx_raw = high_low_diff_stk.mean(axis=1)
high_low_diff_stk2idx = calc_ma_helper(high_low_diff_stk2idx_raw,ma_win,ts_pct_win,min_pct)
ts_factor_quick(high_low_diff_stk2idx,price,factor_name,layers=5)

# 5.
factor_name = 'high_low_diff_a2p'
ma_win = 30 
ts_pct_win = 2400
min_pct = 0.9
high_low_diff_active_raw = high_low_diff_stk[active_mask].mean(axis=1)
high_low_diff_inactive_raw = high_low_diff_stk[inactive_mask].mean(axis=1)
high_low_diff_a2p_raw = high_low_diff_active_raw - high_low_diff_inactive_raw
high_low_diff_a2p = calc_ma_helper(high_low_diff_a2p_raw,ma_win,ts_pct_win,min_pct)
ts_factor_quick(high_low_diff_a2p,price,factor_name,layers=5)

# 6.
factor_name = 'stk2idx_amt_u2d'
ma_win_fac = 30 
min_pct_fac = 0.1
min_periods_fac = int(ma_win*min_pct_fac)
stk_amt_up = stk_amt[up_mask].rolling(ma_win_fac,min_periods_fac).sum()
stk_amt_down = stk_amt[down_mask].rolling(ma_win_fac,min_perimin_periods_facods).sum()
stk_amt_u2d = (stk_amt_up - stk_amt_down) 
stk2idx_amt_u2d_raw = stk_amt_u2d.mean(axis=1)
ma_win = 30
ts_pct_win = 2400
min_pct = 0.9
stk2idx_amt_u2d_raw = stk_amt_u2d.mean(axis=1)
stk2idx_amt_u2d = calc_ma_helper(stk2idx_amt_u2d_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk2idx_amt_u2d,price,factor_name,layers=5)

# 7.
factor_name = 'stk_h2c_a2p'
ma_win = 30
ts_pct_win = 2400
min_pct = 0.9
stk_h2c_active_raw = stk_high2close_raw[active_mask].mean(axis=1)
stk_h2c_inactive_raw = stk_high2close_raw[inactive_mask].mean(axis=1)
stk_h2c_a2p_raw = stk_h2c_active_raw - stk_h2c_inactive_raw
stk_h2c_a2p = calc_ma_helper(-1*stk_h2c_a2p_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk_h2c_a2p,price,factor_name,layers=5)

# 8.
factor_name = 'stk_l2c_a2p'
ma_win = 30
ts_pct_win = 2400
min_pct = 0.9
stk_l2c_active_raw = stk_low2close_raw[active_mask].mean(axis=1)
stk_l2c_inactive_raw = stk_low2close_raw[inactive_mask].mean(axis=1)
stk_l2c_a2p_raw = stk_l2c_active_raw - stk_l2c_inactive_raw
stk_l2c_a2p = calc_ma_helper(-1*stk_l2c_a2p_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk_l2c_a2p,price,factor_name,layers=5)

# 9.
factor_name = 'stk_l2c_a2p_chg'
ma_win = 30
short_win = 20
long_win = 90
ts_pct_win = 2400
min_pct = 0.9
stk_l2c_active_raw = stk_low2close_raw[active_mask].mean(axis=1)
stk_l2c_inactive_raw = stk_low2close_raw[inactive_mask].mean(axis=1)
stk_l2c_a2p_raw = -1*(stk_l2c_active_raw - stk_l2c_inactive_raw)
stk_l2c_a2p_chg = calc_change_helper(stk_l2c_a2p_raw,short_win,long_win,ts_pct_win)        
ts_factor_quick(stk_l2c_a2p_chg,price,factor_name,layers=5)

# 10.
factor_name = 'stk2indx_midret_amt'
roll_win_fac = 15
min_pct = 0.9
ma_win = 20
min_periods = int(min_pct*roll_win_fac)
stk_mid = (stk_high + stk_low)/2
stk_mid_ret = stk_mid/stk_mid.shift(1) - 1
stk_midret_amt_raw = stk_mid_ret * stk_amt
stk_midret_amt_raw_ma = stk_midret_amt_raw.rolling(roll_win_fac,min_periods).mean()
stk2indx_midret_amt_raw = stk_midret_amt_raw_ma.mean(axis=1)
stk2indx_midret_amt = calc_ma_helper(stk2indx_midret_amt_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk2indx_midret_amt,price,factor_name,layers=5)


# 11.
factor_name = 'stk2indx_midret_amt_a2p'
roll_win_fac = 15
min_pct = 0.9
ma_win = 30
ts_pct_win = 2400
min_periods = int(min_pct*roll_win_fac)
stk_mid = (stk_high + stk_low)/2
stk_mid_ret = stk_mid/stk_mid.shift(1) - 1
stk_midret_amt_raw = stk_mid_ret * stk_amt
stk_midret_amt_raw_ma = stk_midret_amt_raw.rolling(roll_win_fac,min_periods).mean()
active_raw = stk_midret_amt_raw_ma[active_mask].mean(axis=1)
inactive_raw = stk_midret_amt_raw_ma[inactive_mask].mean(axis=1)
stk_midret_amt_a2p_raw = active_raw - inactive_raw
stk2indx_midret_amt_a2p = calc_ma_helper(stk_midret_amt_a2p_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk2indx_midret_amt_a2p,price,factor_name,layers=5)

# 12.
factor_name = 'stk2idx_ls_strength'
ma_win = 30
ts_pct_win = 2400
roll_win_fac = 20
min_periods = 10
min_pct = 0.9
stk_long_strength =  (stk_high - stk_open) / stk_open
stk_short_strength =  -(stk_low - stk_open) / stk_open
stk_ls_strength_raw = (stk_long_strength - stk_short_strength).rolling(roll_win_fac,min_periods).mean()
stk2idx_ls_strength_raw = stk_ls_strength_raw.mean(axis=1)
stk2idx_ls_strength = calc_ma_helper(stk2idx_ls_strength_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk2idx_ls_strength,price,factor_name,layers=5)

# 13.
factor_name = 'stk2idx_c2l'
ma_win = 30
ts_pct_win = 2400
roll_win_fac = 20
min_periods = 10
stk_c2l_raw = (stk_close/stk_low-1).rolling(roll_win_fac,min_periods).mean()
stk2idx_c2l_raw = stk_c2l_raw.mean(axis=1)
stk2idx_c2l = calc_ma_helper(stk2idx_c2l_raw,ma_win,ts_pct_win,min_pct)
#ts_factor_quick(stk2idx_c2l,price,factor_name,layers=5)