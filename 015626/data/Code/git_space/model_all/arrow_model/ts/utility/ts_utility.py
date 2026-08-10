import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

plt.style.use('ggplot')

import statsmodels.api as sm
# import pickle
import dill as pickle
import os
import gc
import seaborn as sns
import re

from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed
from multiprocessing import Process, Manager

from line_profiler import LineProfiler
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import datetime as dt
from functools import partial


def convert_timenum2str(num, string_space=4):
    if num < 1000:
        num_str = '0%d' % (num)
    else:
        num_str = '%d' % (num)
    return num_str


def print_current_time():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def calc_ts_ma(ts_price, roll_list=[3, 5, 10, 20], min_pct=0.8):
    ts_ma_list = []
    for win in roll_list:
        ma = ts_price.rolling(win, min_periods=int(min_pct * win)).mean()
        ts_ma_list.append(ma)
    ts_ma = pd.concat(ts_ma_list, axis=1)
    ts_ma.columns = ['ma_%d' % (i) for i in roll_list]
    return ts_ma


def calc_hpr(stock_close, holding_period, ret_shift=True, daily_scale=False):
    if isinstance(stock_close.index, pd.MultiIndex):
        hpr = stock_close.groupby(level=1).shift(-1 * holding_period) / stock_close - 1
        if ret_shift:
            hpr = hpr.groupby(level=1).shift(-1)
    else:
        h_type = type(holding_period)
        holding_period = [holding_period] if h_type is int else holding_period
        hpr = {h: (stock_close.shift(-1 * h) / stock_close - 1) for h in holding_period}
        if ret_shift:
            hpr = {h: hpr[h].shift(-1) for h in holding_period}
        if daily_scale:
            hpr = {h: (hpr[h] + 1) ** (1 / h) - 1 for h in holding_period}
        if h_type is int:
            hpr = hpr[holding_period[0]]
    return hpr


def calc_hpr_intraday(ts_price_minute, holding_period, ret_shift=True):
    # ret_shift = True
    ts_price_minute_eod = ts_price_minute.groupby(ts_price_minute.index.date).transform(lambda x: x.iloc[-1])

    cum_count = ts_price_minute.groupby(ts_price_minute.index.date).cumcount()
    cum_count_max = cum_count.groupby(cum_count.index.date).transform(lambda x: x.max())
    cum_count_idx = cum_count_max - cum_count
    cum_count_idx_mask = cum_count_idx < (holding_period + 2)
    ts_price_minute_fix = ts_price_minute.copy().shift(-1 * holding_period)
    if ret_shift:
        ts_price_minute_fix = ts_price_minute_fix.shift(-1)
    ts_price_minute_fix[cum_count_idx_mask] = ts_price_minute_eod
    ts_price_minute_in = ts_price_minute.shift(-1) if ret_shift else ts_price_minute
    hpr_intraday = ts_price_minute_fix / ts_price_minute_in - 1
    # ret_shift ~ burn last minute ~ set to 0
    if ret_shift:
        tail_mask = cum_count == cum_count_max
        hpr_intraday[tail_mask] = 0
    return hpr_intraday


def calc_hpr_recent_intraday(recent_price_dict, holding_period, trade_price, trade_contract):
    hpr_recent_df = calc_hpr_intraday(recent_price_dict[trade_price][trade_contract], holding_period)
    hpr_recent_df_mask = hpr_recent_df[recent_price_dict['recent_month_mask']]
    hpr = hpr_recent_df_mask.mean(axis=1)
    return hpr


def show_time_spent(ts):
    if ts > 60:
        time_spent = (str((round((ts) / 60, 2))) + ' minutes')
    else:
        time_spent = (str((round((ts), 2))) + ' seconds')
    return time_spent


def print_time(toc, tic, show_time=True, remain_iter=None):
    ts = toc - tic
    time_spent = show_time_spent(ts)
    if remain_iter is not None:
        time_spent_total = '/ remain %s' % (show_time_spent(ts * remain_iter))
    else:
        time_spent_total = ''
    time_str = ' (used %s%s) ' % (time_spent, time_spent_total)
    if show_time:
        time_str = time_str + '- ' + print_current_time()
    return time_str


# def calc_corr_decay(ts_signal, ts_price, decay_list=[1, 2, 3, 4, 5, 10, 15, 20], ret_shift=True):
#     decay_val = []
#     for i in decay_list:
#         hpc = calc_hpc(ts_price, i, ret_shift)
#         decay_val.append(hpc.corr(ts_signal))
#     corr_decay = pd.Series(decay_val, decay_list)
#     return corr_decay


def collect_dict_info(dict_info, collect_list_dict):
    """dict_info:
			{'1':{'a':df,'b':df},'2':{'a':df,'b':df}}
	   collect_list_dict:
			{'a':df.1,'b':[df.2,df.3]}
		eg: collect_dict_info(res_dict_xgr_dict,{'prediction':''})
	"""
    collect_res = {}
    for collect in collect_list_dict:
        lv1_collect_list = collect_list_dict[collect]
        lv1_collect_list = [lv1_collect_list] if isinstance(lv1_collect_list, str) else lv1_collect_list
        for lv1_collect in lv1_collect_list:
            lv1_list = []
            lv1_value_list = []
            for lv1 in dict_info:
                val_df = dict_info[lv1][collect]
                if isinstance(val_df, pd.DataFrame):
                    c_val = val_df[lv1_collect]
                elif isinstance(val_df, pd.Series):
                    c_val = val_df
                lv1_value_list.append(c_val)
                lv1_list.append(lv1)
            lv1_df = pd.concat(lv1_value_list, axis=1)
            lv1_df.columns = lv1_list
            collect_res['%s:%s' % (collect, lv1_collect)] = lv1_df
    return collect_res


def calc_date_diff(ts_score):
    ts_score_index = ts_score.index.tolist()
    date_num = len(ts_score_index)
    date_diff_list = np.zeros(date_num)

    for i in range(0, date_num - 1):
        date_diff_list[i] = (ts_score_index[i + 1] - ts_score_index[i]).days
    date_diff = place_back_format(date_diff_list, ts_score)
    return date_diff


def calc_prob2size(ts_score, position_number=10,
                   buy_limit=0.5, sell_limit=0.5):
    """
	kelly criteria
	size = 2*p - 1
	- input score ~ position discretize by position_number
	eg 100, break into 100 bucket in both way
	"""
    # check max and min of score
    score_max = ts_score.max()
    score_min = ts_score.min()
    if score_max > 1 or score_min < 0:
        print('score out of bound')
        raise Exception
    buy_area = 1 - buy_limit
    sell_area = sell_limit
    buy_mask = ts_score > buy_limit
    sell_mask = ts_score < sell_limit
    buy_pos = np.round((ts_score - buy_limit) / buy_area * position_number) / position_number
    sell_pos = np.round((ts_score - sell_limit) / sell_area * position_number) / position_number
    ts_size = pd.Series(np.zeros(len(ts_score)), index=ts_score.index)
    ts_size[buy_mask] = buy_pos
    ts_size[sell_mask] = sell_pos
    return ts_size


def find_nearest_large(array, value):
    # assume sorted
    li = [i for i in array if i >= value]
    if len(li) > 0:
        nearst_large = li[0]
    else:
        nearst_large = np.nan
    return nearst_large


def max_drawdown(capital_line, interest_type='SIMPLE'):
    # return max draw down in decimal
    mdd_end = np.argmax(np.maximum.accumulate(capital_line) - capital_line)
    if mdd_end == 0:
        return np.nan
    mdd_start = np.argmax(capital_line[:mdd_end])
    if interest_type == 'SIMPLE':
        mdd = capital_line[mdd_start] - capital_line[mdd_end]
    else:
        mdd = 1 - capital_line[mdd_end] / capital_line[mdd_start]
    return -mdd


def calc_portfolio_stats(ts_return, compound_type='cumsum', convert_daily=False):
    ts_return = pd.DataFrame(ts_return)
    date_num, col_num = ts_return.shape
    date_1yr = 252
    ts_ret = ts_return.fillna(0)
    if convert_daily:
        ts_ret_freq = ts_return.groupby(ts_return.index.date).count()
        if (ts_ret_freq.max(axis=0) > 1).sum() > 1:
            ts_ret = ts_ret.groupby(ts_ret.index.date).sum()
    if compound_type == 'cumsum':
        ret_cum = ts_ret.cumsum()
        ret_cum = ret_cum + 1
        ret_ann = ts_ret.mean() * date_1yr
    elif compound_type == 'cumprod':
        ret_cum = (ts_ret + 1).cumprod()
        ret_ann = (ret_cum.iloc[-1, :] ** (date_1yr / date_num) - 1)
    vol_ann = ts_ret.std() * np.sqrt(date_1yr)
    pos_ret = ts_ret[ts_ret.values > 0]
    neg_ret = ts_ret[ts_ret.values < 0]
    downside_vol_ann = neg_ret.std() * np.sqrt(date_1yr)
    mdd = pd.Series(list(map(max_drawdown, ret_cum.T.values)), index=ret_cum.columns)
    sharpe = ret_ann / vol_ann
    sortino = ret_ann / downside_vol_ann
    calmar = -1 * (ret_ann / mdd)
    profit2loss = -1 * (pos_ret.mean() / neg_ret.mean())
    hit_rate = (ts_ret > 0).sum() / date_num
    port_stats = pd.concat([ret_ann, vol_ann, sharpe, mdd, sortino, calmar, profit2loss], axis=1)
    port_stats.columns = ['Return', 'Vol', 'Sharpe', 'MaxDD', 'Sortino', 'Calmar', 'P2L']
    return port_stats


##########################   Plot     #####################################
def plot_with_secondary(df1, df2, plot_name, x_label, y_label1, y_label2,
                        plot_type='line', fig_width=14, fig_height=5, font_size_axis=10,
                        font_size_title=12, font_title_weight=12, font_size_legend=10):
    df1.index.name = ''
    df2.index.name = ''
    fig, ax = plt.subplots()
    df1_plot = df1.plot(ax=ax, kind=plot_type, figsize=(fig_width, fig_height),
                        fontsize=font_size_axis, legend=True)
    df1_plot.set_title(plot_name, fontsize=font_size_title, fontweight=font_title_weight)

    df1_plot.set_ylabel(y_label1, fontsize=font_size_axis)
    ax.set_xlabel(x_label, fontsize=font_size_axis)
    df2_plot = df2.plot(ax=ax, kind=plot_type, figsize=(fig_width, fig_height),
                        fontsize=font_size_axis, secondary_y=True, style='--', legend=True)
    df2_plot.set_ylabel(y_label2, fontsize=font_size_axis)
    # plt.legend(*legend_helper(), loc=legend_loc, fontsize=font_size_legend)
    # imgdata = BytesIO()
    # plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    # imgdata.seek(0)
    # plt.close()
    return


###############################################################################
#### signal

"""
# seasonality signal 
# month long feb/mar/dec + short jun 
# calendar: spring feastival 
# month in between: long first half of month short second half of month 
# week: long month + short thursday
"""

""" date handler"""


def dt_parser(date):
    if isinstance(date, str):
        if date.find('-') > 0:
            date_obj = dt.datetime.strptime(date, '%Y-%m-%d')
        else:
            date_obj = dt.datetime.strptime(str(int(date)), '%Y%m%d')
    else:
        date_obj = dt.datetime.strptime(str(int(date)), '%Y%m%d')
    return date_obj


def label_by_date_list_helper(ts_price, date_list):
    date_list_dt = [dt_parser(i) for i in date_list]
    date_list_full = ts_price.index.tolist()
    signal_list = []
    for i in date_list_full:
        if i in date_list_dt:
            sig = 1
        else:
            sig = np.nan
        signal_list.append(sig)
    signal = pd.Series(signal_list, index=ts_price.index)
    return signal


def find_nearest_date(date, date_list):
    """
	input date and datelist as int
	"""
    nearest_date = min(date_list, key=lambda x: abs(x - date) if x <= date else 100)
    return nearest_date


def label_by_date_list(ts_price, date_list_spec, prev_day=3, post_day=3, return_dict=False):
    """
	iterate date in date_list_spec, find n closest one - label it by 1 else np.nan
	"""
    date_list_trading = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in ts_price.index.tolist()]
    date_num = len(date_list_trading)
    time_delta = 10
    time_lag = time_delta + int(time_delta / 5) * 2 + max(prev_day, post_day)
    time_delta_max = pd.Timedelta('%d days' % (time_lag))
    spec_date_dict = {}
    sig_date_list = []
    for i in date_list_spec:
        # idx = find_nearest([i],date_list_trading)
        i_date = find_nearest_date(i, date_list_trading)
        i_date_diff = abs(pd.Timestamp(str(i_date)) - pd.Timestamp(str(i)))
        if i_date_diff > time_delta_max:
            print('cloest day reaches max tolerance: %d - %d ' % (i, i_date))
            raise Exception
        else:
            idx = date_list_trading.index(i_date)
            idx_min = max(idx - prev_day + 1, 0)
            idx_max = min(idx + post_day + 1, date_num - 1)
            i_spec_date = date_list_trading[idx_min:idx_max]
            if return_dict:
                spec_date_dict[i] = i_spec_date
            else:
                sig_date_list = sig_date_list + i_spec_date
    if return_dict:
        return spec_date_dict
    else:
        signal = label_by_date_list_helper(ts_price, sig_date_list)
        return signal


#############################################################################################
# ts fitting

def align_ts(ts1, ts2):
    ts1_col_num = ts1.shape[1] if isinstance(ts1, pd.DataFrame) else 1
    ts2_col_num = ts2.shape[1] if isinstance(ts2, pd.DataFrame) else 1
    ts_com = pd.concat([ts1, ts2], axis=1).dropna(axis=0)
    ts1_algn = ts_com.iloc[:, :ts1_col_num]
    ts2_algn = ts_com.iloc[:, -ts2_col_num:]
    return ts1_algn, ts2_algn


def ts_align_fitting_data(y_in, x_in, sdate=None, edate=None, label_cut=None, fillna=False,
                          fix_tail=True, value_cut=None, print_cut=False):
    y = y_in.copy()
    x = x_in.copy()
    if isinstance(y, pd.DataFrame):
        y_type = 'df'
        y = y.iloc[:, 0]
    if label_cut is not None or value_cut is not None:
        y_dum = pd.Series(np.full_like(y, fill_value=np.nan), index=y.index)
        if label_cut is not None:
            if isinstance(label_cut, list):
                label_cut.sort()
                lower_cut = label_cut[0]
                higher_cut = label_cut[1]
                y_dum[y > higher_cut] = 1
                y_dum[y < lower_cut] = -1
                if y_type == 'df':
                    y = pd.DataFrame(y_dum).dropna()
                else:
                    y = y_dum.dropna()
            else:
                y = (y > label_cut) * 1
        if value_cut is not None:
            if not isinstance(value_cut, list):
                value_cut = [value_cut, -1 * value_cut]
            value_cut.sort()
            lower_cut = value_cut[0]
            higher_cut = value_cut[1]
            y_dum[y > higher_cut] = y
            y_dum[y < lower_cut] = y
            if y_type == 'df':
                y = pd.DataFrame(y_dum).dropna()
            else:
                y = y_dum.dropna()

    if sdate is not None and edate is not None:
        # x = x.loc[dt_parser(sdate):dt_parser(edate)]
        x = x.loc[pd.Timestamp(str(sdate)):pd.Timestamp(str(edate))]

    if fix_tail:
        y.iloc[-100:].fillna(0, inplace=True)
    y = y.reindex(index=x.index).dropna()
    x_num = len(x.columns)
    cov_x_ts = np.isfinite(x).sum(axis=1)
    # check tail - last update data
    if cov_x_ts.iloc[-1] == 0:
        print('last day x is not updated')
        raise Exception
    if label_cut is not None or value_cut is not None:
        x_test = x.copy()
    x = x.reindex(index=y.index)
    if fillna:
        x.fillna(0, inplace=True)
        if label_cut is not None or value_cut is not None:
            x_test.fillna(0, inplace=True)
    else:
        lack_num = (cov_x_ts < x_num).sum()
        if lack_num > 0:
            print('fillna false: lack %d days data' % (lack_num))
            raise Exception

    if label_cut is not None or value_cut is not None:
        if print_cut:
            print(x.shape, x_test.shape)
        return y, x, x_test
    else:
        return y, x


import bottleneck as bk


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = max(int(min_pct * roll_win), 1)
    if isinstance(ts_dat.index, pd.MultiIndex):
        ts_dat_pct_list = []
        ts_dat_df = ts_dat.unstack()
        for i in ts_dat_df.columns:
            ts_dat_itr = ts_dat_df[[i]]
            ts_dat_pct_np_itr = bk.move_rank(ts_dat_itr, window=roll_win, min_count=min_win, axis=0)
            ts_dat_pct_itr = place_back_format(ts_dat_pct_np_itr, ts_dat_itr)
            ts_dat_pct_list.append(ts_dat_pct_itr)
        ts_dat_pct = pd.concat(ts_dat_pct_list, axis=1)
        ts_dat_pct.columns = ts_dat_df.columns
        ts_dat_pct = ts_dat_pct.stack()
    else:
        ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
        ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    if force_range:
        ts_dat_pct = (ts_dat_pct + 1) / 2
    return ts_dat_pct


def calc_ts_truncation(y_ts, roll_win=240 * 60, cut_limit=0.99, min_pct=0.8):
    ytu = y_ts.rolling(roll_win, int(roll_win * min_pct)).quantile(cut_limit)
    ytl = y_ts.rolling(roll_win, int(roll_win * min_pct)).quantile(1 - cut_limit)
    y_ts_trunc = y_ts.copy()
    y_ts_trunc[y_ts_trunc > ytu] = ytu
    y_ts_trunc[y_ts_trunc < ytl] = ytl
    return y_ts_trunc


def calc_ts_norm(ts_dat, roll_win=20, norm_type='min_max', min_pct=0.9):
    if len(ts_dat) < roll_win:
        print('calc_ts_pct error: ts len too short: %d/%d' % (len(ts_dat), roll_win))
        raise Exception
    min_periods = int(min_pct * roll_win)
    if norm_type == 'pct':
        ts_norm = calc_ts_pct(ts_dat, roll_win, min_pct)
    elif norm_type == 'min_max':
        ts_max = ts_dat.rolling(roll_win, min_periods=min_periods).max()
        ts_min = ts_dat.rolling(roll_win, min_periods=min_periods).min()
        ts_norm = (ts_dat - ts_min) / (ts_max - ts_min)
    elif norm_type == 'zscore':
        ts_mean = ts_dat.rolling(roll_win, min_periods=min_periods).mean()
        ts_std = ts_dat.rolling(roll_win, min_periods=min_periods).std()
        ts_norm = (ts_dat - ts_mean) / ts_std
    return ts_norm


def calc_np_rank(array):
    # array = np.array([4,2,np.nan,7,1])
    mask = np.isfinite(array)
    if not mask[-1]:
        return np.nan
    array_use = array[mask]
    temp = array_use.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(array_use))
    ranks_pct = ranks / max(ranks)
    return ranks_pct[-1]


#############################################
# minute helper


def slice_by_minute(dat, slice_range=[1000, 1454]):
    """ minute mark at the start
		 use left close, right open  - except 1500 - include that
		 slice_range = [[1125,1129],[1300,1310]]

	"""
    if isinstance(dat.index, pd.MultiIndex):
        index_list = dat.index.get_level_values(0)
    else:
        index_list = dat.index
    hour_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.hour]
    minute_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.minute]
    hour_minute_list = [int('%s%s' % (i, j)) for i, j in zip(hour_list, minute_list)]
    if isinstance(slice_range[0], list):
        range_a = slice_range[0]
        range_b = slice_range[1]
        range_a.sort()
        range_b.sort()
        slice_mask = [(i <= range_a[-1] and i >= range_a[0]) or
                      (i <= range_b[-1] and i >= range_b[0])
                      for i in hour_minute_list]
    else:
        slice_range.sort()
        slice_mask = [i <= slice_range[-1] and i >= slice_range[0] for i in hour_minute_list]
    dat_slice = dat[slice_mask]
    return dat_slice


def filter_by_minute(dat, filter_range=[1000, 1454], fill_value=np.nan):
    dat_filter = dat.copy()
    if isinstance(dat.index, pd.MultiIndex):
        index_list = dat.index.get_level_values(0)
    else:
        index_list = dat.index
    hour_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.hour]
    minute_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.minute]
    hour_minute_list = [int('%s%s' % (i, j)) for i, j in zip(hour_list, minute_list)]
    if isinstance(filter_range[0], list):
        range_a = filter_range[0]
        range_b = filter_range[1]
        range_a.sort()
        range_b.sort()
        slice_mask = [(i <= range_a[-1] and i >= range_a[0]) or
                      (i <= range_b[-1] and i >= range_b[0])
                      for i in hour_minute_list]
    else:
        filter_range.sort()
        slice_mask = [i <= filter_range[-1] and i >= filter_range[0] for i in hour_minute_list]
    dat_filter[slice_mask] = fill_value
    return dat_filter


# def handle_minute_timestamp(ts_index):
#     # process minute pkl
#     ts_index = dat_spot.reset_index()
#     minute_hour_list = ['%s' % (i) if i >= 1000 else '0%s' % (i) for i in ts_index.minute]
#     ts_timestamp_list = [pd.Timestamp(str(i) + j) for i, j in zip(ts_index.dt, minute_hour_list)]
#     ts_index.index = ts_timestamp_list
#     ts_index = ts_index.drop(columns=['dt', 'minute'])
#     return ts_index


# calc seasonality
def calc_seasonal_diff(minute_val, roll_day=20, min_pct=0.5):
    day_id = pd.Series([i.date() for i in minute_val.index], index=minute_val.index)
    minute_id = calc_minute_to_close_col(minute_val, reverse=True)
    minute_val_id = pd.concat([minute_val, day_id, minute_id], axis=1)
    minute_val_id.columns = [minute_val_id.columns[0], 'day_id', 'minute_id']
    minute_val_id = minute_val_id.reset_index().set_index(['day_id', 'minute_id'])
    minute_val_id_mat = minute_val_id.drop(columns='dt').unstack()
    minute_val_id_roll = minute_val_id_mat.rolling(roll_day, int(min_pct * roll_day)).mean()
    minute_val_diff_mat = minute_val_id_mat - minute_val_id_roll
    minute_val_diff_raw = minute_val_diff_mat.stack()
    minute_val_diff_tmp = pd.concat([minute_val_id, minute_val_diff_raw], axis=1)
    minute_val_diff = minute_val_diff_tmp.reset_index().set_index('dt').iloc[:, -1]
    return minute_val_diff


###
#  factor helper
def agg_by_measure_cumpct(x_comb, cum_pct=0.1, agg_func=np.nansum):
    """ order by order measure - large to small - order measure is non-negative
	x,measure_cut
	x = np.array([1,3,5,3,2,1,2,3])
	measure_cut = np.array([4,1,4,7,2,1,2,4])
	"""
    x_order = np.array(x_comb.values)
    x_order[:, 0] = -1 * x_order[:, 0]
    # x_order = np.stack([-1*x,measure_cut],axis=1) #
    x_order_sort = x_order[x_order[:, 0].argsort()]  # sort by x - large to small
    measure_cut_sort = x_order_sort[:, 1]
    measure_cut_sort_cumpct = np.cumsum(measure_cut_sort) / np.nansum(measure_cut_sort)
    measure_cut_sort_mask = measure_cut_sort_cumpct <= cum_pct
    measure_cut_sort_mask[0] = True  # force at least one block
    agg_val = -1 * np.nansum(x_order_sort[:, 0][measure_cut_sort_mask])
    return agg_val


####  ts data cleaning ####
def filter_by_mad_ts(ts_dat, mad=3, roll_num=120, min_pct=0.5):
    # 5 minutes for collect data
    ts_dat_filter = ts_dat.copy()
    min_num = max(int(min_pct * roll_num), 1)
    ts_dat_chg = ts_dat - ts_dat.shift(1)
    rm = ts_dat.rolling(roll_num, min_num).median()
    abs_deviation = (ts_dat - rm).abs()
    rm_mad = abs_deviation.rolling(roll_num, min_num).median()
    upper_bound = rm + rm_mad * mad
    lower_bound = rm - rm_mad * mad
    ts_dat_filter[ts_dat > upper_bound] = upper_bound
    ts_dat_filter[ts_dat < lower_bound] = lower_bound
    return ts_dat_filter


def calc_ts_auto_corr(ts_score, lag_list=[1, 3, 5, 10]):
    ts_score = pd.DataFrame(ts_score)
    auto_corr_list = []
    for lag in lag_list:
        auto_corr_list.append(ts_score.corrwith(ts_score.shift(lag)))
    ts_auto_corr = pd.concat(auto_corr_list, axis=1)
    ts_auto_corr.columns = lag_list
    return ts_auto_corr


def calc_rolling_ts_corr_pd(x1, x2, roll_win, min_pct=0.8):
    corr_input_raw = pd.concat([x1, x2], axis=1)
    corr_input_raw.columns = [0, 1]
    corr_raw = corr_input_raw.rolling(roll_win, int(roll_win * min_pct)).corr()
    corr_res = corr_raw.xs(0, level=1).iloc[:, 1]
    return corr_res


import talib as ta


def calc_rolling_ts_corr(x1, x2, window):
    x12 = pd.concat([x1, x2], axis=1).dropna()
    x1_np = x12.iloc[:, 0].values
    x2_np = x12.iloc[:, 1].values
    res_np = ta.CORREL(x1_np, x2_np, timeperiod=window)
    res = pd.Series(res_np, index=x12.index)
    return res


def calc_minute_to_close(minute):
    if isinstance(minute, pd.Timestamp):
        minute = minute.hour * 100 + minute.minute
    minute_list = [i for i in range(60)]
    hour_list = [i for i in range(9, 15)]
    minute_hour_list = [i * 100 + j for i in hour_list for j in minute_list]
    minute_hour_list = [i for i in minute_hour_list if (i < 1130 or i >= 1300) and i >= 930]
    try:
        minute_to_close = 240 - minute_hour_list.index(minute)
    except:
        minute_to_close = np.nan
    return minute_to_close


def calc_minute_to_close_col(minute_df, reverse=False):
    minute_to_close_list = [calc_minute_to_close(i) for i in minute_df.index]
    minute_to_close_ps = pd.Series(minute_to_close_list, index=minute_df.index)
    if reverse:
        minute_to_close_ps = 240 - minute_to_close_ps
    return minute_to_close_ps


from sklearn.preprocessing import StandardScaler


def filter_by_mad_helper(ts_dat_train, ts_dat_test, mad_num=3):
    ts_dat_test_filter = ts_dat_test.copy()
    if type(ts_dat_train) not in [pd.Series, pd.DataFrame]:
        ts_dat_train = pd.DataFrame(ts_dat_train)
    rm = ts_dat_train.median()
    abs_deviation = (ts_dat_train - rm).abs()
    rm_mad = abs_deviation.median()
    upper_bound = (rm + rm_mad * mad_num).values[0]
    lower_bound = (rm - rm_mad * mad_num).values[0]
    ts_dat_test_filter[ts_dat_test_filter > upper_bound] = upper_bound
    ts_dat_test_filter[ts_dat_test_filter < lower_bound] = lower_bound
    return ts_dat_test_filter


import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter


def plot_price_with_label(price, label, show_week=False, plot_return=False):
    label = label.reindex(index=price.index)
    fig, ax = plt.subplots()
    fig.set_size_inches(18, 6)
    plt.plot(price)
    plt.rc('font', size=14)
    fake_x = price.index
    plt1 = plt.fill_between(x=fake_x, y1=label, y2=0, where=label > 0, color='red', alpha=0.25, transform=ax.get_xaxis_transform())
    plt2 = plt.fill_between(x=fake_x, y1=label, y2=1, where=label < 0, color='green', alpha=0.25, transform=ax.get_xaxis_transform())
    plt.ylim(price.min(), price.max())
    l1 = plt.legend([plt1, plt2], ["long", "short"], loc='upper left')
    if show_week:
        # Define the date format
        date_form = DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(date_form)
        # Ensure a major tick for each week using (interval=1)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    return


def parser_trade_result(ts_sig, ts_price):
    hpr = calc_hpr(ts_price, 1, True)
    hpr_sign = np.sign(hpr)
    pred_hit = ts_sig * hpr_sign
    price_plot = ts_price.reindex(index=pred_hit.index)
    label_plot = ts_sig
    year_list = list(set([i.year for i in ts_price.index]))
    year_list = [str(i) for i in year_list]
    year_list.reverse()
    print('check prediction accuracy')
    for year in year_list:
        print(year)
        print('long: %d / short: %d' % ((label_plot.loc[year] > 0).sum(), (label_plot.loc[year] < 0).sum()))
        plot_price_with_label(price_plot.loc[year], label_plot.loc[year])
        plt.show()

    print('check prediction sign')
    label_plot = pred_hit
    for year in year_list:
        print(year)
        print('correct: %d / wrong: %d' % ((label_plot.loc[year] > 0).sum(), (label_plot.loc[year] < 0).sum()))
        plot_price_with_label(price_plot.loc[year], label_plot.loc[year])
        plt.show()


from scipy.stats import ttest_ind


def pred_seg_helper_ts(x_train, y_train, x_test, segment_num=5):
    fac_ret = np.stack([x_train, y_train], axis=1)
    fac_ret_sort = fac_ret[fac_ret[:, 0].argsort()]  # sort by factor score - small to large
    rank_num = sum(np.isfinite(fac_ret_sort[:, 0]))  # 剩下多少只股票,
    stock_num_q = int(rank_num / segment_num)
    order_cut = np.arange(0, rank_num, stock_num_q) if segment_num > 1 else [0]
    order_cut = order_cut[:segment_num] if segment_num > 1 else [0]  # there may be stock left due to rounding error
    bottom_list = fac_ret_sort[:stock_num_q, 1]  # score small
    top_list = fac_ret_sort[-stock_num_q:, 1]  # score large
    t_stats, p = ttest_ind(top_list, bottom_list)
    ls_ret = np.mean(top_list) - np.mean(bottom_list)
    tot_num = len(x_train)
    small_list = [i for i in x_train if i <= x_test[0]]
    ts_pct = len(small_list) / tot_num
    res = [t_stats, ts_pct, ls_ret]
    return res


################################################

from ts.utility.ts_backtest_wange import TS_BACK_TEST


def ts_backtest_quick(factor, sdate=None, edate=None, price_kind='twap',
                      ticker='IC.CFE',
                      initial_cash=50000000,
                      save_path='/data/user/012315/share/ts/strategy/back_test/minute/backtest',
                      name_prefix=None,
                      pos_dict={(0, 0.4): (0.0, 0.0),
                                (0.4, 0.5): (0.0, 0.2 / 3),
                                (0.5, 0.6): (0.2 / 3, 0.4 / 3),
                                (0.6, 0.7): (0.4 / 3, 0.6 / 3),
                                (0.7, 0.8): (0.6 / 3, 0.8 / 3),
                                (0.8, 0.9): (0.8 / 3, 1.0 / 3),
                                (0.9, 1.9): (1.0 / 3, 1.0 / 3)},
                      capital_use_rate=1,
                      stop_loss=-0.005,
                      plot=True):
    slippage_dict = {'IC.CFE': 0.6, 'IF.CFE': 0.4, 'IH.CFE': 0.4}
    slippage = slippage_dict[ticker]
    if isinstance(factor, pd.DataFrame):
        factor_name = factor.columns[0]
        factor = factor.iloc[:, 0]
        if name_prefix is None:
            name_prefix = factor_name + '_'
            save_path = os.path.join(save_path, factor_name)
    else:
        factor_name = ''
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if factor.min() >= 0:
        factor = factor * 2 - 1
    if sdate is not None:
        factor = factor.loc[sdate:]
    if edate is not None:
        factor = factor.loc[:edate]
    ts = TS_BACK_TEST(factor, price_kind=price_kind, ticker=ticker, slippage=slippage,
                      initial_cash=initial_cash,
                      save_path=save_path, name_prefix=name_prefix,
                      pos_dict=pos_dict, capital_use_rate=capital_use_rate,
                      stop_loss=stop_loss)
    profit, prof_stats, trade, trade_by_deal = ts.back_test()
    print(factor_name)
    print(prof_stats)
    res_dict = {'profit': profit, 'prof_stats': prof_stats,
                'trade': trade, 'trade_by_deal': trade_by_deal}
    if plot:
        profit.plot(figsize=[20, 10], fontsize=20)
        plt.title(factor_name, fontsize=40)
    return res_dict


def ts_backtest_quick2(factor_name, factor_dict, sdate=None, edate=None, price_kind='twap',
                       ticker='IC.CFE',
                       initial_cash=50000000,
                       save_path='/data/user/012315/share/ts/strategy/back_test/minute/backtest',
                       name_prefix=None,
                       pos_dict={(0, 0.4): (0.0, 0.0),
                                 (0.4, 0.5): (0.0, 0.2 / 3),
                                 (0.5, 0.6): (0.2 / 3, 0.4 / 3),
                                 (0.6, 0.7): (0.4 / 3, 0.6 / 3),
                                 (0.7, 0.8): (0.6 / 3, 0.8 / 3),
                                 (0.8, 0.9): (0.8 / 3, 1.0 / 3),
                                 (0.9, 1.9): (1.0 / 3, 1.0 / 3)},
                       capital_use_rate=1,
                       stop_loss=-0.005,
                       plot=True):
    factor = factor_dict[factor_name]
    slippage_dict = {'IC.CFE': 0.6, 'IF.CFE': 0.4, 'IH.CFE': 0.4}
    slippage = slippage_dict[ticker]
    if isinstance(factor, pd.DataFrame):
        factor_name = factor.columns[0]
        factor = factor.iloc[:, 0]
        if name_prefix is None:
            name_prefix = factor_name + '_'
            save_path = os.path.join(save_path, factor_name)
    else:
        factor_name = ''
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if factor.min() >= 0:
        factor = factor * 2 - 1
    if sdate is not None:
        factor = factor.loc[sdate:]
    if edate is not None:
        factor = factor.loc[:edate]
    factor.index.name = 'dt'
    ts = TS_BACK_TEST(factor, price_kind=price_kind, ticker=ticker, slippage=slippage,
                      initial_cash=initial_cash,
                      save_path=save_path, name_prefix=name_prefix,
                      pos_dict=pos_dict, capital_use_rate=capital_use_rate,
                      stop_loss=stop_loss)
    profit, prof_stats, trade, trade_by_deal = ts.back_test()
    print(factor_name)
    print(prof_stats)
    res_dict = {'profit': profit, 'prof_stats': prof_stats,
                'trade': trade, 'trade_by_deal': trade_by_deal}
    if plot:
        profit.plot(figsize=[20, 10], fontsize=20)
        plt.title(factor_name, fontsize=40)
    return res_dict


from .SIF_Factor_Test import SIF_Factor_Test


# from .second_factor_test import Factor_Test_5S

def ts_factor_quick(ts_fac, price, factor_name=None, layers=4, holding_period=1, return_price_kind='vwap',
                    sdate='20100101', edate='20301231', save_path='/data/user/012315/data/factor_test/ic',
                    factor_kind='1min', ticker='IC.CFE', show_image=True):
    # return_points = price.shift(-1-holding_period) - price.shift(-1)
    ts_fac.index.name = 'dt'
    if factor_name is None:
        if isinstance(ts_fac, pd.DataFrame):
            factor_name = ts_fac.columns[0]
        else:
            factor_name = ''
    else:
        factor_name = str(factor_name)
    if sdate is not None:
        ts_fac = ts_fac.loc[pd.Timestamp(str(sdate)):]
    if edate is not None:
        ts_fac = ts_fac.loc[:pd.Timestamp(str(edate))]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    ret = price.shift(-1 - holding_period) / price.shift(-1) - 1
    min_val = ts_fac.dropna().values.min()
    if min_val >= 0:
        ts_fac_use = ts_fac * 2 - 1
    else:
        ts_fac_use = ts_fac.copy()
    ret = ret.reindex(index=ts_fac.index)
    if factor_kind not in ['overnight']:
        df = pd.concat([ts_fac_use, ret], axis=1)  # .dropna()
    else:
        df = ts_fac_use
    threshold = 1 - 2 / layers
    sft = SIF_Factor_Test(df, factor_name, layers=layers, ticker=ticker,
                          starttime=sdate, endtime=edate,
                          savepath=save_path, factor_kind=factor_kind,
                          return_price_kind=return_price_kind,
                          show_image=show_image)
    res = sft.draw_result()
    plt.clf()
    plt.cla()
    plt.close()
    return res


def ts_factor_quick_helper(factor_name, score_pct, price, layers, save_path, ticker, factor_kind, show_image):
    res = ts_factor_quick(score_pct[[factor_name]], price, factor_name, layers=layers,
                          save_path=save_path, ticker=ticker, factor_kind=factor_kind,
                          show_image=show_image)
    plt.clf()
    plt.cla()
    plt.close('all')
    gc.collect()
    return res


def ts_factor_test_multi(fac_val, price, sdate=None, ticker='IC.CFE', save_path=None, layers=4, edate=None,
                         factor_kind='1min'):
    if save_path is not None:
        print(save_path)
    if isinstance(fac_val, dict):
        fac_val_df = pd.concat(list(fac_val.values()), axis=1).dropna()
        fac_val_df.columns = list(fac_val.keys())
    elif isinstance(fac_val, pd.Series):
        fac_val_df = pd.DataFrame(fac_val)
    elif isinstance(fac_val, pd.DataFrame):
        fac_val_df = fac_val
    fee_dict = {'IC.CFE': 1.5, 'IF.CFE': 1, 'IH.CFE': 1}
    fee = fee_dict[ticker]
    print('Factor Test: %s' % (ticker))
    price_base = price.mean()
    res_list = []
    for factor_name in fac_val_df:
        print(factor_name)
        score_pct = fac_val_df[factor_name]
        if sdate is not None:
            score_pct = score_pct.loc[sdate:]
        if edate is not None:
            score_pct = score_pct.loc[:edate]
        sdate_ft, edate_ft = score_pct.index[0], score_pct.index[-1]
        print('Test Time: %s - %s' % (sdate_ft, edate_ft))
        if save_path is not None:
            res_itr = ts_factor_quick(score_pct, price, factor_name, layers=layers, save_path=save_path,
                                      ticker=ticker, factor_kind=factor_kind)
        else:
            res_itr = ts_factor_quick(score_pct, price, factor_name, layers=layers, ticker=ticker, factor_kind=factor_kind)
        ret_itr_df = pd.DataFrame(list(res_itr.values()), index=list(res_itr.keys()), columns=[factor_name])
        res_list.append(ret_itr_df)
    res_df = pd.concat(res_list, axis=1).T
    # res_df = res_df.sort_values(by='ret_per_deal',ascending=False)
    res_df['ret_long_short_with_fee'] = res_df['ret_long_short'] - fee / price_base * (res_df['long_deal_num'] + res_df['short_deal_num'])
    take_list_res = ['ret_per_deal', 'sharpe_Q%d-Q0' % (layers - 1), 'IC-1min', 'ret_long_short',
                     'ret_long_short_with_fee', 'ret_per_deal_long', 'ret_per_deal_short']
    rename_list = ['rpd(bp)', 'sharpe', 'ic', 'ret', 'ret_with_cost', 'rpd_l', 'rpd_s']
    res_df_show = res_df[take_list_res]
    res_df_show.columns = rename_list
    multi_list = ['rpd(bp)', 'rpd_l', 'rpd_s']
    res_df_show[multi_list] = res_df_show[multi_list] * 10000
    print('%s - %s' % (sdate_ft, edate_ft))
    print(res_df_show)
    plt.show()
    # plot_heatmap(fac_val_df.corr())
    # plt.show()
    if save_path is not None:
        save_path_name = os.path.join(save_path, 'ts_ft_stats.csv')
        res_df_show.T.to_csv(save_path_name)
    return res_df


def ts_bkt_quick(pred_norm, long_ret, short_ret=None, trade_contract='', model='', plot=True):
    print('%s ~ %s' % (trade_contract, model))
    long_ret = long_ret.reindex(index=pred_norm.index)
    if short_ret is None:
        short_ret = long_ret
    short_ret = short_ret.reindex(index=pred_norm.index)
    long_sig = pred_norm[pred_norm > 0]
    short_sig = pred_norm[pred_norm < 0]
    long_ret_res = (long_sig * long_ret).fillna(0)
    long_ret_stats = calc_portfolio_stats(long_ret_res)
    short_ret_res = (short_sig * short_ret).fillna(0)
    short_ret_stats = calc_portfolio_stats(short_ret_res)
    # ls_ret = (pred_norm*y_ret).fillna(0)
    ls_ret_res = long_ret_res + short_ret_res
    ls_ret_stats = calc_portfolio_stats(ls_ret_res)

    if plot:
        long_ret_res.cumsum().plot(figsize=[15, 4], title='long_ret: %s ~ %s' % (trade_contract, model))
        plt.show()
        print(long_ret_stats)

        short_ret_res.cumsum().plot(figsize=[15, 4], title='short_ret: %s ~ %s' % (trade_contract, model))
        plt.show()
        print(short_ret_stats)

        ls_ret_res.cumsum().plot(figsize=[15, 4], title='long_short_ret: %s ~ %s' % (trade_contract, model))
        plt.show()
        print(ls_ret_stats)

    res_dict = {'ls': ls_ret_stats, 'long': long_ret_stats, 'short': short_ret_stats}
    return res_dict


def ts_factor_test_batch(res_base_path, price, ts_pct_win=240 * 10, min_pct=0.98, sdate_str='2017', layers=4, fee=1.5):
    print('read files')
    pred_df, model_dict = get_model_pred_helper(res_base_path)
    print(pred_df.describe())
    pred_norm = {}
    print('normalize factors')
    take_list = pred_df.columns
    for factor_name in take_list:
        print(factor_name)
        pred_norm[factor_name] = calc_ts_pct(pred_df[factor_name], ts_pct_win, min_pct=min_pct)
    pred_norm_df = pd.DataFrame(pred_norm).reindex(index=price.index).dropna()
    print('test factors')
    res_list = []
    for factor_name in pred_norm_df:
        print(factor_name)
        score_pct = pred_norm_df[factor_name]
        res_itr = ts_factor_quick(score_pct.loc[sdate_str:], price, factor_name, layers=layers)
        ret_itr_df = pd.DataFrame(list(res_itr.values()), index=list(res_itr.keys()), columns=[factor_name])
        res_list.append(ret_itr_df)

    res_df = pd.concat(res_list, axis=1)
    res_df = res_df.T.sort_values(by='rp_per_deal', ascending=False)
    res_df['profit_before_fee'] = res_df['rp_per_deal_long'] * res_df['long_deal_num'] + res_df['rp_per_deal_short'] * res_df['short_deal_num']
    res_df['profit_after_fee'] = res_df['profit_before_fee'] - fee * (res_df['long_deal_num'] + res_df['short_deal_num'])
    take_list_res = ['rp_per_deal', 'sharpe_Q%d-Q0' % (layers - 1), 'IC-1min', 'profit_before_fee', 'profit_after_fee']
    rename_list = ['rp', 'sharpe', 'ic', 'profit', 'with_fee']
    res_df_show = res_df[take_list_res]
    res_df_show.columns = rename_list
    res_df_show[['profit', 'with_fee']] = res_df_show[['profit', 'with_fee']].astype(int)
    print('full sample - layers %d' % (layers))
    print(res_df_show)
    plt.show()
    # plot_heatmap(pred_norm_df.corr())
    # plt.show()
    return pred_norm_df, model_dict


def extract_model_pred(model_dict):
    model_list = list(model_dict.keys())
    model_list.sort()
    pred_list = []
    print(model_list)
    for model in model_list:
        model_pred = model_dict[model]['prediction']
        pred_list.append(model_pred)
    pred_df = pd.concat(pred_list, axis=1)
    pred_df.columns = model_list
    return pred_df


import pickle, dill


def save_pickle(save_dict, save_path):
    print('saving data to:\n', save_path)
    folder = os.path.dirname(save_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if os.path.exists(save_path):
        print('remove existing one')
        os.remove(save_path)
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict, input, protocol=pickle.HIGHEST_PROTOCOL)
    return


def read_pickle(save_path=None, verbose=True):
    tic = time.time()
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    toc = time.time()
    if verbose:
        print('loading done - %s - %s   ' % (print_time(toc, tic), save_path))
    return save_dict


def get_model_pred_helper(res_base_path):
    model_base_dict = find_file(res_base_path, 'pkl')
    model_dict = {i: read_pickle(model_base_dict[i]) for i in model_base_dict}
    pred_df = extract_model_pred(model_dict)
    return pred_df, model_dict


def ts_test_helper(res_base_path, price, ts_pct_win=1200, min_pct=0.9, layers=4, normalize=True):
    pred_raw, model_dict = get_model_pred_helper(res_base_path)
    print('*** raw stats ***')
    print(pred_raw.describe())
    res_dict = ts_test_data_helper(pred_raw, price, ts_pct_win, min_pct, layers, normalize)
    res_dict['model_dict'] = model_dict
    return res_dict


def ts_test_data_helper(pred_raw, price, ts_pct_win=1200, min_pct=0.9, layers=4, normalize=True):
    if normalize:
        pred_norm_dict = {}
        print('normalize factor with %d ts_pct_win, min_pct: %s' % (ts_pct_win, min_pct))
        take_list = pred_raw.columns
        for factor_name in take_list:
            print(factor_name)
            pred_norm_dict[factor_name] = calc_ts_pct(pred_raw[factor_name], ts_pct_win, min_pct=min_pct)
        pred_norm = pd.DataFrame(pred_norm_dict).dropna()
    else:
        pred_norm = pred_raw.copy()
    print('backtest with %d layers' % (layers))
    res_list = []
    for factor_name in pred_norm:
        print(factor_name)
        res_itr = ts_factor_quick(pred_norm[factor_name], price, factor_name, layers=layers)
        ret_itr_df = pd.DataFrame(list(res_itr.values()), index=list(res_itr.keys()), columns=[factor_name])
        res_list.append(ret_itr_df)
    res_stats = pd.concat(res_list, axis=1)
    res_stats = res_stats.T.sort_values(by='rp_per_deal', ascending=False).T
    print(res_stats)
    res_dict = {'pred_raw': pred_raw,
                'pred_norm': pred_norm, 'res_stats': res_stats}
    return res_dict


def plot_sample(sample_df, show_num=10, plt_kind='line'):
    dt_list_sample = sample_df.groupby(sample_df.index.date).count().index.tolist()
    dt_list_sample_str = [dt.datetime.strftime(i, '%Y-%m-%d') for i in dt_list_sample]
    for d in dt_list_sample_str[:show_num]:
        print(d)
        sample_df.loc[d].plot(title=d, kind=plt_kind)
        plt.show()
    return


def mute_open_close_period(dat_df, mute_list=[(9, 29), (9, 30), (13, 0), (11, 30), (15, 0)]):
    dat_df_mute = dat_df.copy()
    dt_list = dat_df.index.tolist()
    nan_mask = [1 if (i.hour, i.minute) in mute_list else 0 for i in dt_list]
    nan_mask_df = pd.Series(nan_mask, index=dat_df.index)
    dat_df_mute[nan_mask_df == 1] = np.nan
    return dat_df_mute


def drop_by_time(dat_df, drop_list=[(11, 30)]):
    dat_df_drop = dat_df.copy()
    dt_list = dat_df.index.tolist()
    keep_mask = [i for i in dt_list if (i.hour, i.minute) not in drop_list]
    dat_df_drop = dat_df.reindex(keep_mask)
    return dat_df_drop


def calc_ts_pct_list(fac_raw, ts_pct_list=[30, 60, 120, 240, 240 * 5, 240 * 10], min_pct=0.9, force_range=False):
    fac_ts_pct_list = []
    for ts_pct_win in ts_pct_list:
        print('calc ts_pct_win:%d' % (ts_pct_win))
        fac_ts_pct_list.append(calc_ts_pct(fac_raw, ts_pct_win, min_pct=min_pct, force_range=force_range))
    fac_ts_pct = pd.concat(fac_ts_pct_list, axis=1)
    fac_ts_pct.columns = ts_pct_list
    return fac_ts_pct


#############
# save and read ts_fac

def save_ts_fac_helper(fac_dict, fac_base):
    if not os.path.exists(fac_base):
        os.makedirs(fac_base)
    if isinstance(fac_dict, dict):
        fac_list = list(fac_dict.keys())

    elif isinstance(fac_dict, pd.DataFrame):
        fac_list = list(fac_dict.columns)
    fac_list.sort()
    fac_num = len(fac_list)
    print('save %d factors ~ %s' % (fac_num, fac_base))
    for fac_name in fac_list:
        print('%d/%d - %s' % (fac_list.index(fac_name) + 1, fac_num, fac_name))
        fac_path = os.path.join(fac_base, '%s.h5' % (fac_name))
        fac_dict[fac_name].to_hdf(fac_path, fac_name)
    return


def find_file(root_path, suffix='h5', file_name_only=False, fac_list=None):
    factor_path_dict = {}
    for path, subdirs, files in os.walk(root_path):
        for name in files:
            if suffix in name:
                fac_name = name[:-len(suffix) - 1]
                factor_path_dict[fac_name] = os.path.join(path, name)
    if file_name_only:
        factor_path_dict = {fac: os.path.basename(fac).replace('.%s' % (suffix), '') for fac in factor_path_dict}
        factor_path_dict = list(factor_path_dict.values())
    if fac_list is not None:
        exist_list = list(factor_path_dict.keys())
        need_list = fac_list
        lack_list = set(need_list) - set(exist_list)
        if len(lack_list) > 0:
            print('need: %s' % (lack_list))
            raise Exception
        else:
            factor_path_dict = {i: factor_path_dict[i] for i in fac_list}
    return factor_path_dict


def read_ts_fac_helper(fac_base, xs_name=None, fac_list=None, suffix='h5'):
    fac_path_dict = find_file(fac_base, suffix=suffix, fac_list=fac_list)
    fac_val_list = []
    fac_name_list = []
    for fac_name in fac_path_dict:
        # print(fac_name)
        if suffix == 'h5':
            fac_itr = pd.read_hdf(fac_path_dict[fac_name])
        elif suffix == 'parquet':
            fac_itr = pd.read_parquet(fac_path_dict[fac_name])
        if xs_name is not None:
            fac_itr = fac_itr.xs(xs_name, level=1)
        if isinstance(fac_itr, pd.DataFrame):
            if 'norm' in fac_itr.columns:
                fac_itr = fac_itr['norm']
        fac_val_list.append(fac_itr)
        fac_name_list.append(fac_name)
    fac_val = pd.concat(fac_val_list, axis=1)
    fac_val.columns = fac_name_list
    return fac_val


######################
#### kaggle related helper #####

def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
		to reduce memory usage.
	"""
    start_mem = df.memory_usage().sum() / 1024 ** 2
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024 ** 2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df


def read_save_fac_helper(trade_contract1, fac_base_pick1, comb_path1,
                         use_new, fac_lib_date, min_fac_pct=0.8):
    print('read factor data')
    print(trade_contract1)
    print(fac_base_pick1)
    print(comb_path1)
    if use_new:
        print('read factor')
        fac_val = read_ts_fac_helper(fac_base_pick1)
        print('slice by contract')
        fac_val = reduce_mem_usage(fac_val)
        save_pickle(fac_val, comb_path1)
        print('save pickle')
    else:
        fac_val = read_pickle(comb_path1)
    # check factor
    last_fac = fac_val.loc[fac_lib_date].iloc[-1, :]
    tot_fac_cnt = len(last_fac)
    min_fac_cnt = min_fac_pct * tot_fac_cnt
    fac_cnt = np.isfinite(last_fac).sum()
    if fac_cnt < min_fac_cnt:
        print('!' * 40)
        print('fac coverage error: %d/%d' % (min_fac_cnt, tot_fac_cnt))
        print('!' * 40)
        raise Exception
    pick_list = os.listdir(fac_base_pick1)
    fac_list_prod = [i[:-3] for i in pick_list]
    fac_list = fac_val.columns.tolist()
    print('prod/total: %d/%d' % (len(fac_list_prod), len(fac_list)))
    print(fac_val.index[0], fac_val.index[-1])
    return fac_val


#####################
# main contract piece by time

def convert_num2str(num, string_space=2):
    # if num<10:
    #    num_str = '0%d'%(num)
    # else:
    #    num_str = '%d'%(num)
    cur_len = len(str(int(num)))
    zero_num = string_space - cur_len
    add_str = '0' * zero_num
    num_str = add_str + str(int(num))
    return num_str


def get_week_number_week_day(date):
    date_dt = pd.Timestamp(date)
    current_week_num = date_dt.isocalendar()[1]
    first_week_num = date_dt.replace(day=1).isocalendar()[1]
    if current_week_num < first_week_num:  # handle year end
        first_week_num = current_week_num
    week_number = (current_week_num - first_week_num + 1)
    week_day = date_dt.weekday() + 1
    year_num_diff = date_dt.isocalendar()[0] - date_dt.replace(day=1).isocalendar()[0]
    return week_number, week_day, year_num_diff


def get_dummies_helper(dat_cat, dummy_na=False):
    cat_list = []
    dat_cat = dat_cat.astype('category')
    for col in dat_cat:
        cat_list.append(pd.get_dummies(dat_cat[col], prefix=col, dummy_na=dummy_na))
    dummies_df = pd.concat(cat_list, axis=1)
    return dummies_df


def get_bin_number(val, bin_num=3, val_range=[0, 1]):
    """assume val in [0,1]"""
    val_range.sort()
    val_max, val_min = val_range[1], val_range[0]
    range_size = val_max - val_min
    if val >= val_max:
        val = val_max - 1e-6
    if val < val_min:
        val = val_min
    if np.isfinite(val):
        val_bin = range_size / bin_num
        bin_number = int(np.floor((val - val_min) / val_bin) + 1)
    # bin_number = min(bin_number,bin_num)
    else:
        bin_number = np.nan
    return bin_number


def get_ts_pct_bin(ts_val, ts_pct_win=2400, bin_num=3, min_pct=0.9):
    get_bin_number_itr = partial(get_bin_number, bin_num=bin_num)
    ts_pct_bin_list = []
    for col in ts_val:
        print(col)
        ts_val_pct = calc_ts_pct(ts_val[col], ts_pct_win, min_pct=min_pct)
        ts_pct_bin_list.append(ts_val_pct.apply(get_bin_number_itr))
    ts_pct_bin = pd.concat(ts_pct_bin_list, axis=1)
    ts_pct_bin.columns = ts_val.columns
    return ts_pct_bin


################# futures related ########################


import calendar


def find_third_friday(year_month):
    year = int(year_month[:4])
    month = int(year_month[-2:])
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    third_friday = [day for week in monthcal for day in week if
                    day.weekday() == calendar.FRIDAY and
                    day.month == month][2]
    return third_friday


def add_1_month(year_month):
    year = int(year_month[:4])
    month = int(year_month[4:])
    if month == 12:
        year_add = year + 1
        month_add = 1
    else:
        year_add = year
        month_add = month + 1
    year_month_add1 = '%d%s' % (year_add, convert_num2str(month_add))
    return year_month_add1


def get_month_year_list(date_list):
    month_year_list = []
    for date in date_list:
        if isinstance(date, str):
            date = pd.Timestamp(date)
        month_year = '%d%s' % (date.year, convert_num2str(date.month))
        month_year_list.append(month_year)
    return month_year_list


def get_expire_countdown(date_list):
    month_year_list = get_month_year_list(date_list)
    date_diff_list = []
    date_diff_trading_list = []
    month_year_unique_list = list(set(month_year_list))
    month_year_unique_list.sort()

    date_num = len(date_list)
    for i in range(date_num):
        date_curr = date_list[i]
        if i == 0:
            month_curr = month_year_list[i]
            third_friday = find_third_friday(month_curr)
            date_diff = (pd.Timestamp(third_friday) - pd.Timestamp(date_curr)).days
            date_diff_prev = date_diff
            date_diff_list.append(date_diff)
            if date_diff == 0:
                month_year_unique_list.remove(month_curr)
                month_curr = month_year_unique_list[0]
                date_diff_list.append(date_diff)
        else:
            third_friday = find_third_friday(month_curr)
            date_diff = (pd.Timestamp(third_friday) - pd.Timestamp(date_curr)).days
            if date_diff <= 0:
                month_year_unique_list.remove(month_curr)
                if len(month_year_unique_list) > 0:
                    month_curr = month_year_unique_list[0]
                else:
                    month_curr = add_1_month(month_curr)
                date_diff_list.append(0)
            else:
                date_diff_list.append(date_diff)

    expire_calendar_count = pd.Series(date_diff_list, index=date_list)
    expire_date = expire_calendar_count[expire_calendar_count == 0]

    expire_date_list = expire_date.index.tolist()
    date_diff_trade_list = []
    for i in range(date_num):
        if i == 0:
            expire_curr = expire_date_list[0]
            expire_curr_idx = date_list.index(expire_curr)
            date_diff_trade = expire_curr_idx - i
            date_diff_trade_list.append(date_diff_trade)
        else:
            if expire_curr_idx > i:
                date_diff_trade = expire_curr_idx - i
                date_diff_trade_list.append(date_diff_trade)
            else:
                if len(expire_date_list) > 1:
                    expire_date_list.remove(expire_curr)
                    expire_curr = expire_date_list[0]
                    expire_curr_idx = date_list.index(expire_curr)
                    # date_diff_trade = expire_curr_idx - i
                    date_diff_trade_list.append(0)
                else:
                    date_diff_trade_list.append(date_diff_list[i])
    expire_trading_count = pd.Series(date_diff_trade_list, index=date_list)
    expire_countdown = pd.concat([expire_trading_count, expire_calendar_count], axis=1)
    expire_countdown.columns = ['trading', 'calendar']
    return expire_countdown


def calc_date_diff(ts_score):
    ts_score_index = ts_score.index.tolist()
    date_num = len(ts_score_index)
    date_diff_list = np.zeros(date_num)

    for i in range(0, date_num - 1):
        date_diff_list[i] = (ts_score_index[i + 1] - ts_score_index[i]).days
    date_diff = place_back_format(date_diff_list, ts_score)
    return date_diff


def PerformanceMeasure(seg_return, compound_type='cumsum'):
    date_num, segment_num = seg_return.shape
    take_list = (np.isnan(seg_return).sum(axis=1) == segment_num).index
    seg_return = seg_return.loc[take_list]
    date_1yr = 240
    if compound_type == 'cumsum':
        seg_return_cum = seg_return.fillna(0).cumsum() + 1
        Ret_Annual = seg_return.mean() * date_1yr
    elif compound_type == 'cumprod':
        seg_return_cum = (seg_return.fillna(0) + 1).cumprod()
        Ret_Annual = (seg_return_cum.iloc[-1, :] ** (date_1yr / date_num) - 1)

    Vol_Annual = seg_return.fillna(0).std() * np.sqrt(date_1yr)
    MDD = pd.DataFrame(list(map(max_drawdown, seg_return_cum.T.values)), index=seg_return_cum.columns)
    SharpeRatio = Ret_Annual / Vol_Annual
    res_list = [Ret_Annual, Vol_Annual, SharpeRatio]
    name_list = ['Return(Ann.)', 'Vol(Ann.)', 'Sharpe Ratio']
    if 'Benchmark' in Ret_Annual:
        Ret_Excess = Ret_Annual - Ret_Annual['Benchmark']
        Tracking_Error = (seg_return.T - seg_return['Benchmark']).T.std(axis=0) * np.sqrt(date_1yr)
        InfoRatio = Ret_Excess / Tracking_Error
        res_list.append([Ret_Excess, Tracking_Error, InfoRatio])
        name_list.append(['Excess Return', 'Tracking Error', 'IR'])
    res_list.append(MDD)
    name_list.append('MaxDD')
    PerfMeasure = pd.concat(res_list, axis=1)
    PerfMeasure.columns = name_list
    # PerfMeasure = pd.concat([Ret_Annual,Vol_Annual,SharpeRatio,Ret_Excess,Tracking_Error,InfoRatio,MDD],axis=1)
    # PerfMeasure.columns = ['Return(Ann.)','Vol(Ann.)','Sharpe Ratio','Excess Return','Tracking Error','IR','MaxDD']
    return PerfMeasure


def do_rolling(dat, roll_win):
    dat_roll = dat.rolling(roll_win, int(roll_win * 0.5)).mean()
    return dat_roll


# def do_dynamic_piece(func, dat, cmty_universe, hpr, rl=[5, 10, 15, 20, 25, 30, 40], rebal_start=400,
#                      rebal_freq=20):
#     dat_len = len(dat)
#     dat_list = dat.index.tolist()
#
#     rebal_itr = [i + rebal_start for i in range(dat_len - rebal_start) if i % rebal_freq == 0]
#     seg_res_itr = a
#     score_ma_dict = {}
#     seg_ret_list = []
#     for r in rl:
#         print(r)
#         score_ma = do_rolling(dat, r)
#         score_ma_norm = clean_by_universe(score_ma, cmty_universe, normalize=True)
#         seg_res_itr = calc_easy_seg(score_ma_norm, hpr, seg_num=5, print_info=False)
#         score_ma_dict[r] = score_ma_norm
#         # ls_ret = seg_res_itr['seg_ret_stats']['Return(Ann.)'].loc['long_short']
#         seg_ret_list.append(seg_res_itr['seg_ret']['long_short'])  # burn data
#
#     seg_ret_df = pd.concat(seg_ret_list, axis=1)
#     seg_ret_df.columns = rl
#
#     dynamic_piece_list = []
#     for i in rebal_itr:
#         ei = min(i + rebal_freq, dat_len - 1)
#         r_use = seg_ret_df.iloc[:i].mean().argmax()
#         i_d, ei_d = dat_list[i + 1], dat_list[ei]
#         # print(i_d,ei_d,r_use)
#         score_use = score_ma_dict[r_use]
#         if rebal_itr.index(i) == 0:
#             piece_cut = score_use.loc[:i_d]
#         else:
#             piece_cut = score_use.loc[i_d:ei_d]
#
#         dynamic_piece_list.append(piece_cut)
#     dynamic_piece = pd.concat(dynamic_piece_list, axis=0)
#     return dynamic_piece


def calc_realized_corr_multi(minute_dat1, minute_dat2):
    corr_list = []
    prod_list = minute_dat1.columns.tolist()
    for prod in prod_list:
        if pd.DataFrame(minute_dat2).shape[1] == 1:
            corr_input = pd.concat([minute_dat1[prod], minute_dat2], axis=1)
        else:
            corr_input = pd.concat([minute_dat1[prod], minute_dat2[prod]], axis=1)
        corr_input.columns = [corr_input.columns[0], corr_input.columns[1] + '1']
        corr_itr = corr_input.groupby(corr_input.index.date).apply(lambda x: x.corr())
        cl = corr_itr.columns
        corr_itr_ret = corr_itr[cl[0]].xs(cl[1], level=1)
        corr_list.append(corr_itr_ret)
    realized_corr = pd.concat(corr_list, axis=1)
    return realized_corr


def create_cmty_universe(volume, listing_day_cut=120, volume_win=30, volume_cut=1e4):
    """universe definition:
	1. listing for at least 120 days
	2. prev n1 days, avg trading volume larger than n2
		n1= 20, n2 = 1e4
	cmty_universe: True as in the universe
	"""
    listing_day_count = np.isfinite(volume).expanding().apply(np.nansum)
    listing_day_mask = listing_day_count > listing_day_cut
    volume_ma = volume.rolling(volume_win, int(volume_win * 0.5)).mean()
    volume_mask = volume_ma > volume_cut
    cmty_universe = listing_day_mask & volume_mask
    cmty_universe = cmty_universe.shift(1)
    cmty_universe = cmty_universe.fillna(value=False)
    return cmty_universe


def check_tail_helper(fac_val, tail_length=238, min_pct=1):
    if isinstance(fac_val, pd.DataFrame):
        fav_val_tail = fac_val.iloc[-tail_length:, 0]
    elif isinstance(fac_val, pd.Series):
        fav_val_tail = fac_val.iloc[-tail_length:]
    cov_num = np.isfinite(fav_val_tail).sum()
    need_num = int(min_pct * tail_length)
    if cov_num < need_num:
        print('tail coverage failed: %d < %d' % (cov_num, need_num))
        raise Exception
    else:
        1 == 1
    # print('tail check pass')
    return


def prep_ps2df_save(fac_ps, fac_name, save_path=None, check_tail=True, tail_length=238, min_pct=1):
    fac_df = pd.DataFrame(fac_ps)
    fac_df.columns = [fac_name]
    fac_df.index.name = 'dt'
    print(fac_df.index[0], fac_df.index[-1])
    if check_tail:
        check_tail_helper(fac_df, tail_length=tail_length, min_pct=min_pct)
    if save_path is not None:
        save_ts_fac_helper(fac_df, save_path)
    return fac_df


# 以下为整理所有结果
import glob


def collect_backtest_result(save_root_path, return_res=False):
    return_stats_list = []
    cum_ret_list = []
    sig_name_list = []
    result_str = '_results.csv'
    res_name_list = ['model_stats', 'model_cumret']
    result_path_dict = {i + '.csv': os.path.join(save_root_path, '%s.csv' % (i)) for i in res_name_list}
    result_path_dict.update({i + '.png': os.path.join(save_root_path, '%s.png' % (i)) for i in res_name_list})
    for i in result_path_dict:
        file_iter = result_path_dict[i]
        if os.path.isfile(file_iter):
            print('remove file: %s' % (file_iter))
            os.remove(file_iter)

    for sigtype in os.listdir(save_root_path):
        if sigtype.find('.') < 0:
            spath = os.path.join(save_root_path, sigtype)
            pathlist_result = glob.glob(spath + '/*_results.csv')[0]
            pathlist_return = glob.glob(spath + '/*daily_return.csv')[0]
            sig_name = os.path.basename(pathlist_result).replace(result_str, '')
            stats_iter = pd.read_csv(pathlist_result, index_col=0, encoding='gbk')
            return_stats_list.append(stats_iter)
            sig_name_list.append(sig_name)

            ret_iter = pd.read_csv(pathlist_return, index_col=0)
            ret_iter[['daily_return']].iloc[0, :] = 0
            cum_ret_iter = ret_iter[['daily_return']].cumsum()
            cum_ret_list.append(cum_ret_iter)

    return_stats = pd.concat(return_stats_list, axis=1)
    cum_ret = pd.concat(cum_ret_list, axis=1)

    return_stats.columns = sig_name_list
    cum_ret.columns = sig_name_list

    return_stats.to_csv(os.path.join(save_root_path, 'model_stats.csv'), encoding='gbk')
    cum_ret.to_csv(os.path.join(save_root_path, 'model_cumret.csv'))

    cum_ret.plot(figsize=(20, 10), grid=True)
    plt.savefig(os.path.join(save_root_path, 'model_cumret.png'))
    if return_res:
        res_dict = {'stats': return_stats, 'cum_ret': cum_ret}
        return res_dict
    else:
        return


def collect_backtest_result_dat(backtest_res):
    sl = []
    for f in backtest_res:
        s = pd.DataFrame(backtest_res[f]['prof_stats'])
        s.columns = [f]
        sl.append(s)
    stats_df = pd.concat(sl, axis=1)
    print(stats_df)
    pl = []
    for f in backtest_res:
        p = pd.DataFrame(backtest_res[f]['profit'])
        p.columns = [f]
        pl.append(p)
    profit_df = pd.concat(pl, axis=1)
    profit_df.plot(figsize=[15, 10])
    return stats_df, profit_df


#### duplicate ~ factor_tool


############### multiprocess ############################

def multiprocess_wrapper(func, iter_list=None, logger=None, max_process=None,
                         collect_output=False, collect_status=False, print_para=True, **kwargs):
    """ func: list of function
				iter_list: list, dict(input inside)
		"""
    max_process = os.cpu_count() if max_process == None else max_process
    iter_input = False
    if iter_list is not None:
        if isinstance(iter_list, dict):
            task_number = len(list(iter_list.keys()))
            iter_input = True
        if isinstance(iter_list, list):
            task_number = len(iter_list)
    else:
        task_number = len(func)
    tic1 = time.time()
    if print_para:
        def pf(x):
            print(x)
            return
    else:
        def pf(x):
            return
    print_func_info = pf if logger is None else logger.info
    print_func_warning = pf if logger is None else logger.warning

    print_func_info('*' * 20)
    start_info = 'start multiprocess -  max process number: %d - task number: %d' % (max_process, task_number)
    print_func_info(start_info)
    if collect_output:
        manager_dict = Manager().dict()
        if iter_list is None:
            if len(func) - len(set(func)) != 0:
                print_func_warning('not unique func input for collecting output')
                raise Exception
    else:
        manager_dict = None
    status_dict = {}
    with Pool(max_process) as executor:
        print_func_info('*** task initialization ***')
        future_tasks = {}
        init_idx, ex_idx = 0, 0
        if iter_list is not None:
            for itr in iter_list:
                init_idx = init_idx + 1
                try:
                    print_func_info('* init %d/%d : %s *' % (init_idx, task_number, itr))
                    if iter_input:
                        future_tasks[executor.submit(func, iter_list[itr], **kwargs)] = itr
                    else:
                        future_tasks[executor.submit(func, itr, **kwargs)] = itr
                except Exception as e:
                    print_func_warning('iter task initialization failed: %s - %s' % (itr, e))
        elif iter_list is None:
            for fc in func:
                init_idx = init_idx + 1
                try:
                    print_func_info('* init %d/%d : %s' % (init_idx, task_number, fc))
                    future_tasks[executor.submit(fc, **kwargs)] = fc
                except Exception as e:
                    print_func_warning('func task init failed: %s - %s' % (fc, e))
        print_func_info('*** task execution ***')
        key_list = []
        for f in as_completed(future_tasks):
            if isinstance(f, dict) or isinstance(f, list):
                key = future_tasks[str(f)]
            else:
                key = future_tasks[f]
            key_list.append(key)
            ex_idx = ex_idx + 1
            try:
                done_ind = f.done()
            except Exception as e:
                print_func_warning('task execution failed - %s' % (e))
                f.cancel()
            if done_ind:
                try:
                    ts = f.result()
                    if manager_dict is not None:
                        manager_dict[key] = ts
                except Exception as e:
                    print_func_warning('%s' % (e))
                    ts = None
                    done_ind = None
            else:
                ts = None
            if isinstance(ts, np.float) or isinstance(ts, np.int):
                print_str = str((round((ts), 2))) + 's'
            elif isinstance(ts, str):
                print_str = ts
            else:
                print_str = ''
            done_str = 'done' if done_ind == True else 'fail'
            status_dict[key] = True if done_ind else False
            itr_info = '* %d/%d - %s -%s  %s *' % (ex_idx, task_number, done_str, key, print_str)
            if done_ind:
                print_func_info(itr_info)
            else:
                print_func_warning(itr_info)
            done_ind = None

    toc1 = time.time()
    time_str1 = str((round((toc1 - tic1) / 60, 2))) + 'minutes'
    end_info = '***** multiprocess end - %s ***' % (time_str1) + '\n' + '*' * 20
    print_func_info(end_info)
    if collect_output:
        value_dict = dict(zip(key_list, manager_dict.values()))
        if collect_status:
            return value_dict, status_dict
        else:
            return value_dict
    else:
        if collect_status:
            return status_dict
        return


def ts_factor_quick_univ(fac, price_df, layers=5, factor_kind='open_to_open', verbose=0, plot=True):
    res_itr_dict = {}
    res_df_list = []
    ret_ls_list = []
    show_image = True if verbose == 1 else False
    take_list_val = ['annual_ret', 'sharpe_Q%d-Q0' % (layers - 1), 'IC-1min',
                     'long_short_mdd', 'win_ratio', 'winloss_ret_ratio']
    rename_dict = {'annual_ret': 'ret', 'sharpe_Q%d-Q0' % (layers - 1): 'sharpe', 'IC-1min': 'ic',
                   'long_short_mdd': 'mdd', 'win_ratio': 'hit', 'winloss_ret_ratio': 'w2l'}
    univ_list = price_df.columns.tolist()
    univ_list.sort()
    if isinstance(fac.index, pd.MultiIndex):
        if isinstance(fac, pd.DataFrame):
            factor_name = fac.columns.tolist()[0]
            fac = fac.unstack()[factor_name]
        else:
            factor_name = 'univ_fac'
            fac = fac.unstack()
    else:
        if isinstance(fac, pd.DataFrame):
            if fac.shape[1] == len(univ_list):
                factor_name = 'univ_fac'
        else:
            factor_name = 'single_fac'
            fac = pd.concat([fac for tc_itr in univ_list], axis=1)
            fac.columns = univ_list
    for tc_itr in univ_list:
        fac_name = '%s ~ %s' % (tc_itr, factor_name)
        # print(fac_name)
        res_itr = ts_factor_quick(fac[tc_itr], price_df[tc_itr], fac_name, layers=layers,
                                  factor_kind=factor_kind, show_image=show_image)
        res_itr_dict[tc_itr] = res_itr
        # plt.show()
        ret_itr = res_itr['seg_ret'].reset_index().set_index(['dt', 'bins'])['ret'].unstack()
        ret_ls_itr = pd.DataFrame(ret_itr[layers - 1].fillna(0) - ret_itr[0].fillna(0), columns=[tc_itr])
        ret_ls_list.append(ret_ls_itr)

        res_itr_use = [res_itr[i] for i in take_list_val]
        res_itr_df = pd.DataFrame(res_itr_use, index=take_list_val, columns=[tc_itr])
        res_df_list.append(res_itr_df)
    res_df = pd.concat(res_df_list, axis=1)
    res_df_t = res_df.T
    res_df_t['calmar'] = -1 * res_df_t['annual_ret'] / res_df_t['long_short_mdd']
    res_df = res_df_t.T
    res_df = res_df.rename(index=rename_dict)
    res_df['univ'] = res_df[univ_list].mean(axis=1)

    ret_ls_df = pd.concat(ret_ls_list, axis=1)
    ret_ls_df['univ'] = ret_ls_df[univ_list].mean(axis=1)
    res_info = {'stats': res_df, 'ls_ret': ret_ls_df}
    if plot:
        print(res_df)
        ret_ls_df.cumsum().plot(figsize=[11, 5], title=fac_name)
        plt.show()
    return res_info


def transform2univ(single_fac, univ_list):
    uf_list = []
    single_fac.index.name = 'dt'
    for tc_itr in univ_list:
        sf_use = pd.DataFrame(single_fac)
        sf_use['Ticker'] = tc_itr
        sf_use = sf_use.reset_index().set_index(['dt', 'Ticker'])
        uf_list.append(sf_use)
    univ_fac = pd.concat(uf_list, axis=0).sort_index()
    return univ_fac


def transform2univ_mi(fac_df, univ_list):
    fac_univ_dict = {i: transform2univ(fac_df[i], univ_list) for i in fac_df}
    fac_univ_mi = dict2mi(fac_univ_dict).sort_index()
    return fac_univ_mi


# factor_tool duplicate

def dict2mi_helper(col, df_dict, sdate=None, edate=None, alpha_universe_mi=None):
    if sdate is not None and edate is not None:
        if isinstance(sdate, int):
            sdate_dt = pd.Timestamp(str(sdate))
            edate_dt = pd.Timestamp(str(edate))
        else:
            raise Exception
        slice_date = True
    else:
        slice_date = False
    obj_mi = df_dict[col].stack() if not isinstance(df_dict[col].index, pd.MultiIndex) else df_dict[col]
    if alpha_universe_mi is not None:
        obj_mi = obj_mi.reindex(index=alpha_universe_mi.index)
    obj_mi = obj_mi.loc[sdate_dt:edate_dt] if slice_date else obj_mi
    obj_mi = pd.DataFrame(obj_mi, columns=[col])
    if col == 'Industry':
        obj_mi = pd.get_dummies(obj_mi['Industry'])
        obj_mi.columns = [int(i) for i in obj_mi.columns.tolist()]
    return obj_mi


def dict2mi(df_dict, col_list=None, sdate=None, edate=None,
            alpha_universe_mi=None, verbose=False, parallel=False):
    tic = time.time()
    if col_list is None:
        if isinstance(df_dict, pd.DataFrame):
            col_list = df_dict.columns.tolist()
        elif isinstance(df_dict, dict):
            col_list = list(df_dict.keys())
    if sdate is not None and edate is not None:
        if isinstance(sdate, int):
            sdate_dt = pd.Timestamp(str(sdate))
            edate_dt = pd.Timestamp(str(edate))
        else:
            raise Exception
        slice_date = True
        if verbose:
            print('slice date %s - %s' % (str(sdate), str(edate)))
    else:
        slice_date = False
    if alpha_universe_mi is not None:
        if not isinstance(alpha_universe_mi.index, pd.MultiIndex):
            if verbose:
                print('stack alpha_universe to mi format')
            alpha_universe_mi = alpha_universe_mi.stack()
            alpha_universe_mi = alpha_universe_mi[alpha_universe_mi]
        if slice_date:
            alpha_universe_mi = alpha_universe_mi.loc[sdate_dt:edate_dt]

    if parallel:
        use_dict = multiprocess_wrapper(func=dict2mi_helper, iter_list=col_list,
                                        df_dict=df_dict, sdate=sdate, edate=edate,
                                        alpha_universe_mi=alpha_universe_mi, collect_output=True)
    else:
        use_dict = {}
        col_name = []
        col_num = len(col_list)
        for col in col_list:
            try:
                tic1 = time.time()
                obj_mi = df_dict[col].stack() if not isinstance(df_dict[col].index, pd.MultiIndex) else df_dict[col]
                if alpha_universe_mi is not None:
                    obj_mi = obj_mi.reindex(index=alpha_universe_mi.index)
                use_dict[col] = obj_mi.loc[sdate_dt:edate_dt] if slice_date else obj_mi
                if col == 'Industry':
                    industry_mi = df_dict[col] if isinstance(df_dict[col].index, pd.MultiIndex) else df_dict[col].stack()
                    use_dict[col] = pd.get_dummies(industry_mi)
                    col_name_current = [int(i) for i in use_dict[col].columns.tolist()]
                else:
                    col_name_current = [col]
                col_name = col_name + col_name_current
                toc1 = time.time()
            except:
                print('dict2mi failed for %s' % (col))
                raise Exception
            if verbose:
                print('stack - %d/%d - %s - %s' % (col_list.index(col) + 1, col_num, col, print_time(toc1, tic1)))
    col_list = list(use_dict.keys())
    col_num = len(col_list)
    if verbose:
        toc2 = time.time()
        print('stack %d fac done - %s' % (col_num, print_time(toc2, tic)))

    mi = pd.concat(list(use_dict.values()), axis=1)
    mi.columns = col_list
    if verbose:
        toc3 = time.time()
        print('concat all fac done - %s' % (print_time(toc3, toc2)))
        print('dict2mi done ~ %s' % (print_time(toc3, tic)))
    return mi


def show_time_spent(ts):
    if ts > 60:
        time_spent = (str((round((ts) / 60, 2))) + ' minutes')
    else:
        time_spent = (str((round((ts), 2))) + ' seconds')
    return time_spent


def print_time(toc, tic, show_time=True, remain_iter=None):
    ts = toc - tic
    time_spent = show_time_spent(ts)
    if remain_iter is not None:
        time_spent_total = '/ remain %s' % (show_time_spent(ts * remain_iter))
    else:
        time_spent_total = ''
    time_str = ' (used %s%s) ' % (time_spent, time_spent_total)
    if show_time:
        time_str = time_str + '- ' + print_current_time()
    return time_str


#################### 2022

def get_ret_vol(fts_data_is, fts_data_os):
    ret_vol_list = []
    trade_contract_list = ['IC.CFE', 'IF.CFE', 'IH.CFE', 'IM.CFE']
    # is_time = '20200630'
    # os_time = '20200701'
    is_time = '20201231'
    os_time = '20210101'

    for trade_contract in trade_contract_list:
        var_name = 'recent_month_mask'
        ticker_ini = trade_contract.split('.')[0].lower()
        rm_mask = pd.concat([fts_data_is[var_name].loc[:is_time],
                             fts_data_os[var_name].loc[os_time:]],
                            axis=0).fillna(value=False)
        var_name = 'close' if trade_contract == 'IC.CFE' else 'close_%s' % (ticker_ini)
        print(trade_contract, var_name)
        if trade_contract == 'IM.CFE':
            clse = fts_data_os[var_name].loc[os_time:]
        else:
            cls = pd.concat([fts_data_is[var_name].loc[:is_time],
                             fts_data_os[var_name].loc[os_time:]], axis=0)

        vol_win = 30
        min_pct = 0.5
        slice_range = ['9:30', '14:56']
        cls = cls.between_time(slice_range[0], slice_range[1])
        rt = cls / cls.shift(1) - 1
        rt_std = rt.rolling(vol_win, int(vol_win * min_pct)).std()
        ret_vol = rt_std[rm_mask].sum(axis=1)

        rt_fix = cls / cls.shift(1) - 1
        # mask_930 =[True if i.minute == 30 and i.hour ==9 else False for i in rt_fix.index]
        # rt_fix[mask_930] = np.nan
        rt_std_fix = rt_fix.rolling(vol_win, int(vol_win * min_pct)).std()
        ret_vol_fix = rt_std_fix[rm_mask].sum(axis=1)
        ret_vol_list.append(ret_vol)
    ret_vol_df = pd.concat(ret_vol_list, axis=1)
    ret_vol_df.columns = trade_contract_list
    return ret_vol_df


def calc_ts_vol_weight(ret_ts, vol_win=240, min_pct=0.5):
    vol_ts = ret_ts.rolling(vol_win, int(vol_win * 0.5)).std()
    vol_ts_inv = 1 / vol_ts
    vol_weight = vol_ts_inv.divide(vol_ts_inv.sum(axis=1), axis=0)
    return vol_weight


def calc_ic_stats(IC_ts):
    IC_mean = IC_ts.mean()
    IC_std = IC_ts.std()
    ICIR = IC_mean / IC_std  # *np.sqrt(240)
    IC_stats = pd.DataFrame([IC_mean, IC_std, ICIR], index=['IC_mean', 'IC_std', 'ICIR'])
    return IC_stats


# def calc_cs_ls_test(factor, price, universe, holding_period=1, seg_num=5):
#     print('%s' % ('-' * 50))
#     tic = time.time()
#     factor_use = factor.copy().reindex(columns=universe.columns)
#     price = price.reindex(columns=universe.columns)
#     hpr = calc_hpr(price, holding_period).reindex(index=factor_use.index)
#     factor_use = factor_use[universe.reindex(index=factor_use.index)]
#     date_list = factor_use.index.tolist()
#     date_s, date_e = date_list[0], date_list[-1]
#     print('hpr %d: %s - %s' % (holding_period, date_s, date_e))
#     ic_ts = factor_use.corrwith(hpr, axis=1)
#     ic_stats = calc_ic_stats(ic_ts)
#     print(ic_stats)
#     ic_ts.cumsum().dropna().plot(title='ic cumsum', figsize=[13, 3])
#     plt.show()
#
#     seg_res = calc_easy_seg(factor_use, hpr, seg_num=5)
#     res_dict = {'ic_stats': ic_stats, 'seg_res': seg_res, 'ic_ts': ic_ts}
#     toc = time.time()
#     print('%s - %s -%s' % ('-' * 10, print_time(toc, tic), '-' * 10))
#     print('%s' % ('-' * 50))
#     return res_dict


######################################################################################
# ts_back_test with filp trade

# 20220119 ts_backtest with flip


def get_overnight_idx_list(trade_signal):
    time_list = trade_signal.index.tolist()
    idx_list = [i for i in range(len(time_list))]
    time_index = pd.DataFrame(idx_list, index=time_list)
    daily_end_tick = time_index.groupby(time_index.index.date).agg(np.max)
    daily_start_tick = time_index.groupby(time_index.index.date).agg(np.min)
    end_idx_list = daily_end_tick.values.flatten()
    start_idx_list = daily_start_tick.values.flatten()
    return start_idx_list, end_idx_list


def send_msg_link(msg_str):
    from xquant.xqutils.helper import link
    lm = link.LinkMessage()
    lm.sendMessage(msg_str)
    return


def calc_hpr_recent(recent_price_dict, holding_period, trade_price, trade_contract):
    hpr_recent_df = calc_hpr(recent_price_dict[trade_price][trade_contract], holding_period)
    hpr_recent_df_mask = hpr_recent_df[recent_price_dict['recent_month_mask']]
    hpr = hpr_recent_df_mask.mean(axis=1)
    return hpr


def get_price_with_mask(fts_data_is, fts_data_os,
                        is_time='20191231', os_time='20200101',
                        # is_time = '20201231',
                        # os_time = '20210101',
                        trade_contract_list=['IC.CFE', 'IF.CFE', 'IH.CFE', 'IM.CFE'],
                        var_list=['open', 'close', 'vwap', 'twap']):
    recent_price_dict = {}
    var_name = 'recent_month_mask'
    rm_mask = pd.concat([fts_data_is[var_name].loc[:is_time],
                         fts_data_os[var_name].loc[os_time:]],
                        axis=0).fillna(value=False)
    recent_price_dict[var_name] = rm_mask
    for var_itr in var_list:
        recent_price_dict[var_itr] = {}
        for tc_itr in trade_contract_list:
            ticker_ini = tc_itr.split('.')[0].lower()
            var_name = var_itr if tc_itr == 'IC.CFE' else '%s_%s' % (var_itr, ticker_ini)
            print(tc_itr, var_name)
            if tc_itr == 'IM.CFE':
                cls = fts_data_os[var_name].loc[os_time:]
            else:
                cls = pd.concat([fts_data_is[var_name].loc[:is_time],
                                 fts_data_os[var_name].loc[os_time:]], axis=0)
            # slice_range = ['9:30','14:56']
            # cls = cls.between_time(slice_range[0],slice_range[1])
            recent_price_dict[var_itr][tc_itr] = cls

    return recent_price_dict


def get_null_df(fac_score, fill_value=np.nan):
    fac_mask = np.isfinite(fac_score)
    null_df = place_back_format(np.full_like(fac_score, fill_value=fill_value), fac_score)
    null_df[~fac_mask] = np.nan
    null_df[fac_mask] = fill_value
    return null_df


###############
### ts meta factor

def get_calendar_info(dat_raw):
    dt_list = dat_raw.index.tolist()
    # where 0 is Sunday and 6 is Saturday.
    weekday_list = np.array([int(dt.datetime.strftime(i, '%w')) for i in dt_list])
    month_list = np.array([int(dt.datetime.strftime(i, '%-m')) for i in dt_list])
    year_list = np.array([int(dt.datetime.strftime(i, '%-Y')) for i in dt_list])
    calendar_info = pd.DataFrame(np.array([weekday_list, month_list, year_list]).T, index=dt_list)
    calendar_info.columns = ['week', 'month', 'year']
    return calendar_info


def get_dummies_helper(dat_cat, dummy_na=False):
    cat_list = []
    dat_cat = dat_cat.astype('category')
    for col in dat_cat:
        cat_list.append(pd.get_dummies(dat_cat[col], prefix=col, dummy_na=dummy_na))
    dummies_df = pd.concat(cat_list, axis=1)
    return dummies_df
