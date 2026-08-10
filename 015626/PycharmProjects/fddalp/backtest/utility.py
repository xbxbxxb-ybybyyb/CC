import numpy as np
import pandas as pd
import statsmodels.api as sm
import time
import datetime as dt
#from multifactor.utility.common import resider
#import ntplib
#import hashlib


def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(tic=dt.datetime.now())
def pprint(*args, **kwargs):
    print(('%.3fs <- prev msg: ' % (dt.datetime.now() - pprint.tic).total_seconds()).rjust(22), *args, **kwargs)
    pprint.tic = dt.datetime.now()


def excel_saver(output_dict, excel_name):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key)
    writer.save()
    return


def max_drawdown(capital_line):
    # return max draw down in decimal
    mdd_end = np.argmax(np.maximum.accumulate(capital_line) - capital_line)
    if mdd_end == 0:
        return np.nan
    mdd_start = np.argmax(capital_line[:mdd_end])
    mdd = 1 - capital_line[mdd_end] / capital_line[mdd_start]
    return mdd


def segment_test(factor_pd, stock_close_pd, holding_period, benchmark_price_ps, segment_num, handle_insufficient=False):
    # given matrix style factor and stock close prices, calculate benchmark return and factor sgement returns
    holding_period_ret = stock_close_pd.shift(-1 * holding_period) / stock_close_pd - 1
    benchmark_holding_period_ret = benchmark_price_ps.shift(-1 * holding_period) / benchmark_price_ps - 1
    holding_period_ret_daily = (holding_period_ret + 1) ** (1 / holding_period) - 1
    holding_period_ret_daily_mat = holding_period_ret_daily.values
    benchmark_holding_period_ret_daily =(benchmark_holding_period_ret + 1) ** (1 / holding_period) - 1
    factor_pd_mat = factor_pd.values
    date_num = factor_pd.shape[0]
    easy_seg_return_mat = np.zeros([date_num, segment_num])
    for i in range(date_num):
        easy_seg_return_mat[i, :] = segment_test_daily(factor_pd_mat[i, :], holding_period_ret_daily_mat[i, :],
                                                       segment_num, handle_insufficient=handle_insufficient)
    name_pool = ['Q' + str(segment_num - i) for i in range(int(segment_num))]
    easy_seg_return = pd.DataFrame(easy_seg_return_mat, columns=name_pool, index=factor_pd.index)
    name_pool_reversed = [item for item in reversed(name_pool)]
    easy_seg_return = easy_seg_return[name_pool_reversed]
    easy_seg_return['Benchmark'] = benchmark_holding_period_ret_daily
    easy_seg_return['Benchmark'][~easy_seg_return.any(axis=1)] = np.nan
    _ = easy_seg_return[[name_pool[0], name_pool[-1]]].mean()
    max_quantile, min_quantile = _.idxmax(), _.idxmin()
    easy_seg_return[max_quantile + '-' + min_quantile] = easy_seg_return[max_quantile] - easy_seg_return[min_quantile]
    return easy_seg_return


def segment_test_daily(factor_score, daily_return, segment_num, handle_insufficient=False):
    factor_ret = np.stack([factor_score, daily_return], axis=1)
    factor_ret_sorted = factor_ret[factor_ret[:, 0].argsort()]  # sort by factor score - small to large
    valid_pair_num = np.count_nonzero(np.isfinite(factor_ret.sum(axis=1)))
    valid_factor_num = np.count_nonzero(np.isfinite(factor_ret[:, 0]))
    if valid_pair_num < segment_num:
        if handle_insufficient and valid_pair_num >= 1:
            return [np.nanmean(factor_ret_sorted[:,1])] * segment_num
        else:
            return [np.nan] * segment_num
    num_per_quantile = int(valid_factor_num / segment_num)
    idx_seperators = np.arange(0, valid_pair_num, num_per_quantile) if segment_num > 1 else [0]
    idx_seperators = idx_seperators[:segment_num] if segment_num > 1 else [0]  # there may be stock left due to rounding error
    seg_ret_reversed = [np.nanmean(factor_ret_sorted[i:i + num_per_quantile, 1]) for i in idx_seperators]
    return seg_ret_reversed


def multi_index_to_dataframe(h5_data):
    data_dict = {}
    for factor in h5_data.columns:
        data_dict[factor] = h5_data[factor].unstack()
    return data_dict

 

def get_industry_weight(stock_industry, benchmark='hs300'):
    start_date, end_date = stock_industry.index[0], stock_industry.index[-1]
    assert benchmark in ['hs300', 'zz500', 'sh50', 'alla']
    if benchmark in ['hs300','zz500','sh50']:
        stock_weight = IO.read_data([start_date, end_date], columns='index_weight_'+benchmark,
                                     dsource=DSource.OPTM, ftype=FType.UNIV)
        stock_weight.columns= ['stock_weight']
    else:
        mkt_cap_ard_MI = IO.read_data([start_date, end_date], columns=['mkt_cap_ard'],
                                       ftype=FType.MD, dsource=DSource.WIND)
        stock_weight = mkt_cap_ard_MI / mkt_cap_ard_MI.groupby('dt').sum()
        stock_weight.columns= ['stock_weight']
    _stock_industry = pd.DataFrame(stock_industry.stack(), columns=['Industry'])
    weight_grouped = pd.concat([_stock_industry, stock_weight], axis=1).groupby(['dt', 'Industry'])
    industry_weight = weight_grouped['stock_weight'].sum()
    # normalized to 1.0
    return industry_weight / industry_weight.groupby('dt').sum()


def segment_test_by_industry(factor_pd, stock_close_pd, holding_period, benchmark_price_ps, segment_num,
                             stock_industry, industry_weight, handle_insufficient=True):
    seg_return_by_industry = []
    name_pool = ['Q' + str(i) for i in range(1, int(segment_num+1))]
    col_selector = name_pool + ['Benchmark']
    for idx in pd.Series(np.unique(stock_industry)).dropna():
        # reduce the calculation dimension by dropping columns
        factor_filtered = factor_pd[stock_industry==idx].dropna(axis=1, how='all')
        seg_return = segment_test(factor_filtered,
                                  stock_close_pd.reindex(columns=factor_filtered.columns),
                                  holding_period, benchmark_price_ps,
                                  segment_num, handle_insufficient)[col_selector]
        seg_return['Industry'] = idx
        seg_return_by_industry.append(seg_return)
    seg_return_combined = pd.concat(seg_return_by_industry, axis=0).reset_index().set_index(['dt','Industry'])
    res = seg_return_combined.multiply(industry_weight, axis=0).groupby('dt').sum()
    res['Benchmark'] = seg_return['Benchmark']
    _ = res[[name_pool[0], name_pool[-1]]].mean()
    max_quantile, min_quantile = _.idxmax(), _.idxmin()
    res[max_quantile + '-' + min_quantile] = res[max_quantile] - res[min_quantile]
    return res




def align_data_inner(data_dict):
    # maybe should use dt, Ticker instead
    i = 0
    for factor in data_dict:
        if np.any([isinstance(data_dict[factor], _type) for _type in [pd.DataFrame, pd.Series]]):
            if isinstance(data_dict[factor].index, pd.core.index.MultiIndex):
                if 'dt' in data_dict[factor].index.names:
                    if i == 0:
                        date_list = list(set(data_dict[factor].index.get_level_values(level=0).tolist()))
                        i = i + 1
                    else:
                        date_list = np.intersect1d(date_list, list(set(data_dict[factor].index.get_level_values(level=0).tolist())))
            else:
                if type(data_dict[factor]) == pd.DataFrame:
                    if i == 0:
                        stock_list = data_dict[factor].columns.tolist()
                        date_list = data_dict[factor].index.tolist()
                        i = i + 1
                    else:
                        stock_list = np.intersect1d(stock_list, data_dict[factor].columns.tolist())
                        date_list = np.intersect1d(date_list, data_dict[factor].index.tolist())
                else:  # Series
                    if i == 0:
                        date_list = data_dict[factor].index.tolist()
                        i = i + 1
                    else:
                        date_list = np.intersect1d(date_list, data_dict[factor].index.tolist())
        elif type(data_dict[factor]) == dict:
            for nested_factor in data_dict[factor]:
                if type(data_dict[factor][nested_factor]) == pd.DataFrame:
                    if i == 0:
                        stock_list = data_dict[factor][nested_factor].columns.tolist()
                        date_list = data_dict[factor][nested_factor].index.tolist()
                        i = i + 1
                    else:
                        stock_list = np.intersect1d(stock_list, data_dict[factor][nested_factor].columns.tolist())
                        date_list = np.intersect1d(date_list, data_dict[factor][nested_factor].index.tolist())
        else:
            continue
    data_dict_aligned = {}
    for factor in data_dict:
        if np.any([isinstance(data_dict[factor], _type) for _type in [pd.DataFrame, pd.Series]]):
            if isinstance(data_dict[factor].index, pd.core.index.MultiIndex):
                if 'dt' in data_dict[factor].index.names:
                    data_dict_aligned[factor] = data_dict[factor].loc[date_list]
            else:
                if type(data_dict[factor]) == pd.DataFrame:
                    data_dict_aligned[factor] = data_dict[factor].loc[date_list, stock_list]
                else:
                    data_dict_aligned[factor] = data_dict[factor].loc[date_list]
        elif type(data_dict[factor]) == dict:
            data_dict_aligned[factor] = {}
            for nested_factor in data_dict[factor]:
                if type(data_dict[factor][nested_factor]) == pd.DataFrame:
                    data_dict_aligned[factor][nested_factor] = data_dict[factor][nested_factor].loc[date_list, stock_list]
    return data_dict_aligned



def box_skew_algo(x):
    y = np.array(x)
    x = y[~np.isnan(y)]
    if len(np.unique(x)) < 10:
        return y
    x = np.sort(x)
    md = np.median(x)
    q3 = np.percentile(x, 75)
    q1 = np.percentile(x, 25)
    iqr = q3 - q1
    rx = np.flip(x, axis=0)
    x, rx = zip(*[(i, j) for i, j in zip(x, rx) if i != j])
    x = np.split(np.array(x), 2)[1]
    rx = np.split(np.array(rx), 2)[1]
    if len(x) < 5:
        return y
    mc = np.median((x + rx - 2.0 * md) / (x - rx))
    a, b = (3.5, 4.0) if mc >= 0 else (4.0, 3.5)
    L = q1 - 1.5 * np.exp(-a * mc) * iqr
    U = q3 + 1.5 * np.exp(b * mc) * iqr
    y[np.array([item < L if not np.isnan(item) else False for item in y])] = L
    y[np.array([item > U if not np.isnan(item) else False for item in y])] = U
    return y


def BoxSkewPlot(pd_raw, axis=1):
    if type(pd_raw) == pd.DataFrame:
        pd_process = pd_raw.copy()
        return pd_process.apply(box_skew_algo, axis=axis)
    else:
        raise AssertionError


def norm_winsor(factor_pd, bound=3, winsor=False):
    factor_pd = factor_pd.copy()
    factor_pd = median_filter(factor_pd, mad=bound, winsor=winsor, inplace=True)
    std_ts = factor_pd.std(axis=1, ddof=0)
    std_ts.loc[std_ts == 0] = 1
    factor_pd = factor_pd.subtract(factor_pd.mean(axis=1), axis=0).divide(std_ts, axis=0)
    return factor_pd


def median_filter(factor_pd, mad=3, winsor=False, inplace=False):
    if not inplace:
        factor_pd = factor_pd.copy()
    dm = factor_pd.median(axis=1)
    # caution of symmetric uppper & lower bounds
    dist_dm = (factor_pd.subtract(dm, axis=0)).abs().median(axis=1)
    date_num, stock_num = factor_pd.shape
    fac_ub = pd.DataFrame(np.tile(dm + mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    fac_lb = pd.DataFrame(np.tile(dm - mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    if winsor:
        factor_pd[factor_pd > fac_ub] = np.nan
        factor_pd[factor_pd < fac_lb] = np.nan
    else:
        factor_pd[factor_pd > fac_ub] = fac_ub
        factor_pd[factor_pd < fac_lb] = fac_lb
    return factor_pd


def regression_ols(y, x):
    # calculate ols problem given y as DataFrame and x as dictionary with DataFrames of regressors
    assert(isinstance(x, dict))
    date_num, stock_num = y.shape
    x_list = list(x.keys())
    contains_industry = True if 'Industry' in x_list else False
    x_num = len(x_list) - 1 if contains_industry else len(x_list)
    x_mat = np.ones([x_num, date_num, stock_num])
    y_mat = np.array(y)
    r2_mat = np.empty(date_num)
    r2_mat[:] = np.nan
    beta_mat = np.empty([date_num, x_num+1])
    beta_mat[:] = np.nan
    tstats_mat = beta_mat.copy()
    res_mat = np.full_like(y, np.nan, dtype=np.double)

    if contains_industry:
        ind_mat = np.array(x['Industry'])
        x_list.remove('Industry')
    i = 0
    for x_name in x_list:
        x_mat[i, :, :] = np.array(x[x_name])
        i = i + 1

    for date_idx in range(date_num):
        if contains_industry:
            ind_dum = pd.get_dummies(ind_mat[date_idx, :]).values
            _x = np.column_stack([x_mat[:, date_idx, :].T, ind_dum])
        else:
            _x = x_mat[:, date_idx, :].T
        try:
            res_mat[date_idx, :], r2_mat[date_idx], beta_mat[date_idx, :], tstats_mat[date_idx, :] = stats_model_ols(y_mat[date_idx, :], _x)
        except ValueError:
            pass

    res = pd.DataFrame(res_mat, columns=y.columns, index=y.index)
    r2 = pd.Series(r2_mat, index=y.index)
    beta = pd.DataFrame(beta_mat, columns=['intercept']+x_list, index=y.index)
    tstats = pd.DataFrame(tstats_mat, columns=['intercept']+x_list, index=y.index)
    return res, r2, beta, tstats


def stats_model_ols(y, x, min_percentage=20):
    res = np.full_like(y, np.nan, dtype=np.double)
    mask = np.isfinite(y + x.sum(axis=1))
    if np.count_nonzero(mask) / len(mask) * 100 < min_percentage:
        raise ValueError
    ols = resider(x[mask], y[mask], method='sm.OLS', add_const=True, mean_only=False, r_square=False, return_sm=True)
    res[mask] = ols.resid
    return res, ols.rsquared, ols.params, ols.tvalues



def resider(x, y, method='lstsq', add_const=True, mean_only=False, r_square=False, return_sm=False):
    # Two step regression
    # 1: Determine dummy columns in matrix and use them to remove mean
    # 2: Regular ols: OLS or least square to calculate residual
    # Direct OLS or least square may have problems with dummy columns with few 1s
    # Less computation and more robustness
    # x -> axis0: stocks, axis1: factors
    y = y.flatten()  # 1-D array
    dummy_cols = np.apply_along_axis(is_dummy, 0, x)
    d_array = x[:, dummy_cols]
    s_array = x[:, ~dummy_cols]
    r2 = np.nan
    if d_array.shape[1] != 0:
        d_mean_array = np.array([i / j if j != 0 else 0 for i, j in
                                 zip(np.dot(d_array.T, y).flatten(), d_array.sum(axis=0))])
        y = y - np.dot(d_array, d_mean_array)
    if not mean_only and s_array.shape[1] != 0:
        if method == 'lstsq':
            if add_const:
                # Prepend constant in accordance with sm.OLS
                x = np.concatenate((np.ones((s_array.shape[0], 1)), s_array), axis=1)
            else:
                x = s_array
            try:
                coeff, residual_sum = np.linalg.lstsq(x, y, rcond=None)[0:2]
                resid = y - np.dot(x, coeff)
                if r_square:
                    r2 = 1 - residual_sum[0] / (y.size * y.var())
            except:
                resid = np.full_like(y, np.nan, dtype=np.double)
        elif method == 'sm.OLS':
            import statsmodels.api as sm
            x = s_array
            try:
                if add_const:
                    ols_problem = sm.OLS(y, sm.add_constant(x)).fit()
                else:
                    ols_problem = sm.OLS(y, x).fit()
                if return_sm:
                    return ols_problem
                resid = ols_problem.resid
                if r_square:
                    r2 = ols_problem.rsquared
            except:
                resid = np.full_like(y, np.nan, dtype=np.double)
        else:
            raise AssertionError
    else:
        resid = y
    if r_square:
        return resid, r2
    else:
        return resid


def is_dummy(x):
    x = np.array(x) if not isinstance(x, np.ndarray) else x
    one_num = np.count_nonzero(x == 1)
    zero_num = np.count_nonzero(x == 0)
    if one_num + zero_num == x.size:
        return True
    else:
        return False
