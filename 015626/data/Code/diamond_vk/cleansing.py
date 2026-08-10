from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.common as ut
import scipy.stats as sps
import pandas as pd
import numpy as np
import itertools
import numbers
from collections import deque
import bottleneck as bk
from statsmodels.tsa.stattools import adfuller
from multifactor.strategy.fitter import fill_infinite
import warnings
try:
    from pykalman import KalmanFilter
except ImportError:
    KalmanFilter = None


def box_skew_algo(x, discard=False):
    if isinstance(x, np.ndarray):
        assert len(x.shape) == 1
    else:
        assert isinstance(x, pd.Series)
    _x = x.copy()
    y = ut.np_valid(x, fillna=True)
    x = ut.np_valid(y)
    if len(np.unique(x)) < 10:
        return y
    x = np.sort(x)
    md = np.median(x)
    q3 = np.percentile(x,75)
    q1 = np.percentile(x,25)
    iqr = q3 - q1
    rx = np.flip(x, axis=0)
    x, rx = zip(*[(i, j) for i, j in zip(x, rx) if i!=j])
    x = np.split(np.array(x), 2)[1]
    rx = np.split(np.array(rx), 2)[1]
    if len(x) < 5:
        return y
    mc = np.median((x + rx - 2.0 * md) / (x - rx))
    a, b= (3.5, 4.0) if mc >= 0 else (4.0, 3.5)
    L = q1 - 1.5 * np.exp(-a * mc) * iqr
    U = q3 + 1.5 * np.exp( b * mc) * iqr
    if discard:
        y[np.array([item < L if not np.isnan(item) else False for item in y])] = np.nan
        y[np.array([item > U if not np.isnan(item) else False for item in y])] = np.nan
    else:
        y[np.array([item < L if not np.isnan(item) else False for item in y])] = L
        y[np.array([item > U if not np.isnan(item) else False for item in y])] = U
    if isinstance(_x, pd.Series):
        y = pd.Series(y, index=_x.index)
        y.index.name = _x.index.name
        y.name = _x.name
    return y


def outlier_median_algo(x, distance=5, percentage=3, discard=False):
    # Remove or reset outlier according to median value
    # Max percentage to process: min(percentage, qualified / total)
    if isinstance(x, np.ndarray):
        assert len(x.shape) == 1
    else:
        assert isinstance(x, pd.Series)
    _x = x.copy()
    y = ut.np_valid(x, fillna=True)
    x = ut.np_valid(y)
    u_num = len(np.unique(x))
    if u_num < 10:
        return y
    md = np.median(x)
    md_distances = x - md
    if ((md_distances >= 0).sum() / x.size >= 0.95 or (md_distances <= 0).sum() / x.size >= 0.95) and u_num / x.size <= 0.5:
        return y
    # Differentiate left and right distribution
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')  # caution: median zero condition
        if np.all(md_distances >= 0) or np.all(md_distances <= 0):
            warnings.warn('highly skewed or constant dataset encountered')
        while True:
            u_md = np.median(md_distances[md_distances>0])
            U = distance * u_md + md
            l_md = np.median(md_distances[md_distances<0])
            L = distance * l_md + md
            # Percentage verification
            if (x[x>U].size + x[x<L].size) / x.size <= percentage / 100:
                break
            else:
                distance = 1.1 * distance
    if discard:
        y[np.array([item < L if not np.isnan(item) else False for item in y])] = np.nan
        y[np.array([item > U if not np.isnan(item) else False for item in y])] = np.nan
    else:
        y[np.array([item < L if not np.isnan(item) else False for item in y])] = L
        y[np.array([item > U if not np.isnan(item) else False for item in y])] = U
    if isinstance(_x, pd.Series):
        y = pd.Series(y, index=_x.index)
        y.index.name = _x.index.name
        y.name = _x.name
    return y


def uniform_norm_transform(raw, std=1, cutoff=5, ranked=False):
    # Transform input data into norm distribution with specified std
    # The transformed data shall with limits [-std*cutoff, std*cutoff]
    # The std of the transformed data shall be approximately equal to given std
    # on condition the cutoff is not too small
    # The input and output data shall have the same length
    assert np.any([isinstance(raw, _type) for _type in [pd.Series, np.ndarray, list]])
    _raw = pd.Series(raw)
    if _raw.diff().abs().sum() == 0:  # constant data
        warnings.warn('constant input for uniform norm transform')
        return raw
    if not ranked:
        _raw = _raw.rank()
    scale = (sps.norm.cdf(cutoff) - sps.norm.cdf(-cutoff)) / (_raw.max() - _raw.min())
    with warnings.catch_warnings():
        # np.nan warning filter
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        transformed = sps.norm.ppf((_raw + (sps.norm.cdf(-cutoff) / scale - _raw.min())) * scale, scale=std)
    if isinstance(raw, pd.Series):
        transformed = pd.Series(transformed, index=raw.index)
        transformed.index.name = raw.index.name
        transformed.name = raw.name
    elif isinstance(raw, list):
        transformed = list(transformed)
    return transformed


def shrinkage_transform(raw, layers=30, method='median'):
    # cut samples to number of layers and set segment values to layer median
    assert np.any([isinstance(raw, _type) for _type in [pd.Series, np.ndarray, list]])
    _raw = pd.Series(raw)
    labels = ut.layer_chopper(_raw, layers=layers, rank=True)
    transformed = _raw.groupby(labels).transform(method)
    if isinstance(raw, np.ndarray):
        transformed = transformed.values
    elif isinstance(raw, list):
        transformed = list(transformed)
    return transformed


def rank(raw):
    assert np.any([isinstance(raw, _type) for _type in [pd.Series, np.ndarray, list]])
    ranked = pd.Series(raw).rank()
    if isinstance(raw, np.ndarray):
        ranked = np.array(ranked)
    elif isinstance(raw, list):
        ranked = list(ranked)
    return ranked


def bounded_transformer(x, upper, lower):
    # linear transform x distribution according to upper and lower bound inputs
    assert upper > lower
    x_upper = np.nanmax(x)
    x_lower = np.nanmin(x)
    scaler = (upper - lower) / (x_upper - x_lower)
    return (x - x_lower) * scaler + lower


def outlier_normalizer(pd_raw, axis=1, func=box_skew_algo, **kwargs):
    pd_raw[~np.isfinite(pd_raw)] = np.nan
    if type(pd_raw) == pd.DataFrame:
        return pd_raw.apply(func, axis=axis, result_type='broadcast', **kwargs)
    else:
        raise AssertionError


def std_normalizer(pd_raw, axis=1):
    x, y = (1, 0) if axis == 1 else (0, 1)
    if isinstance(pd_raw, pd.DataFrame):
        return pd_raw.subtract(pd_raw.mean(axis=x), axis=y).divide(pd_raw.std(axis=x, ddof=0), axis=y)
    elif isinstance(pd_raw, np.ma.MaskedArray):
        pd_raw = pd.DataFrame(pd_raw)
        return np.ma.masked_invalid(pd_raw.subtract(pd_raw.mean(axis=x), axis=y).divide(pd_raw.std(axis=x, ddof=0), axis=y))
    elif isinstance(pd_raw, np.ndarray):
        pd_raw = pd.DataFrame(pd_raw)
        return np.array(pd_raw.subtract(pd_raw.mean(axis=x), axis=y).divide(pd_raw.std(axis=x, ddof=0), axis=y))
    else:
        raise AssertionError


def bootstrap(pd_raw, axis=1, outlier_process='box', **kwargs):
    if outlier_process == 'box':
        return std_normalizer(outlier_normalizer(pd_raw, axis=axis, func=box_skew_algo, **kwargs), axis=axis)
    elif outlier_process == 'median':
        return std_normalizer(outlier_normalizer(pd_raw, axis=axis, func=outlier_median_algo, **kwargs), axis=axis)
    elif outlier_process == 'rank':
        return std_normalizer(outlier_normalizer(pd_raw, axis=axis, func=rank, **kwargs), axis=axis)
    elif outlier_process == 'norm':
        return std_normalizer(outlier_normalizer(pd_raw, axis=axis, func=uniform_norm_transform, **kwargs), axis=axis)
    elif outlier_process == 'shrinkage':
        return std_normalizer(outlier_normalizer(pd_raw, axis=axis, func=shrinkage_transform, **kwargs), axis=axis)
    elif outlier_process == 'median_solo':
        return outlier_normalizer(pd_raw, axis=axis, func=outlier_median_algo, **kwargs)
    else:
        return std_normalizer(axis=axis)


def multi_bootstrap(pd_raw, axis=1, **kwargs):
    # Unstack a DataFrame or Series and bootstrap along given axis
    # e.g. axis 1 for cross section and axis 0 for time
    parsed = ut.pd_unstack(pd_raw)
    if isinstance(parsed, dict):
        for key in parsed:
            parsed[key] = bootstrap(parsed[key], axis=axis, **kwargs)
        return ut.pd_stack(parsed)
    else:
        parsed = bootstrap(parsed, axis=axis, **kwargs)
        if isinstance(pd_raw, pd.Series):
            return ut.pd_stack(parsed, pd_raw.name)
        else:
            return pd.DataFrame(ut.pd_stack(parsed, pd_raw.columns[0]))


def standard_process(pd_raw, boxskew=True, stock_filter=None, stock_industry=None, winsor=True):
    pd_raw = pd_raw.copy()
    pd_raw[~np.isfinite(pd_raw)] = np.nan
    if boxskew:
        pd_raw = outlier_normalizer(pd_raw, axis=1, func=box_skew_algo, discard=False)
    else:
        pd_raw = outlier_normalizer(pd_raw, axis=1, func=outlier_median_algo, discard=False)
    if stock_filter is not None and stock_industry is not None:
        pd_raw = factor_fillna_industry(pd_raw, stock_filter, stock_industry, inplace=False)
    if winsor:
        pd_raw = norm_winsor(pd_raw)
    else:
        pd_raw = bootstrap(pd_raw, axis=1, outlier_process='median', discard=False)
    return pd_raw


def norm_winsor(factor_pd, bound=5, winsor=False):
    # obviously input date should not be altered without notice
    factor_pd = median_filter(factor_pd, mad=bound, winsor=winsor, inplace=False)
    std_ts = factor_pd.std(axis=1, ddof=0)
    std_ts.loc[std_ts == 0] = 1
    factor_pd = factor_pd.subtract(factor_pd.mean(axis=1), axis=0).divide(std_ts, axis=0)
    return factor_pd


def median_filter(factor_pd, mad=5, winsor=False, inplace=False):
    if not inplace:
        factor_pd = factor_pd.copy()
    dm = factor_pd.median(axis=1)
    # caution of symmetric uppper & lower bounds
    dist_pd = factor_pd.subtract(dm, axis=0).abs()
    dist_dm = dist_pd[dist_pd > 0].median(axis=1)
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
    if not inplace:
        return factor_pd


def factor_fillna_industry(pd_raw, stock_filter, stock_industry, inplace=False):
    # all inputs are in shape of DataFrame: dates, stocks
    # np.nans in pd_raw which are "True" in stock_filter are filled by industry median
    assert pd_raw.shape == stock_filter.shape == stock_industry.shape
    if not inplace:
        pd_raw = pd_raw.copy()
    fill_indicator = np.isnan(pd_raw) & (stock_filter == True)
    industry_universe = [i + 1 for i in range(int(stock_industry.max().max()))]
    industry_median = pd.DataFrame(index=pd_raw.index, columns=industry_universe, dtype=np.float64)
    for row in stock_industry.itertuples():
        date = row[0]
        industry_list = list(row[1:])
        industry_median.loc[date] = pd_raw.loc[date].groupby(industry_list).median()
    stock_number = pd_raw.shape[1]
    for ind in industry_universe:
        pd_raw[(stock_industry == ind) & fill_indicator] = np.tile(industry_median[ind], (stock_number, 1)).T
    if not inplace:
        return pd_raw


class IndustryFiller:
    def __init__(self, start_date, end_date, universe='alpha_universe', industry_name='CITIC_I'):
        self.start_date = IO.str_date_parser(start_date)
        self.end_date = IO.str_date_parser(end_date)
        self._universe_pd = IO.read_data([self.start_date, self.end_date], columns=universe,
                                          ftype=FType.UNIV, dsource=DSource.OPTM)[universe].unstack().fillna(False)
        self._industry_pd = IO.read_data([self.start_date, self.end_date], ftype=FType.INDUSTRY,
                                          dsource=DSource.WIND, columns=industry_name)[industry_name].unstack()
        self._universe_pd, self._industry_pd = self._universe_pd.align(self._industry_pd, join='inner')

    def fillna(self, pd_raw):
        _pd_raw = ut.pd_matrix_reshaper(pd_raw)
        _pd_raw = _pd_raw.reindex(index=self._universe_pd.index, columns=self._universe_pd.columns)
        res = factor_fillna_industry(_pd_raw, self._universe_pd, self._industry_pd, inplace=False)
        if isinstance(pd_raw, pd.Series):
            res = res.stack()
            res.name = pd_raw.name
        else:
            if len(pd_raw.columns) == 1:
                res = pd.DataFrame(res.stack())
                res.columns = pd_raw.columns
        return res


def scale_estimator(*args, sample_number=20, axis=1, agger=np.ma.mean, **kwargs):
    # estimate [a, b, c, ...] according to axis features
    assert axis in [0, 1]
    if len(args) < 1:
        raise AssertionError
    samples = [item if isinstance(item, np.ma.MaskedArray) else np.ma.masked_invalid(item) for item in args]
    if axis == 1:
        sub_samples = [item[::int(item.shape[0]/sample_number), :] for item in samples]
    else:
        sub_samples = [item[:, ::int(item.shape[1]/sample_number)] for item in samples]
    condensed = [agger(np.abs(item), axis=axis, **kwargs) for item in sub_samples]
    if 0 in [agger(item, **kwargs) for item in condensed]:  # zero for all matrix elements
        print(*args)
        raise ValueError
    if len(args) == 1:
        return agger(condensed[0], **kwargs)
    else:
        stats_list = list()
        for a, b in itertools.combinations(condensed, 2):
            stats = agger(a / b, **kwargs)
            if stats >= 1:
                stats_list.append(stats)
            else:
                stats_list.append(1 / stats)
        return max(stats_list)


def is_stationary_by_adf(timeseries, p_threshold=0.01):
    #Dickey-Fuller test null hypothesis: time series contains Unit Root (trend exists)
    if isinstance(timeseries, list) or isinstance(timeseries, tuple):
        timeseries = np.array(timeseries)
    if isinstance(timeseries, np.ndarray):
        assert len(timeseries.shape) == 1
        timeseries = timeseries[np.isfinite(timeseries)]
    elif isinstance(timeseries, pd.Series):
        timeseries = timeseries.dropna()
    else:
        raise NotImplementedError
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            df_result = adfuller(timeseries, autolag='AIC')
    except:
        return False
    # [0:4] 'Test Statistic', 'p-value', 'Lags Used', 'Number of Observations Used'
    tstats, p_value = df_result[0:2]
    critical_value = min(df_result[4].values())
    if p_value <= p_threshold and tstats <= critical_value:
        # reject null hypothesis, no trend detected
        return True
    else:
        return False


def is_stationary_sampled_by_adf(array, sample_num=10, downsample=5, fill_rate=0.5, confidence=0.8):
    if isinstance(array, pd.DataFrame):
        array = array.values
    elif isinstance(array, np.ndarray):
        assert len(array.shape) == 2
    else:
        raise AssertionError
    if array.shape[1] < sample_num:
        sample_num = array.shape[1]
    if downsample is not None:
        array = array[::downsample, :]
    _fill_rate = np.isfinite(array).sum(axis=0) / array.shape[0]
    valid_cols = np.arange(array.shape[1])[_fill_rate >= fill_rate]
    if len(valid_cols) < sample_num:
        return False
    sample_cols = np.random.choice(valid_cols, size=sample_num, replace=False)
    adf_results = [is_stationary_by_adf(array[:, i]) for i in sample_cols]
    return np.sum(adf_results) / len(adf_results) >= confidence


def ts_ma_winsorize(x, ma_window, dev_window, outlier_distance=5):
    # look back periods equal ma + dev windows
    if isinstance(x, np.ndarray):
        assert len(x.shape) == 1
        _x = x.copy()
    elif isinstance(x, pd.Series):
        _x = x.values.copy()
    else:
        raise NotImplementedError
    _x[~np.isfinite(_x)] = np.nan
    ma = None
    dev = None
    ma_queue = deque(maxlen=ma_window)
    dev_queue = deque(maxlen=dev_window)
    for i in np.nditer(_x, op_flags=['readwrite']):
        if np.isnan(i):
            continue
        if ma is not None:
            _dev = abs(i - ma)
            if dev is not None and dev !=0 and _dev / dev >= outlier_distance:
                if i > ma:
                    i[...] = ma + outlier_distance * dev
                else:
                    i[...] = ma - outlier_distance * dev
                _dev = abs(i - ma)
            dev_queue.append(_dev)
        ma_queue.append(i)
        # update moving average and deviation
        if len(ma_queue) == ma_window:
            ma = np.mean(ma_queue)
        if len(dev_queue) == dev_window:
            dev = np.mean(dev_queue)
    if isinstance(x, pd.Series):
        _x = pd.Series(_x, index=x.index)
        _x.index.name = x.index.name
        _x.name = x.name
    return _x


def ts_median_winsorize(pd_raw, ma_window, dev_window, outlier_distance=5):
    if isinstance(pd_raw, pd.Series) or isinstance(pd_raw, np.ndarray):
        np_data = pd.DataFrame(pd_raw).values
    elif isinstance(pd_raw, pd.DataFrame):
        np_data = pd_raw.values.copy()
    else:
        raise AssertionError
    np_data[~np.isfinite(np_data)] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        np_median = bk.move_median(np_data, window=ma_window, min_count=int(ma_window / 2), axis=0)
        np_dev = np_data - np_median
        np_dev_median = bk.move_median(np.abs(np_dev), window=dev_window, min_count=int(dev_window / 2), axis=0)
        np_env_top = np_median + outlier_distance * np_dev_median
        np_env_bot = np_median - outlier_distance * np_dev_median
        res = np_data
        res = np.where(res < np_env_top, res, np_env_top)
        res = np.where(res > np_env_bot, res, np_env_bot)
        # pad result nan with original
        res = np.where(np.isnan(res), np_data, res)
        # drop original nan within result
        res = np.where(np.isnan(np_data), np_data, res)
    if isinstance(pd_raw, pd.Series):
        res = pd.Series(res.ravel(), index=pd_raw.index)
        res.index.name = pd_raw.index.name
        res.name = pd_raw.name
    elif isinstance(pd_raw, np.ndarray):
        res = np.reshape(res, pd_raw.shape)
    else:
        res = pd.DataFrame(res, columns=pd_raw.columns, index=pd_raw.index)
    return res


def tiktok_helper(input_data, chunk_bar_num, phaser_bar_num, boundary=5):
    if isinstance(input_data, pd.Series):
        np_data = input_data.values
    elif isinstance(input_data, np.ndarray):
        np_data = input_data
    else:
        raise NotImplementedError
    assert len(np_data.shape) == 1 and len(np_data) % chunk_bar_num == 0
    phase_out = np.append(np.array([1] * (chunk_bar_num - phaser_bar_num)),
                          ut.phaser(phaser_bar_num, 1, 0, method='sigmoid', cfg= {'boundary': boundary}))
    # split given data into individual intraday chunks
    chunks = ut.into_subchunks(np_data, chunk_bar_num, chunk_bar_num)
    # round beginning position to zero
    chunks = (chunks.T - fill_infinite(chunks[:, 0], 0)).T
    # round ending position to zero
    chunks = chunks * phase_out
    if isinstance(input_data, pd.Series):
        res = pd.Series(chunks.ravel(), index=input_data.index)
        res.index.name = input_data.index.name
        res.name = input_data.name
    else:
        res = chunks.flatten()
    return res


def ts_rolling_normalize(pd_raw, window, min_periods, method='RANK',
                         outlier_distance=None, ma_window=None, dev_window=None,
                         outlier_handler='MEDIAN', **kwargs):
    if isinstance(pd_raw, pd.Series):
        np_data = pd.DataFrame(pd_raw).values
    elif isinstance(pd_raw, pd.DataFrame):
        np_data = pd_raw.values
    elif isinstance(pd_raw, np.ndarray):
        np_data = pd_raw
    else:
        raise AssertionError
    np_data = np_data.astype('double')
    if outlier_distance is not None:
        assert ma_window is not None and dev_window is not None
        if outlier_handler == 'MEDIAN':
            np_data = ts_median_winsorize(np_data, ma_window=ma_window,
                                          dev_window=dev_window, outlier_distance=outlier_distance)
        elif outlier_handler == 'MEAN':
            np_data = np.apply_along_axis(ts_ma_winsorize, 0, np_data, ma_window=ma_window,
                                          dev_window=dev_window, outlier_distance=outlier_distance)
        else:
            raise NotImplementedError
    else:
        np_data[~np.isfinite(np_data)] = np.nan
    if method == 'ZSCORE':
        roll_std = bk.move_std(np_data, window, min_count=min_periods, axis=0)
        roll_std[roll_std == 0] = np.nan
        res = (np_data - bk.move_mean(np_data, window, min_count=min_periods, axis=0)) / roll_std
    elif method == 'RANK':
        res = bk.move_rank(np_data, window, min_count=min_periods, axis=0)
    elif method == 'MAXMIN':
        roll_max = bk.move_max(np_data, window, min_count=min_periods, axis=0)
        roll_min = bk.move_min(np_data, window, min_count=min_periods, axis=0)
        roll_range = roll_max - roll_min
        roll_range[roll_range == 0] = np.nan
        res = (np_data - roll_min) / roll_range
    elif method == 'NORM':
        res = pd.DataFrame(np_data).rolling(window, min_periods=min_periods).apply(\
                 lambda x: uniform_norm_transform(x, ranked=False, **kwargs)[-1], raw=True).values
    elif method == 'TIKTOK':
        aligned_data = np.apply_along_axis(tiktok_helper, 0, np_data, **kwargs)
        roll_max = bk.move_max(aligned_data, window, min_count=min_periods, axis=0)
        roll_min = bk.move_min(aligned_data, window, min_count=min_periods, axis=0)
        with warnings.catch_warnings():
            # np.nan warning filter
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            aligned_data = np.where(aligned_data > 0, aligned_data / roll_max, aligned_data)
            aligned_data = np.where(aligned_data < 0, - aligned_data / roll_min, aligned_data)
        res = (aligned_data + 1) / 2
    else:
        raise NotImplementedError
    if isinstance(pd_raw, pd.Series):
        res = pd.Series(res.ravel(), index=pd_raw.index)
        res.index.name = pd_raw.index.name
        res.name = pd_raw.name
    elif isinstance(pd_raw, np.ndarray):
        res = np.reshape(res, pd_raw.shape)
    else:
        res = pd.DataFrame(res, columns=pd_raw.columns, index=pd_raw.index)
    return res


def signal_stats(sig):
    stats = dict()
    assert isinstance(sig, pd.Series)
    sig = sig.fillna(0)
    assert np.all([item in [-1, 0, 1] for item in sig.unique()])
    flag =  sig * sig.shift(-1)
    sig.name = 'sig'
    flag.name=  'flag'
    data = pd.DataFrame(sig).merge(pd.DataFrame(flag), how='left', left_index=True, right_index=True)
    stats['invalid_deal_num'] = (flag == -1).sum()
    stats['long_deal_num'] = ((data['sig'] == 1) & (data['flag'] != 1)).sum()
    stats['short_deal_num'] = ((data['sig'] == -1) & (data['flag'] != 1)).sum()
    stats['long_num'] = (sig == 1).sum()
    stats['short_num'] = (sig == -1).sum()
    stats['avg_long_bars'] = stats['long_num'] / stats['long_deal_num']
    stats['avg_short_bars'] = stats['short_num'] / stats['short_deal_num']
    return stats


def signal_filter(sig, observation_window):
    '''
    the main purpose of signal filter is to transform signals:
    * no contradictory new open gesture within observation window
    * minimum holding period for new open should be gte observation window
    '''
    assert isinstance(sig, pd.Series)
    sig = sig.fillna(0)
    assert np.all([item in [-1, 0, 1] for item in sig.unique()])
    q = deque(maxlen=observation_window)  # previous original values
    flag = 0  # previous operation
    counter = 0  # counter for current holding period
    for i in np.nditer(sig.values, op_flags=['readwrite']):
        _i = int(i)  # copy new signal
        if len(q) == 0:
            flag = i
            if i != 0:
                counter = 1
        else:
            _flag = i * flag
            if _flag == 0:
                if flag == 0 and i == 0:
                    # nothing to do
                    pass
                elif flag == 0:
                    # no operation before, determine whether to open
                    if -i not in q:
                        # reversion should not be within given holding period
                        flag = i
                    else:
                        i[...] = 0
                else:
                    # determine whether to close, i == 0
                    if counter >= observation_window:
                        flag = 0
                        counter = 0
                    else:
                        # hold position until minimum holding period
                        i[...] = flag
            else:
                if _flag == -1:
                    # conflict of current operation and new signal
                    i[...] = 0
                    flag = 0
            # update counter
            if i * flag == 1:
                counter += 1
        q.append(_i)
    return sig


def signal_resizer(signals, signal_lims=(0, 1)):
    assert isinstance(signals, pd.Series)
    assert isinstance(signal_lims, tuple) and len(signal_lims) == 2
    # resize signal to [-1, 1]
    signals.index.name = 'dt'
    signals.name = 'signals'
    signal_mean = np.mean(signal_lims)
    signal_amp = (max(signal_lims) - min(signal_lims)) / 2
    signals = (signals - signal_mean) / signal_amp
    signals = signals.fillna(0)
    return signals


def linear_position_mapper(signal, threshold, saturation=None, init=None, steps=10):
    # simple mapper to convert signal into actual positions
    # given signal [0, 1], return position [0, 1] in linear style
    # use num of steps to size up position from trigger threshold to saturation point
    # long / short positions are deemed symmetric
    if saturation is None:
        saturation = 1
    if init is None:
        init = 1 / steps
    assert 1 >= saturation >= threshold
    assert init <= 1
    signal_lots = np.linspace(threshold, saturation, steps, endpoint=True)
    signal_lots = np.append(signal_lots, np.inf)
    position_lots = np.linspace(init, 1.0, steps, endpoint=True)
    if isinstance(signal, numbers.Number):
        assert 0 <= signal <= 1
        _signal  = [signal]
    elif isinstance(signal, pd.Series):
        assert signal.min() >= 0 and signal.max() <= 1
        _signal = signal
    elif isinstance(signal, np.ndarray):
        assert np.nanmin(signal) >= 0 and np.nanmax(signal) <= 1
        _signal = signal
    else:
        raise NotImplementedError
    res = fill_infinite(pd.cut(_signal, bins=signal_lots, labels=position_lots, right=False, include_lowest=True).astype('float'), 0)
    if isinstance(signal, numbers.Number):
        res = res[0]
    elif isinstance(signal, np.ndarray):
        res = np.array(res)
    return res


def signal_dealer(signals, *args, signal_lims=(0, 1), mode='linear', **kwargs):
    signals = signal_resizer(signals, signal_lims).abs()
    if mode == 'linear':
        return linear_position_mapper(signals, *args, **kwargs)
    else:
        raise NotImplementedError


def signal_reshaper(signals, threshold=0.75, signal_lims=(0, 1), signal_plummet_amplitude=None,
                    signal_plummet_period=None, signal_plummet_threshold=None, delay=None, smooth_period=None, print_stats=True):
    # threshold: (entry, exit) threshold
    # lims: used to transform signal into [-1, 1]
    # plummet: exit in case signal turns backwards
    # delay: delay the exit to prevent fast in & out
    # smooth period: to prevent signal from sign flipping and ensure minimum holding period
    signals = signal_resizer(signals, signal_lims)
    if signal_plummet_amplitude is not None:
        assert signal_plummet_threshold is not None
    # prepare entry and exit thresholds
    if delay is None:
        delay = 0
    else:
        assert 0 <= delay <= 0.5
    if isinstance(threshold, tuple):
        assert len(threshold) == 2 and 0 < threshold[0] < 1 and 0 < threshold[1] < 1
        long_entry_threshold = threshold[0]
        short_entry_threshold = - threshold[1]
    else:
        assert 0 < threshold < 1
        long_entry_threshold = threshold
        short_entry_threshold = - threshold
    long_exit_threshold = long_entry_threshold - delay
    short_exit_threshold = short_entry_threshold + delay
    # loop for entry and exit markers
    status = 0
    previous_status = 0
    dmz_flag = False  # enter dmz to prevent re-enter
    trailing_signal_max= None  # trailing max signal value
    trailing_max_counter = None  # bars from the trailing max signal
    for i in np.nditer(signals.values, op_flags=['readwrite']):
        long_entry_flag = i >= long_entry_threshold
        long_exit_flag = i < long_exit_threshold
        short_entry_flag = i <= short_entry_threshold
        short_exit_flag = i > short_exit_threshold
        plummet_flag = False
        if status != 0:
            if status * i >= trailing_signal_max:
                trailing_signal_max = status * i
                trailing_max_counter = 0
            else:
                trailing_max_counter += 1
                # if signal has decayed shorter than given period or not designated
                if signal_plummet_period is None or trailing_max_counter >= signal_plummet_period:
                    # and the depth is more than the given amplitude
                    if signal_plummet_amplitude is not None and \
                       trailing_signal_max >= signal_plummet_threshold and \
                       trailing_signal_max - status * i >= signal_plummet_amplitude:
                        plummet_flag = True
                        dmz_flag = True
        if status == 0:
            if dmz_flag:
                if previous_status == 1:
                    if long_exit_flag:
                        dmz_flag = False
                elif previous_status == -1:
                    if short_exit_flag:
                        dmz_flag = False
                else:
                    raise AssertionError
            if long_entry_flag and not dmz_flag:
                trailing_signal_max = status * i
                trailing_max_counter = 0
                status = 1
            elif short_entry_flag and not dmz_flag:
                trailing_signal_max = status * i
                trailing_max_counter = 0
                status = -1
        elif status == 1:
            if long_exit_flag or plummet_flag:
                previous_status = status
                status = 0
        elif status == -1:
            if short_exit_flag or plummet_flag:
                previous_status = status
                status = 0
        else:
            raise AssertionError
        i[...] = status
    if smooth_period is not None and smooth_period > 1:
        signals = signal_filter(signals, smooth_period)
    if print_stats:
        print(pd.Series(signal_stats(signals)))
    return signals


def kalman_smoother(x, kalman_cfg={}):
    assert KalmanFilter is not None
    # default params may be suitable for stock prices only
    if isinstance(x, np.ndarray):
        assert len(x.shape) == 1
    else:
        assert isinstance(x, pd.Series)
    _x = x.copy()
    x = pd.Series(np.array(x).ravel())
    finite_mask = np.isfinite(x)
    x.loc[~finite_mask] = np.nan
    valid_x = x.loc[finite_mask]
    kalman_cfg['transition_matrices'] = kalman_cfg.get('transition_matrices', [1])
    kalman_cfg['observation_matrices'] = kalman_cfg.get('observation_matrices', [1])
    kalman_cfg['initial_state_mean'] = kalman_cfg.get('initial_state_mean', valid_x.iloc[0])
    kalman_cfg['initial_state_covariance'] = kalman_cfg.get('initial_state_covariance', 1)
    kalman_cfg['observation_covariance'] = kalman_cfg.get('observation_covariance', 1)
    kalman_cfg['transition_covariance'] = kalman_cfg.get('transition_covariance', 0.1)
    kf = KalmanFilter(**kalman_cfg)
    state_means, _ = kf.filter(valid_x)
    x.loc[finite_mask] = state_means.ravel()
    if isinstance(_x, pd.Series):
        res = pd.Series(x.values, index=_x.index)
        res.index.name = _x.index.name
        res.name = _x.name
    else:
        res = x.values
    return res


def kalman_synthesizer(x, kalman_cfg={}):
    # synthesize columns of x by kalman filter
    assert KalmanFilter is not None
    if isinstance(x, np.ndarray) or isinstance(x, pd.DataFrame):
        assert len(x.shape) == 2 and x.shape[1] > 1
    else:
        raise AssertionError
    _x = x.copy()
    x = pd.DataFrame(np.array(x))
    y = pd.Series(np.nan, index=x.index)
    n = x.shape[1]
    finite_mask = np.isfinite(x).all(axis=1)
    valid_x = x.loc[finite_mask, :]
    kalman_cfg['transition_matrices'] = kalman_cfg.get('transition_matrices', [1])
    kalman_cfg['observation_matrices'] = kalman_cfg.get('observation_matrices', np.ones((n, 1)))
    kalman_cfg['initial_state_mean'] = kalman_cfg.get('initial_state_mean', valid_x.iloc[0, :].mean())
    kalman_cfg['initial_state_covariance'] = kalman_cfg.get('initial_state_covariance', 1)
    kalman_cfg['observation_covariance'] = kalman_cfg.get('observation_covariance', np.diag([1] * n))
    kalman_cfg['transition_covariance'] = kalman_cfg.get('transition_covariance', 0.5)
    kf = KalmanFilter(**kalman_cfg)
    state_means, _ = kf.filter(valid_x)
    y.loc[finite_mask] = state_means.ravel()
    if isinstance(_x, pd.DataFrame):
        res = pd.Series(y.values, index=_x.index)
        res.index.name = _x.index.name
        res.name = None
    else:
        res = y.values
    return res


def chunk_normalizer(x, subchunk_length, every_n, normalizer, **kwargs):
    if isinstance(x, pd.Series):
        x_ = x.values
    elif isinstance(x, np.ndarray):
        assert len(x.shape) == 1
        x_ = x
    else:
        raise NotImplementedError
    sx = ut.into_subchunks(x_, subchunk_length, every_n)
    assert callable(normalizer)
    sx = np.apply_along_axis(normalizer, axis=1, arr=sx, **kwargs)
    nx = sx[:, :every_n].ravel()
    if isinstance(x, pd.Series):
        res = pd.Series(nx, x.index[:len(nx)])
    else:
        res = nx
    return res

