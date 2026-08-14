import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import bottleneck
import numpy as np
import pandas as pd
import warnings

from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date

warnings.filterwarnings("ignore")

source_path = '/data/group/800442/800319/Timing/BackTest/Source/'
label_path = '/data/group/800442/800319/Timing/FixFactor/FixFactor/label/'
wf1d1000 = np.load(f'{label_path}/wf1d1000.npy')
month_list = [100 * x + y for x in range(2015, 2022) for y in range(1, 13)]
date_list = get_date_range(20140601, 20211231)
mdd_dates = pd.read_pickle(f'{source_path}/market_mdd_dates.pkl')
real_time_factor = pd.read_pickle(f'{source_path}/real_time_std_factor.pkl')
real_time_max = real_time_factor > 10
real_time_min = real_time_factor == 0
benchmark = pd.read_pickle(f'{source_path}/bench_close.pkl')

def load_timing_factor(name):
    address1 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/CrossFactor/'
    address2 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/factor/'
    address3 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/HeredityFactor/'
    address4 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/wyl/factor_values/'
    try:
        factor = np.load(f'{address1}/{name}.npy')
    except:
        try:
            factor = np.load(f'{address2}/{name}.npy')
        except:
            try:
                factor = np.load(f'{address3}/{name}.npy')
            except:
                factor = np.load(f'{address4}/{name}.npy')
    return factor


def load_timing_factor_test(name, item):
    address1 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewCrossFactorTest/'
    address2 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewFixFactorTest/'
    address3 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewHeredityFactorTest/'
    address4 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/DiscreteFactorTest/'
    try:
        factor = pd.read_pickle(f'{address1}/{name}.pkl')[item]
    except:
        try:
            factor = pd.read_pickle(f'{address2}/{name}.pkl')[item]
        except:
            try:
                factor = pd.read_pickle(f'{address3}/{name}.pkl')[item]
            except:
                factor = pd.read_pickle(f'{address4}/{name}.pkl')[item]
    return factor


def calc_test_months(freq='Y', start=201512, end=202112):
    ml = [x for x in month_list if (x >= start) & (x <= end)]
    freq_dic = {'Y': 12, 'H': 6, 'Q': 3, 'M': 1}
    return ml[::freq_dic[freq]]


def calc_end_date(end_month):
    return get_recent_trade_date(end_month * 100 + 31)


def calc_start_date(end_month, signal_months=12, all_start=20150105):
    if month_list.index(end_month) - signal_months < 0:
        return all_start
    else:
        return get_pre_trade_date(get_recent_trade_date(month_list[month_list.index(
            end_month) - signal_months] * 100 + 31), -1)


def corr_filter(corr, limit=0.7):
    corr = corr.copy()
    rank = np.arange(corr.shape[0])
    corr_triu = np.tril_indices(corr.shape[0])
    corr[corr_triu] = 0.
    corr_pool = corr.max(axis=0) < limit
    _corr_pool_num1 = 0
    _corr_pool_num2 = corr_pool.sum()
    while _corr_pool_num2 > _corr_pool_num1:
        _corr_pool_num1 = _corr_pool_num2
        corr[corr[corr_pool].max(axis=0) >= limit] = 0
        corr_pool = corr.max(axis=0) < limit
        _corr_pool_num2 = corr_pool.sum()
    return rank[corr_pool]


def d2_move_max(arr, d, pct):
    shape = arr.shape
    move = d * shape[1]
    x = arr.copy().flatten()
    nf = ~np.isfinite(x)
    x[nf] = -np.inf
    x = bottleneck.move_rank(x, move)
    f = bottleneck.move_sum(nf.astype(x.dtype), move)
    x = ((x + 1) / 2 * (move - 1) - f) / np.fmax(move - f - 1, 1)
    x = x.reshape(shape)[d - 1:] > max(pct, 1 - pct)
    return x


def d2_move_min(arr, d, pct):
    return d2_move_max(-arr, d, pct)


def d2_corr(x, y):
    f = np.isfinite(x) & np.isfinite(y)
    return np.corrcoef(x[f], y[f])[0, 1]


def test_factor_1p(factor, future, start_idx, end_idx, sub_list, pct_max, pct_min, move_d):
    x = factor[start_idx - move_d + 1: end_idx + 1].copy()
    y = future[start_idx: end_idx + 1].copy()
    nf = (~ np.isfinite(x[move_d - 1:])).mean()

    ic = d2_corr(x[move_d - 1:], y)
    ic_sign = np.sign(ic)
    ic_abs = np.fabs(ic)
    x *= ic_sign
    ic_pos = d2_corr(x[move_d - 1:][y > 0], y[y > 0])
    ic_neg = d2_corr(x[move_d - 1:][y < 0], y[y < 0])

    x_max = d2_move_max(x, move_d, pct_max)
    x_min = d2_move_min(x, move_d, pct_min)

    # 1 signal test
    x_max_pct = x_max.mean()
    x_min_pct = x_min.mean()

    x_max_pct_d = np.any(x_max, axis=1).mean()
    x_min_pct_d = np.any(x_min, axis=1).mean()

    x_max_mean = y[x_max].mean()
    x_min_mean = y[x_min].mean()
    y_mean = y.mean()

    x_max_pos = (x_max & (y > 0.001)).sum() / x_max.sum()
    x_min_pos = (x_min & (y < -0.001)).sum() / x_min.sum()
    y_max_pos = (y > 0.001).sum() / np.isfinite(y).sum()
    y_min_pos = (y < -0.001).sum() / np.isfinite(y).sum()

    x_max_pnl = - y[x_max & (y > 0)].mean() / y[x_max & (y < 0)].mean()
    x_min_pnl = - y[x_min & (y < 0)].mean() / y[x_min & (y > 0)].mean()
    y_max_pnl = - y[y > 0].mean() / y[y < 0].mean()
    y_min_pnl = - y[y < 0].mean() / y[y > 0].mean()

    # 2 mdd test
    mdd_sub_idx = [x for x in mdd_dates if x in sub_list]
    mdd_sub_idx = [sub_list.index(x) for x in mdd_sub_idx]
    xm_max = x_max[mdd_sub_idx]
    xm_min = x_min[mdd_sub_idx]
    ym = y[mdd_sub_idx]

    xm_max_pct = xm_max.mean()
    xm_min_pct = xm_min.mean()

    xm_max_mean = ym[xm_max].mean()
    xm_min_mean = ym[~ xm_min].mean()
    ym_mean = ym.mean()

    xm_max_pos = (xm_max & (ym > 0.001)).sum() / xm_max.sum()
    xm_min_pos = ((~xm_min) & (ym > 0.001)).sum() / xm_min.sum()
    ym_pos = (ym > 0.001).sum() / np.isfinite(ym).sum()

    xm_max_std = ym[xm_max].std(ddof=1)
    xm_min_std = ym[~xm_min].std(ddof=1)
    ym_std = ym.std(ddof=1)

    xm_max_year = np.expm1(244 * (xm_max_mean - 0.5 * xm_max_std ** 2))
    xm_max_sp = xm_max_year / xm_max_std / 244 ** 0.5
    xm_min_year = np.expm1(244 * (xm_min_mean - 0.5 * xm_min_std ** 2))
    xm_min_sp = xm_min_year / xm_min_std / 244 ** 0.5
    ym_year = np.expm1(244 * (ym_mean - 0.5 * ym_std ** 2))
    ym_sp = ym_year / ym_std / 244 ** 0.5

    xm_max_mdd = np.cumprod(1 + ym[xm_max])
    xm_max_mdd = (1 - xm_max_mdd / np.maximum.accumulate(xm_max_mdd)).max() if xm_max_mdd.shape[0] else np.nan
    xm_max_cm = xm_max_year / xm_max_mdd

    xm_min_mdd = np.cumprod(1 + ym[~ xm_min])
    xm_min_mdd = (1 - xm_min_mdd / np.maximum.accumulate(xm_min_mdd)).max() if xm_min_mdd.shape[0] else np.nan
    xm_min_cm = xm_min_year / xm_min_mdd

    ym_mdd = np.cumprod(1 + ym)
    ym_mdd = (1 - ym_mdd / np.maximum.accumulate(ym_mdd)).max() if ym_mdd.shape[0] else np.nan
    ym_cm = ym_year / ym_mdd

    # 3 val test
    d_max = np.where(x_max, y - 0.002, 0).mean(axis=1)
    d_min = np.where(x_min, y + 0.002, 0).mean(axis=1)
    d_max_pct = x_max.mean(axis=1)
    d_min_pct = x_min.mean(axis=1)
    d_max_val = np.cumprod(1 + d_max)
    d_min_val = np.cumprod(1 + d_min)
    d_max_year = d_max_val[-1] ** (244 / d_max_val.shape[0]) - 1
    d_min_year = d_min_val[-1] ** (244 / d_min_val.shape[0]) - 1
    d_max_std = d_max.std(ddof=1)
    d_min_std = d_min.std(ddof=1)
    d_max_sp = d_max_year / d_max_std / 244 ** 0.5
    d_min_sp = d_min_year / d_min_std / 244 ** 0.5
    d_max_mdd = (1 - d_max_val / np.maximum.accumulate(d_max_val)).max() if d_max_val.shape[0] else np.nan
    d_min_mdd = (d_min_val / np.minimum.accumulate(d_min_val)).max() if d_min_val.shape[0] else np.nan
    d_max_cm = d_max_year / d_max_mdd
    d_min_cm = d_min_year / d_min_mdd

    bench = benchmark.loc[get_pre_trade_date(sub_list[0]):sub_list[-1]] / benchmark.loc[get_pre_trade_date(sub_list[0])]
    bench_year = bench.iloc[-1] ** (244 / bench.shape[0]) - 1
    bench_std = bench.pct_change().std(ddof=1)
    bench_sp = bench_year / bench_std / 244 ** 0.5
    bench_mdd = (1 - bench / np.maximum.accumulate(bench)).max()
    bench_cm = bench_year / bench_mdd

    series = pd.DataFrame({'多头仓位': d_max_pct, '空头仓位': d_min_pct,
                           '多头净值': d_max_val, '空头净值': d_min_val}, index=sub_list)
    series = pd.concat([series, bench.iloc[1:]], axis=1)

    # 4 base corr
    common_dates = [x for x in sub_list if (x >= 20170104) & (x <= 20210528)]
    if not common_dates:
        max_corr = np.nan
        min_corr = np.nan
    else:
        max_r = real_time_max.loc[common_dates[0]: common_dates[-1]].values
        min_r = real_time_min.loc[common_dates[0]: common_dates[-1]].values
        common_index = [sub_list.index(x) for x in common_dates]
        max_t = x_max[common_index]
        min_t = x_min[common_index]
        max_corr = 1 - (max_r & max_t).sum() / max_t.sum()
        min_corr = 1 - (min_r & min_t).sum() / min_t.sum()

    res = [nf, ic_sign, ic_abs, ic_pos, ic_neg, max_corr, min_corr,
           x_max_pct, x_min_pct, x_max_pct_d, x_min_pct_d,
           x_max_mean, x_min_mean, y_mean, x_max_pos, x_min_pos, y_max_pos, y_min_pos,
           x_max_pnl, x_min_pnl, y_max_pnl, y_min_pnl,
           xm_max_pct, xm_min_pct, xm_max_mean, xm_min_mean, ym_mean,
           xm_max_pos, xm_min_pos, ym_pos,
           xm_max_year, xm_min_year, ym_year, xm_max_sp, xm_min_sp, ym_sp,
           xm_max_mdd, xm_min_mdd, ym_mdd, xm_max_cm, xm_min_cm, ym_cm,
           d_max_year, d_min_year, d_max_sp, d_min_sp,
           d_max_mdd, d_min_mdd, d_max_cm, d_min_cm,
           ]

    res = res + bench_year.tolist() + bench_sp.tolist() + bench_mdd.tolist() + bench_cm.tolist()
    return res, series


def test_signal_1p(factor, future, start_idx, end_idx, sub_list):
    x = factor[start_idx: end_idx + 1].copy()
    y = future[start_idx: end_idx + 1].copy()

    x_max = x == 1
    x_min = x == -1

    # 1 signal test
    x_max_pct = x_max.mean()
    x_min_pct = x_min.mean()

    x_max_pct_d = np.any(x_max, axis=1).mean()
    x_min_pct_d = np.any(x_min, axis=1).mean()

    x_max_mean = y[x_max].mean()
    x_min_mean = y[x_min].mean()
    y_mean = y.mean()

    x_max_pos = (x_max & (y > 0.001)).sum() / x_max.sum()
    x_min_pos = (x_min & (y < -0.001)).sum() / x_min.sum()
    y_max_pos = (y > 0.001).sum() / np.isfinite(y).sum()
    y_min_pos = (y < -0.001).sum() / np.isfinite(y).sum()

    x_max_pnl = - y[x_max & (y > 0)].mean() / y[x_max & (y < 0)].mean()
    x_min_pnl = - y[x_min & (y < 0)].mean() / y[x_min & (y > 0)].mean()
    y_max_pnl = - y[y > 0].mean() / y[y < 0].mean()
    y_min_pnl = - y[y < 0].mean() / y[y > 0].mean()

    # 2 mdd test
    mdd_sub_idx = [x for x in mdd_dates if x in sub_list]
    mdd_sub_idx = [sub_list.index(x) for x in mdd_sub_idx]
    xm_max = x_max[mdd_sub_idx]
    xm_min = x_min[mdd_sub_idx]
    ym = y[mdd_sub_idx]

    xm_max_pct = xm_max.mean()
    xm_min_pct = xm_min.mean()

    xm_max_mean = ym[xm_max].mean()
    xm_min_mean = ym[~ xm_min].mean()
    ym_mean = ym.mean()

    xm_max_pos = (xm_max & (ym > 0.001)).sum() / xm_max.sum()
    xm_min_pos = ((~xm_min) & (ym > 0.001)).sum() / xm_min.sum()
    ym_pos = (ym > 0.001).sum() / np.isfinite(ym).sum()

    xm_max_std = ym[xm_max].std(ddof=1)
    xm_min_std = ym[~xm_min].std(ddof=1)
    ym_std = ym.std(ddof=1)

    xm_max_year = np.expm1(244 * (xm_max_mean - 0.5 * xm_max_std ** 2))
    xm_max_sp = xm_max_year / xm_max_std / 244 ** 0.5
    xm_min_year = np.expm1(244 * (xm_min_mean - 0.5 * xm_min_std ** 2))
    xm_min_sp = xm_min_year / xm_min_std / 244 ** 0.5
    ym_year = np.expm1(244 * (ym_mean - 0.5 * ym_std ** 2))
    ym_sp = ym_year / ym_std / 244 ** 0.5

    xm_max_mdd = np.cumprod(1 + ym[xm_max])
    xm_max_mdd = (1 - xm_max_mdd / np.maximum.accumulate(xm_max_mdd)).max() if xm_max_mdd.shape[0] else np.nan
    xm_max_cm = xm_max_year / xm_max_mdd

    xm_min_mdd = np.cumprod(1 + ym[~ xm_min])
    xm_min_mdd = (1 - xm_min_mdd / np.maximum.accumulate(xm_min_mdd)).max() if xm_min_mdd.shape[0] else np.nan
    xm_min_cm = xm_min_year / xm_min_mdd

    ym_mdd = np.cumprod(1 + ym)
    ym_mdd = (1 - ym_mdd / np.maximum.accumulate(ym_mdd)).max()
    ym_cm = ym_year / ym_mdd

    # 3 val test
    d_max = np.where(x_max, y - 0.002, 0).mean(axis=1)
    d_min = np.where(x_min, y + 0.002, 0).mean(axis=1)
    d_max_pct = x_max.mean(axis=1)
    d_min_pct = x_min.mean(axis=1)
    d_max_val = np.cumprod(1 + d_max)
    d_min_val = np.cumprod(1 + d_min)
    d_max_year = d_max_val[-1] ** (244 / d_max_val.shape[0]) - 1
    d_min_year = d_min_val[-1] ** (244 / d_min_val.shape[0]) - 1
    d_max_std = d_max.std(ddof=1)
    d_min_std = d_min.std(ddof=1)
    d_max_sp = d_max_year / d_max_std / 244 ** 0.5
    d_min_sp = d_min_year / d_min_std / 244 ** 0.5
    d_max_mdd = (1 - d_max_val / np.maximum.accumulate(d_max_val)).max() if d_max_val.shape[0] else np.nan
    d_min_mdd = (d_min_val / np.minimum.accumulate(d_min_val)).max() if d_min_val.shape[0] else np.nan
    d_max_cm = d_max_year / d_max_mdd
    d_min_cm = d_min_year / d_min_mdd

    bench = benchmark.loc[get_pre_trade_date(sub_list[0]):sub_list[-1]] / benchmark.loc[get_pre_trade_date(sub_list[0])]
    bench_year = bench.iloc[-1] ** (244 / bench.shape[0]) - 1
    bench_std = bench.pct_change().std(ddof=1)
    bench_sp = bench_year / bench_std / 244 ** 0.5
    bench_mdd = (1 - bench / np.maximum.accumulate(bench)).max()
    bench_cm = bench_year / bench_mdd

    series = pd.DataFrame({'多头仓位': d_max_pct, '空头仓位': d_min_pct,
                           '多头净值': d_max_val, '空头净值': d_min_val}, index=sub_list)
    series = pd.concat([series, bench.iloc[1:]], axis=1)

    # 4 base corr
    common_dates = [x for x in sub_list if (x >= 20170104) & (x <= 20210528)]
    if not common_dates:
        max_corr = np.nan
        min_corr = np.nan
    else:
        max_r = real_time_max.loc[common_dates[0]: common_dates[-1]].values
        min_r = real_time_min.loc[common_dates[0]: common_dates[-1]].values
        common_index = [sub_list.index(x) for x in common_dates]
        max_t = x_max[common_index]
        min_t = x_min[common_index]
        max_corr = 1 - (max_r & max_t).sum() / max_t.sum()
        min_corr = 1 - (min_r & min_t).sum() / min_t.sum()

    res = [max_corr, min_corr,
        x_max_pct, x_min_pct, x_max_pct_d, x_min_pct_d,
        x_max_mean, x_min_mean, y_mean, x_max_pos, x_min_pos, y_max_pos, y_min_pos,
        x_max_pnl, x_min_pnl, y_max_pnl, y_min_pnl,
        xm_max_pct, xm_min_pct, xm_max_mean, xm_min_mean, ym_mean,
        xm_max_pos, xm_min_pos, ym_pos,
        xm_max_year, xm_min_year, ym_year, xm_max_sp, xm_min_sp, ym_sp,
        xm_max_mdd, xm_min_mdd, ym_mdd, xm_max_cm, xm_min_cm, ym_cm,
        d_max_year, d_min_year, d_max_sp, d_min_sp,
        d_max_mdd, d_min_mdd, d_max_cm, d_min_cm,
    ]
    res = res + bench_year.tolist() + bench_sp.tolist() + bench_mdd.tolist() + bench_cm.tolist()
    return res, series


def test_factor_np(factor, future=wf1d1000, freq='Y', signal_months=12,
                   pct_max=0.1, pct_min=0.1, move_d=40,
                   ins_end=20191231, all_start=20150105, all_end=20211231):
    test_months = calc_test_months(freq)
    start_dates = [calc_start_date(x, signal_months) for x in test_months]
    end_dates = [calc_end_date(x) for x in test_months]
    ins_end = get_recent_trade_date(ins_end)
    oos_start = get_pre_trade_date(ins_end, -1)
    date_signal = [x // 100 for x in test_months]
    date_signal = date_signal if len(set(date_signal)) == len(test_months) else test_months
    date_signal = ['ins', 'oos'] + date_signal
    start_dates = [all_start, oos_start] + start_dates
    end_dates = [ins_end, all_end] + end_dates
    item_list = [
        '因子缺失率', '因子方向', 'IC', '多头IC', '空头IC', '多头策略相关性', '空头策略相关性',
        '多头占比', '空头占比', '多头日占比', '空头日占比',
        '多头收益', '空头收益', '基准收益', '多头胜率', '空头胜率', '基准多头胜率', '基准空头胜率',
        '多头盈亏比', '空头盈亏比', '基准多头盈亏比', '基准空头盈亏比',
        '回撤期多头占比', '回撤期空头占比', '回撤期多头收益', '回撤期空头收益', '回撤期基准收益',
        '回撤期多头胜率', '回撤期空头胜率', '回撤期基准胜率',
        '回撤期多头年化', '回撤期空头年化', '回撤期基准年化', '回撤期多头夏普', '回撤期空头夏普', '回撤期基准夏普',
        '回撤期多头回撤', '回撤期空头回撤', '回撤期基准回撤', '回撤期多头卡玛', '回撤期空头卡玛', '回撤期基准卡玛',
        '净值多头年化', '净值空头年化', '净值多头夏普', '净值空头夏普',
        '净值多头回撤', '净值空头回撤', '净值多头卡玛', '净值空头卡玛',
        '全A等权年化', '万德全A年化', '沪深300年化', '中证500年化', '中证1000年化', '创业板综年化',
        '全A等权夏普', '万德全A夏普', '沪深300夏普', '中证500夏普', '中证1000夏普', '创业板综夏普',
        '全A等权回撤', '万德全A回撤', '沪深300回撤', '中证500回撤', '中证1000回撤', '创业板综回撤',
        '全A等权卡玛', '万德全A卡玛', '沪深300卡玛', '中证500卡玛', '中证1000卡玛', '创业板综卡玛',
    ]
    res = {}
    val = {}
    for j in range(len(date_signal)):
        bar = date_signal[j]
        start_date = start_dates[j]
        end_date = end_dates[j]
        start_idx = date_list.index(start_date)
        end_idx = date_list.index(end_date)
        sub_list = get_date_range(start_date, end_date)
        res[bar], val[bar] = test_factor_1p(factor, future, start_idx, end_idx, sub_list, pct_max, pct_min, move_d)
    res = pd.DataFrame(res, index=item_list, columns=date_signal)
    val_ins = val['ins']
    val_oos = val['oos']
    del val
    return res, val_ins, val_oos


def test_signal_np(factor, future=wf1d1000, freq='Y', signal_months=12,
                   ins_end=20191231, all_start=20150105, all_end=20211231):
    test_months = calc_test_months(freq)
    start_dates = [calc_start_date(x, signal_months) for x in test_months]
    end_dates = [calc_end_date(x) for x in test_months]
    ins_end = get_recent_trade_date(ins_end)
    oos_start = get_pre_trade_date(ins_end, -1)
    date_signal = [x // 100 for x in test_months]
    date_signal = date_signal if len(set(date_signal)) == len(test_months) else test_months
    date_signal = ['ins', 'oos'] + date_signal
    start_dates = [all_start, oos_start] + start_dates
    end_dates = [ins_end, all_end] + end_dates
    item_list = ['多头策略相关性', '空头策略相关性',
        '多头占比', '空头占比', '多头日占比', '空头日占比',
        '多头收益', '空头收益', '基准收益', '多头胜率', '空头胜率', '基准多头胜率', '基准空头胜率',
        '多头盈亏比', '空头盈亏比', '基准多头盈亏比', '基准空头盈亏比',
        '回撤期多头占比', '回撤期空头占比', '回撤期多头收益', '回撤期空头收益', '回撤期基准收益',
        '回撤期多头胜率', '回撤期空头胜率', '回撤期基准胜率',
        '回撤期多头年化', '回撤期空头年化', '回撤期基准年化', '回撤期多头夏普', '回撤期空头夏普', '回撤期基准夏普',
        '回撤期多头回撤', '回撤期空头回撤', '回撤期基准回撤', '回撤期多头卡玛', '回撤期空头卡玛', '回撤期基准卡玛',
        '净值多头年化', '净值空头年化', '净值多头夏普', '净值空头夏普',
        '净值多头回撤', '净值空头回撤', '净值多头卡玛', '净值空头卡玛',
        '全A等权年化', '万德全A年化', '沪深300年化', '中证500年化', '中证1000年化', '创业板综年化',
        '全A等权夏普', '万德全A夏普', '沪深300夏普', '中证500夏普', '中证1000夏普', '创业板综夏普',
        '全A等权回撤', '万德全A回撤', '沪深300回撤', '中证500回撤', '中证1000回撤', '创业板综回撤',
        '全A等权卡玛', '万德全A卡玛', '沪深300卡玛', '中证500卡玛', '中证1000卡玛', '创业板综卡玛',
    ]
    res = {}
    val = {}
    for j in range(len(date_signal)):
        bar = date_signal[j]
        start_date = start_dates[j]
        end_date = end_dates[j]
        start_idx = date_list.index(start_date)
        end_idx = date_list.index(end_date)
        sub_list = get_date_range(start_date, end_date)
        res[bar], val[bar] = test_signal_1p(factor, future, start_idx, end_idx, sub_list)
    res = pd.DataFrame(res, index=item_list, columns=date_signal)
    val_ins = val['ins']
    val_oos = val['oos']
    del val
    return res, val_ins, val_oos

if __name__ == '__main__':
    import os
    from dataApi import aimr
    from HFfactor.MinFactorSuper.Utility.Parallel import play_aimr
    factor_path = '/data/group/800442/800319/Timing/FixFactor/FixFactor/CrossFactor/'  # 64585
    save_path = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewCrossFactorTest/'  # 64584
    factor_list = sorted([x[:-4] for x in os.listdir(factor_path) if x.endswith('.npy')])

    def _func(name):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        factor = np.load(f'{factor_path}/{name}.npy')
        res, _, _ = test_factor_np(factor, wf1d1000, 'M', 36)
        pd.to_pickle(res, f'{save_path}/{name}.pkl')

    idd, parts = eval(aimr.getParam())
    play_aimr(idd, parts, _func, factor_list)
