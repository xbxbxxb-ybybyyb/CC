"""Metrics to evaluate the fitness of a program.
The :mod:`gplearn.fitness` module contains some metric with which to evaluate
the computer programs created by the :mod:`gplearn.genetic` module.
"""

# Author: Trevor Stephens <trevorstephens.com>
#
# License: BSD 3 clause

import numbers
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from scipy.stats import linregress
from joblib import wrap_non_picklable_objects
from operators.operators_wsc import rolling_norm
from sklearn.metrics import adjusted_mutual_info_score
from factor_test.SIF_Factor_Test10_modify import SIF_Factor_Test


__all__ = ['_Fitness', 'make_fitness', '_fitness_map']


def signal_reshaper(signals, signal_lims, layers):
    assert isinstance(signals, pd.Series)
    assert isinstance(signal_lims, tuple)
    threshold = max(signal_lims) - 2 * max(signal_lims) / layers
    assert 0 < threshold < 1
    signals = signals.copy()
    signals.index.name = 'dt'
    signals.name = 'signals'
    signals.loc[signals >= threshold] = threshold
    signals.loc[signals <= -threshold] = -threshold
    signals.loc[(signals < threshold) & (signals > - threshold)] = 0
    signals = signals / threshold
    return signals


class _Fitness(object):
    """A metric to measure the fitness of a program.
    This object is able to be called with NumPy vectorized arguments and return
    a resulting floating point score quantifying the quality of the program's
    representation of the true relationship.
    Parameters
    ----------
    function : callable
        A function with signature function(y, y_pred, sample_weight) that
        returns a floating point number. Where `y` is the input target y
        vector, `y_pred` is the predicted values from the genetic program, and
        sample_weight is the sample_weight vector.
    greater_is_better : bool
        Whether a higher value from `function` indicates a better fit. In
        general this would be False for metrics indicating the magnitude of
        the error, and True for metrics indicating the quality of fit.
    """

    def __init__(self, function, greater_is_better):
        self.function = function
        self.greater_is_better = greater_is_better
        self.sign = 1 if greater_is_better else -1

    def __call__(self, *args):
        return self.function(*args)


def make_fitness(function, greater_is_better, wrap=True):
    """Make a fitness measure, a metric scoring the quality of a program's fit.
    This factory function creates a fitness measure object which measures the
    quality of a program's fit and thus its likelihood to undergo genetic
    operations into the next generation. The resulting object is able to be
    called with NumPy vectorized arguments and return a resulting floating
    point score quantifying the quality of the program's representation of the
    true relationship.
    Parameters
    ----------
    function : callable
        A function with signature function(y, y_pred, sample_weight) that
        returns a floating point number. Where `y` is the input target y
        vector, `y_pred` is the predicted values from the genetic program, and
        sample_weight is the sample_weight vector.
    greater_is_better : bool
        Whether a higher value from `function` indicates a better fit. In
        general this would be False for metrics indicating the magnitude of
        the error, and True for metrics indicating the quality of fit.
    wrap : bool, optional (default=True)
        When running in parallel, pickling of custom metrics is not supported
        by Python's default pickler. This option will wrap the function using
        cloudpickle allowing you to pickle your solution, but the evolution may
        run slightly more slowly. If you are running single-threaded in an
        interactive Python session or have no need to save the model, set to
        `False` for faster runs.
    """
    if not isinstance(greater_is_better, bool):
        raise ValueError('greater_is_better must be bool, got %s'
                         % type(greater_is_better))
    if not isinstance(wrap, bool):
        raise ValueError('wrap must be an bool, got %s' % type(wrap))
    if function.__code__.co_argcount != 3:
        raise ValueError('function requires 3 arguments (y, y_pred, w),'
                         ' got %d.' % function.__code__.co_argcount)
    if not isinstance(function(np.array([1, 1]),
                               np.array([2, 2]),
                               np.array([1, 1])), numbers.Number):
        raise ValueError('function must return a numeric.')

    if wrap:
        return _Fitness(function=wrap_non_picklable_objects(function),
                        greater_is_better=greater_is_better)
    return _Fitness(function=function,
                    greater_is_better=greater_is_better)


def _weighted_pearson(y, y_pred, w):
    """Calculate the weighted Pearson correlation coefficient."""
    with np.errstate(divide='ignore', invalid='ignore'):
        y_pred_demean = y_pred - np.average(y_pred, weights=w)
        y_demean = y - np.average(y, weights=w)
        corr = ((np.sum(w * y_pred_demean * y_demean) / np.sum(w)) /
                np.sqrt((np.sum(w * y_pred_demean ** 2) *
                         np.sum(w * y_demean ** 2)) /
                        (np.sum(w) ** 2)))
    if np.isfinite(corr):
        return np.abs(corr)
    return 0.


def _weighted_spearman(y, y_pred, w):
    """Calculate the weighted Spearman correlation coefficient."""
    y_pred_ranked = np.apply_along_axis(rankdata, 0, y_pred)
    y_ranked = np.apply_along_axis(rankdata, 0, y)
    return _weighted_pearson(y_pred_ranked, y_ranked, w)


def _mean_absolute_error(y, y_pred, w):
    """Calculate the mean absolute error."""
    return np.average(np.abs(y_pred - y), weights=w)


def _mean_square_error(y, y_pred, w):
    """Calculate the mean square error."""
    return np.average(((y_pred - y) ** 2), weights=w)


def _root_mean_square_error(y, y_pred, w):
    """Calculate the root mean square error."""
    return np.sqrt(np.average(((y_pred - y) ** 2), weights=w))


def _log_loss(y, y_pred, w):
    """Calculate the log loss."""
    eps = 1e-15
    inv_y_pred = np.clip(1 - y_pred, eps, 1 - eps)
    y_pred = np.clip(y_pred, eps, 1 - eps)
    score = y * np.log(y_pred) + (1 - y) * np.log(inv_y_pred)
    return np.average(-score, weights=w)


def _calc_information_coefficient(y, y_pred, w):
    """Calculate the information coefficient"""
    if y_pred.count() / y.count() < 0.9:
        output = np.nan
    else:
        # y_pred = rolling_norm(y_pred, window=1200, method='bn_move_rank')
#        output = np.minimum(np.minimum(y['2017'].corr(y_pred['2017']), y['2018'].corr(y_pred['2018'])),
#                            y['2019'].corr(y_pred['2019']))
        output = y.corr(y_pred)
    # print(y.corr(y_pred))
    return output
    
    
def _calc_segmented_information_coefficient(y, y_pred, w):
    """Calculate the information coefficient"""
    if y_pred.count() / y.count() < 0.9:
        output = np.nan
    else:
        # y_pred = rolling_norm(y_pred, window=1200, method='bn_move_rank')
        temp = pd.concat([y, y_pred], axis=1, join='inner')
        output = temp.groupby(temp.index.year).apply(lambda _: _.corr().iloc[0,1]).min()
    return output


def _calc_sharpe_ratio(y, y_pred, w):
    if y_pred.count() / y.count() < 0.9:
        output = np.nan
    else:
        layers = 4
        layer_lims = (-1, 1)
        # y_pred = rolling_norm(y_pred, window=1200, method='bn_move_rank')
        df = pd.concat([y_pred, y], axis=1)
        df.columns = ['raw', 'ret']
        df_slice = SIF_Factor_Test.slice_by_minute(df)
        ps_raw = df_slice.iloc[:, 0]
        ps_return = df_slice.iloc[:, 1]
        pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)
        maxQ = layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        c.loc[c.bins == 0, 'ret'] = c.loc[c.bins == 0, 'ret'] * -1
        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        if (c_long.shape[0] + c_short.shape[0]) / y.count() < 0.4:
            output = np.nan
        else:
            c['ret_cumsum'] = c['ret'].cumsum()
            c_long['ret_cumsum'] = c_long['ret'].cumsum()
            c_short['ret_cumsum'] = c_short['ret'].cumsum()
            sharpe = c['ret'].to_frame().reset_index()
            sharpe['date'] = sharpe.dt.apply(lambda x: x.date())
            sharpe_daily_return = sharpe.groupby('date')['ret'].sum().to_frame()
            sharpe_ratio = sharpe_daily_return['ret'].mean() / sharpe_daily_return['ret'].std() * np.sqrt(242)
            # print(sharpe_ratio)
            output = sharpe_ratio
    return output


def _calc_r_square(y, y_pred, w):
    if y_pred.count() / y.count() < 0.7:
        output = np.nan
    else:
        layers = 4
        layer_lims = (-1, 1)
        # y_pred = rolling_norm(y_pred, window=1200, method='bn_move_rank')
        df = pd.concat([y_pred, y], axis=1)
        df.columns = ['raw', 'ret']
        df_slice = SIF_Factor_Test.slice_by_minute(df)
        ps_raw = df_slice.iloc[:, 0]
        ps_return = df_slice.iloc[:, 1]
        pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)
        maxQ = layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        c.loc[c.bins == 0, 'ret'] = c.loc[c.bins == 0, 'ret'] * -1
        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        # print(c_long.shape, c_short.shape)
        if ((c_long.shape[0] + c_short.shape[0]) / y.count() < 0.3) | (c_long.shape[0] == 0) | (c_short.shape[0] == 0):
            output = np.nan
        else:
            r_value1 = linregress(c['ret'].cumsum(), np.arange(c.shape[0]) + 1.0).rvalue
            r_value2 = linregress(c_long['ret'].cumsum(), np.arange(c_long.shape[0]) + 1.0).rvalue
            r_value3 = linregress(c_short['ret'].cumsum(), np.arange(c_short.shape[0]) + 1.0).rvalue
            r_value = np.minimum(r_value1, np.minimum(r_value2, r_value3))
            # print(r_value)
            output = r_value
    # print(output)
    return output


def _calc_fitness1(y, y_pred, w):
    if y_pred.count() / y.count() < 0.9:
        output = np.nan
    else:
        layers = 4
        layer_lims = (-1, 1)
        # y_pred = rolling_norm(y_pred, window=1200, method='bn_move_rank')
        df = pd.concat([y_pred, y], axis=1)
        df.columns = ['raw', 'ret']
        df_slice = SIF_Factor_Test.slice_by_minute(df)
        ps_raw = df_slice.iloc[:, 0]
        ps_return = df_slice.iloc[:, 1]
        pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)
        maxQ = layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        c.loc[c.bins == 0, 'ret'] = c.loc[c.bins == 0, 'ret'] * -1
        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        if (c_long.shape[0] + c_short.shape[0]) / y.count() < 0.4:
            output = np.nan
        else:
            c['ret_cumsum'] = c['ret'].cumsum()
            c_long['ret_cumsum'] = c_long['ret'].cumsum()
            c_short['ret_cumsum'] = c_short['ret'].cumsum()
            sharpe = c['ret'].to_frame().reset_index()
            sharpe['date'] = sharpe.dt.apply(lambda x: x.date())
            sharpe_daily_return = sharpe.groupby('date')['ret'].sum().to_frame()
            sharpe_ratio = sharpe_daily_return['ret'].mean() / sharpe_daily_return['ret'].std() * np.sqrt(242)
            stats = SIF_Factor_Test.signal_stats(signal_reshaper(ps_raw, signal_lims=layer_lims, layers=layers))
            long_deal_num = stats['long_deal_num']
            short_deal_num = stats['short_deal_num']
            ret_long_short = c.iloc[-1]['ret_cumsum']
            ret_per_deal = ret_long_short / (long_deal_num + short_deal_num)
            output = ret_per_deal * (sharpe_ratio ** 2)
    return output


def _calc_fitness2(y, y_pred, w):
    if y_pred.count() / y.count() < 0.7:
        output = np.nan
    else:
        layers = 4
        layer_lims = (-1, 1)
        # y_pred = rolling_norm(y_pred, window=1200, method='bn_move_rank')
        df = pd.concat([y_pred, y], axis=1)
        df.columns = ['raw', 'ret']
        df_slice = SIF_Factor_Test.slice_by_minute(df)
        information_coefficient = df_slice['raw'].corr(df_slice['ret'])
        ps_raw = df_slice.iloc[:, 0]
        ps_return = df_slice.iloc[:, 1]
        pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)
        maxQ = layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        c.loc[c.bins == 0, 'ret'] = c.loc[c.bins == 0, 'ret'] * -1
        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        if (c_long.shape[0] + c_short.shape[0]) / y.count() < 0.35:
            output = np.nan
        else:
            c['ret_cumsum'] = c['ret'].cumsum()
            c_long['ret_cumsum'] = c_long['ret'].cumsum()
            c_short['ret_cumsum'] = c_short['ret'].cumsum()
            stats = SIF_Factor_Test.signal_stats(signal_reshaper(ps_raw, signal_lims=layer_lims, layers=layers))
            long_deal_num = stats['long_deal_num']
            short_deal_num = stats['short_deal_num']
            ret_long_short = c.iloc[-1]['ret_cumsum']
            ret_per_deal = ret_long_short / (long_deal_num + short_deal_num)
            output = ret_per_deal * (information_coefficient ** 3)
    return output


def _calc_fitness3(y, y_pred, w):
    if y_pred.count() / y.count() < 0.7:
        output = np.nan
    else:
        layers = 4
        layer_lims = (-1, 1)
        df = pd.concat([y_pred, y], axis=1)
        df.columns = ['raw', 'ret']
        df_slice = SIF_Factor_Test.slice_by_minute(df)
        ps_raw = df_slice.iloc[:, 0]
        ps_return = df_slice.iloc[:, 1]
        pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)
        maxQ = layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        c.loc[c.bins == 0, 'ret'] = c.loc[c.bins == 0, 'ret'] * -1
        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        if ((c.shape[0]) / y.count() < 0.35) | (c_long.shape[0] == 0) | (c_short.shape[0] == 0):
            output = np.nan
        else:
            stats = SIF_Factor_Test.signal_stats(signal_reshaper(ps_raw, signal_lims=layer_lims, layers=layers))
            long_deal_num = stats['long_deal_num']
            short_deal_num = stats['short_deal_num']
            ret_long = c_long['ret'].cumsum().iloc[-1]
            ret_short = c_short['ret'].cumsum().iloc[-1]
            ret_long_after_fee = ret_long - (0.3 / 5000) * long_deal_num
            ret_short_after_fee = ret_short - (0.3 / 5000) * short_deal_num
            output = np.minimum(ret_long_after_fee, ret_short_after_fee)
    return output
    
    
def _calc_ami_10_3(y, y_pred, w):
    if y_pred.count() / y.count() < 0.9:
        ami = np.nan
    else:
        try:
            y_pred = pd.cut(y_pred, 10, labels=range(10)).astype('int')
        except:
            # temp_num = str(np.random.randint(low=0, high=1e10))
            # y_pred.to_hdf('/data/user/017024/waiting_for_delete/' + temp_num + '.h5', key=temp_num)
            ami = np.nan
        y[y>0.0008] = 1
        y[y<-0.0008] = -1
        y[(y<1)&(y>-1)] = 0
        ami = adjusted_mutual_info_score(y, y_pred)
        # print(ami)
    return ami
    

def _calc_icir(y, y_pred, w):
    if y_pred.count() / y.count() < 0.9:
        icir = np.nan
    else:
        ic = y.rolling(4800, min_periods=2400).corr(y_pred)
        icir = ic.mean() / ic.std()
    return icir


weighted_pearson = _Fitness(function=_weighted_pearson,
                            greater_is_better=True)
weighted_spearman = _Fitness(function=_weighted_spearman,
                             greater_is_better=True)
mean_absolute_error = _Fitness(function=_mean_absolute_error,
                               greater_is_better=False)
mean_square_error = _Fitness(function=_mean_square_error,
                             greater_is_better=False)
root_mean_square_error = _Fitness(function=_root_mean_square_error,
                                  greater_is_better=False)
log_loss = _Fitness(function=_log_loss,
                    greater_is_better=False)
information_coefficient = _Fitness(function=_calc_information_coefficient,
                                   greater_is_better=True)
segmented_information_coefficient = _Fitness(function=_calc_segmented_information_coefficient,
                                   greater_is_better=True)                                
sharpe_ratio = _Fitness(function=_calc_sharpe_ratio,
                        greater_is_better=True)
fitness1 = _Fitness(function=_calc_fitness1,
                    greater_is_better=True)
fitness2 = _Fitness(function=_calc_fitness2,
                    greater_is_better=True)
fitness3 = _Fitness(function=_calc_fitness3,
                    greater_is_better=True)
r_square = _Fitness(function=_calc_r_square,
                    greater_is_better=True)
ami = _Fitness(function=_calc_ami_10_3,
               greater_is_better=True)      
icir = _Fitness(function=_calc_icir,
                greater_is_better=True)              

_fitness_map = {'pearson': weighted_pearson,
                'spearman': weighted_spearman,
                'mean absolute error': mean_absolute_error,
                'mse': mean_square_error,
                'rmse': root_mean_square_error,
                'log loss': log_loss,
                'information_coefficient': information_coefficient,
                'segmented_information_coefficient': segmented_information_coefficient,
                'sharpe_ratio': sharpe_ratio,
                'r_square': r_square,
                'fitness1': fitness1,
                'fitness2': fitness2,
                'ami': ami,
                'icir': icir}
