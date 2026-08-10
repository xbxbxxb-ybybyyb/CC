"""The functions used to create programs.

The :mod:`gplearn_super.functions` module contains all of the functions used by
gplearn_super programs. It also contains helper methods for a user to define their
own custom functions.
"""

# Author: Trevor Stephens <trevorstephens.com>
#
# License: BSD 3 clause

import numpy as np
import pandas as pd
from sklearn.externals import six
import talib as ta
import bottleneck as bk
from skimage.util import view_as_windows
import scipy.stats

__all__ = ['make_function']


class _Function(object):

    """A representation of a mathematical relationship, a node in a program.

    This object is able to be called with NumPy vectorized arguments and return
    a resulting vector based on a mathematical relationship.

    Parameters
    ----------
    function : callable
        A function with signature function(x1, *args) that returns a Numpy
        array of the same shape as its arguments.

    name : str
        The name for the function as it should be represented in the program
        and its visualizations.

    arity : int
        The number of arguments that the ``function`` takes.

    """
    def __init__(self, function, name, arity, is_ts=False, params_need=None):
        self.function = function
        self.name = name
        self.arity = arity

        # 新增参数
        self.is_ts = is_ts  # bool, 代表此函数是否为时间序列函数，默认为False
        self.d = 0  # int, 时间序列回滚周期，若为时间序列函数则需要重设此参数
        self.params_need = params_need  # list, 部分TA-Lib的方法需要的固定参数及顺序

    def __call__(self, *args):
        if not self.is_ts:
            return self.function(*args)
        else:
            if self.d == 0:
                raise AttributeError("Please reset attribute 'd'")
            else:
                return self.function(*args, self.d)

    # 新增重设参数d的方法
    def set_d(self, d):
        self.d = d
        self.name += '_%d' % self.d


def make_function(function, name, arity):
    """Make a function node, a representation of a mathematical relationship.

    This factory function creates a function node, one of the core nodes in any
    program. The resulting object is able to be called with NumPy vectorized
    arguments and return a resulting vector based on a mathematical
    relationship.

    Parameters
    ----------
    function : callable
        A function with signature `function(x1, *args)` that returns a Numpy
        array of the same shape as its arguments.

    name : str
        The name for the function as it should be represented in the program
        and its visualizations.

    arity : int
        The number of arguments that the `function` takes.

    """
    if not isinstance(arity, int):
        raise ValueError('arity must be an int, got %s' % type(arity))
    if not isinstance(function, np.ufunc):
        if six.get_function_code(function).co_argcount != arity:
            raise ValueError('arity %d does not match required number of '
                             'function arguments of %d.'
                             % (arity,
                                six.get_function_code(function).co_argcount))
    if not isinstance(name, six.string_types):
        raise ValueError('name must be a string, got %s' % type(name))

    # Check output shape
    args = [np.ones(10) for _ in range(arity)]
    try:
        function(*args)
    except ValueError:
        raise ValueError('supplied function %s does not support arity of %d.'
                         % (name, arity))
    if not hasattr(function(*args), 'shape'):
        raise ValueError('supplied function %s does not return a numpy array.'
                         % name)
    if function(*args).shape != (10,):
        raise ValueError('supplied function %s does not return same shape as '
                         'input vectors.' % name)

    # Check closure for zero & negative input arguments
    args = [np.zeros(10) for _ in range(arity)]
    if not np.all(np.isfinite(function(*args))):
        raise ValueError('supplied function %s does not have closure against '
                         'zeros in argument vectors.' % name)
    args = [-1 * np.ones(10) for _ in range(arity)]
    if not np.all(np.isfinite(function(*args))):
        raise ValueError('supplied function %s does not have closure against '
                         'negatives in argument vectors.' % name)

    return _Function(function, name, arity)


def _protected_division(x1, x2):
    """Closure of division (x1/x2) for zero denominator."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(np.abs(x2) > 0.001, np.divide(x1, x2), 1.)


def _protected_sqrt(x1):
    """Closure of square root for negative arguments."""
    return np.sqrt(np.abs(x1))


def _protected_log(x1):
    """Closure of log for zero arguments."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(np.abs(x1) > 0.001, np.log(np.abs(x1)), 0.)


def _protected_inverse(x1):
    """Closure of log for zero arguments."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(np.abs(x1) > 0.001, 1. / x1, 0.)

add2 = make_function(function=np.add, name='add', arity=2)
sub2 = make_function(function=np.subtract, name='sub', arity=2)
mul2 = make_function(function=np.multiply, name='mul', arity=2)
div2 = make_function(function=_protected_division, name='div', arity=2)
sqrt1 = make_function(function=_protected_sqrt, name='sqrt', arity=1)
log1 = make_function(function=_protected_log, name='log', arity=1)
neg1 = make_function(function=np.negative, name='neg', arity=1)
inv1 = make_function(function=_protected_inverse, name='inv', arity=1)
abs1 = make_function(function=np.abs, name='abs', arity=1)
max2 = make_function(function=np.maximum, name='max', arity=2)
min2 = make_function(function=np.minimum, name='min', arity=2)
sin1 = make_function(function=np.sin, name='sin', arity=1)
cos1 = make_function(function=np.cos, name='cos', arity=1)
tan1 = make_function(function=np.tan, name='tan', arity=1)

_function_map = {'add': add2,
                 'sub': sub2,
                 'mul': mul2,
                 'div': div2,
                 'sqrt': sqrt1,
                 'log': log1,
                 'abs': abs1,
                 'neg': neg1,
                 'inv': inv1,
                 'max': max2,
                 'min': min2,
                 'sin': sin1,
                 'cos': cos1,
                 'tan': tan1}

def _ts_delay(data, d):
    # A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = np.empty_like(data)
        if d >= 0:
            output[d:] = data[:-d]
            output[:d] = np.nan
        else:
            output[:d] = data[-d:]
            output[d:] = np.nan

    else:
        output = data.shift(periods=d)
    return output
ts_delay1 = _Function(function=_ts_delay, name='ts_delay', arity=1, is_ts=True)

def _ts_delta(data, d):
    # A_i - A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = data - _ts_delay(data, d)
    else:
        output = data.diff(periods=d)
    return output
ts_delta1 = _Function(function=_ts_delta, name='ts_delta', arity=1, is_ts=True)

def _ts_max(data, d):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_max(data, window=d, min_count=int(d / 2), axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output
ts_max1 = _Function(function=_ts_max, name='ts_max', arity=1, is_ts=True)


def _ts_mean(data, d):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output
ts_mean1 = _Function(function=_ts_mean, name='ts_mean', arity=1, is_ts=True)

def _ts_median(data, d):
    # moving time-series meidan for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_median(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output
ts_median1 = _Function(function=_ts_median, name='ts_median', arity=1, is_ts=True)

def _ts_min(data, d):
    # moving time-series minimum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_min(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output
ts_min1 = _Function(function=_ts_min, name='ts_min', arity=1, is_ts=True)


def _ts_argmax(data, d):
    # which moment ts_max(x, d) occurred on.
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    elif isinstance(data, np.ndarray):
        output = bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output
ts_argmax1 = _Function(function=_ts_argmax, name='ts_argmax', arity=1, is_ts=True)


def _ts_argmin(data, d):
    # which moment ts_min(x, d) occurred on.
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    elif isinstance(data, np.ndarray):
        output = bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output
ts_argmin1 = _Function(function=_ts_argmin, name='ts_argmin', arity=1, is_ts=True)

def _ts_std(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=data.index, name=data.name)
    return output
ts_std1 = _Function(function=_ts_std, name='ts_std', arity=1, is_ts=True)


def _ts_sum(data, d):
    # moving time-series sum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_sum(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output
ts_sum1 = _Function(function=_ts_sum, name='ts_sum', arity=1, is_ts=True)

def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    elif data.ndim == 2:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding

def _ts_skew(data, d):
    # moving time-series skew over the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = np.full_like(data, np.nan)
            temp = rolling_window_upgrade(data, d)
            output[d - 1:] = scipy.stats.skew(temp, axis=-1, bias=False)
        else:
            output = data.rolling(d, min_periods=int(d / 2)).skew()
            output.iloc[:d - 1] = np.nan
    return output
ts_skew1 = _Function(function=_ts_skew, name='ts_skew', arity=1, is_ts=True)


def _ts_corr(data1, data2, d):
    # data1, data2过去d条数据的时序相关系数
    if type(data1) != type(data2):
        raise TypeError('`data1` and `data2` must be the same type.')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if not (isinstance(data1, pd.Series) or isinstance(data1, pd.DataFrame) or isinstance(data1, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data1, np.ndarray):
        output = np.full(data1.shape, np.nan)
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
        flag = np.isnan(data1_expanding) | np.isnan(data2_expanding)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        data1_expanding[flag] = np.nan
        data2_expanding[flag] = np.nan
        data1_expanding_centralized = data1_expanding - np.nanmean(data1_expanding, axis=-1, keepdims=True)
        data2_expanding_centralized = data2_expanding - np.nanmean(data2_expanding, axis=-1, keepdims=True)
        output[d - 1:] = np.nansum(data1_expanding_centralized * data2_expanding_centralized, axis=-1) / np.sqrt(
            np.nansum(data1_expanding_centralized ** 2, axis=-1) * np.nansum(data2_expanding_centralized ** 2,
                                                                             axis=-1)) * flag2
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).corr(data2)
        output.iloc[:d - 1] = np.nan
    return output
ts_corr1 = _Function(function=_ts_corr, name='ts_corr', arity=2, is_ts=True)


def _ts_cov(data1, data2, d):
    # data1, data2过去d条数据的时序协方差
    if type(data1) != type(data2):
        raise TypeError('`data1` and `data2` must be the same type.')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if not (isinstance(data1, pd.Series) or isinstance(data1, pd.DataFrame) or isinstance(data1, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data1, np.ndarray):
        output = np.full(data1.shape, np.nan)
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
        flag = np.isnan(data1_expanding) | np.isnan(data2_expanding)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        data1_expanding[flag] = np.nan
        data2_expanding[flag] = np.nan
        data1_expanding_centralized = data1_expanding - np.nanmean(data1_expanding, axis=-1, keepdims=True)
        data2_expanding_centralized = data2_expanding - np.nanmean(data2_expanding, axis=-1, keepdims=True)
        output[d - 1:] = np.nansum(data1_expanding_centralized*data2_expanding_centralized, axis=-1) * flag2 / (
                d - 1 - flag1)
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).cov(data2)
        output.iloc[:d - 1] = np.nan
    return output
ts_cov1 = _Function(function=_ts_cov, name='ts_cov', arity=2, is_ts=True)


def _ts_decay_linear(data, d, weight=None):
    # weighted moving average over the past d periods
    # default weight: linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    if weight is None:
        weight = np.arange(d) + 1.0
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if data.ndim == 2:
        weight_expanding = np.tile(weight, (data_expanding.shape[0], data_expanding.shape[1], 1))
    elif data.ndim == 1:
        weight_expanding = np.tile(weight, (data_expanding.shape[0], 1))
    flag = np.isnan(data_expanding) | np.isnan(weight_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    weight_expanding[flag] = np.nan
    output_need = (np.nansum(data_expanding * weight_expanding, axis=-1) / np.nansum(weight_expanding, axis=-1)) * flag2
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d - 1:] = output_need
    elif isinstance(data, pd.Series):
        output = pd.Series(np.nan, index=data.index, name=data.name)
        output.iloc[d - 1:] = output_need
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        output.iloc[d - 1:] = output_need
    return output
ts_decay_linear1 = _Function(function=_ts_decay_linear, name='ts_decay_linear', arity=1, is_ts=True)

def replace_inf(data, x=np.nan):
    '''replace inf to a predefined number for the input data
    parameters
    --------------------------------------------------
    data: dataframe, series or ndarray
        the data which contains inf
    x: int, float or np.nan, optional (default=np.nan)
        the value used to replace inf
    --------------------------------------------------
    return
    --------------------------------------------------
    data: input data whose inf has been replaced
        the data whose inf is replaced
    --------------------------------------------------
    '''
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'the data structure of input is illegal'
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        data = data.replace([-np.inf, np.inf], x)
    elif isinstance(data, np.ndarray):
        data[np.isinf(data)] = x
    return data


def replace_zero(data, x=np.nan):
    """
    replace 0 to a predefined number for the input data
    :param data: dataframe, series or np.ndarray
        the data which contains 0
    :param x: int, float or np.nan, optional (default=np.nan)
        the value used to replace 0
    :return: same data structure as input data
        input data whose 0 has been replaced
    """
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal, must be pd.Series, pd.DataFrame or np.ndarray'
    if isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
    data[abs(data) < 1e-8] = x
    return data

def _ts_pct_change(data, d=1):
    # (A_n - A_(n-d)) / A_(n-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance (data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d:] = ((data[d:]-data[:-d]) / replace_zero(data[:-d]))
    else:
        output = data.pct_change(d, fill_method=None)
    return output
ts_pct_change1 = _Function(function=_ts_pct_change, name='ts_pct_change', arity=1, is_ts=True)


def _ts_rank(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
    return output
ts_rank1 = _Function(function=_ts_rank, name='ts_rank', arity=1, is_ts=True)


_ts_function_map = {
    'ts_delay': ts_delay1,
    'ts_delta': ts_delta1,
    'ts_min': ts_min1,
    'ts_max': ts_max1,
    'ts_mean': ts_mean1,
    'ts_sum': ts_sum1,
    'ts_std': ts_std1,
    'ts_rank': ts_rank1,
    'ts_skew': ts_skew1,
    # 'ts_corr': ts_corr1,
    # 'ts_cov': ts_cov1,
    'ts_median': ts_median1,
    'ts_argmin': ts_argmin1,
    'ts_argmax': ts_argmax1,
    'ts_decay_linear': ts_decay_linear1,
    'ts_pct_change': ts_pct_change1
}



fixed_midprice = _Function(function=ta.MIDPRICE, name='midprice', arity=0, is_ts=True, params_need=['high', 'close'])
fixed_aroonosc = _Function(function=ta.AROONOSC, name='AROONOSC', arity=0, is_ts=True, params_need=['high', 'close'])

_fixed_function_map = {
    'MIDPRICE': fixed_midprice,
    'AROONOSC': fixed_aroonosc
}
