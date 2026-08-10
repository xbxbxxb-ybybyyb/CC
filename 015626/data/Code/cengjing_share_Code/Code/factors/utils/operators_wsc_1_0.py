import pandas as pd
import numpy as np
import bottleneck as bk
import scipy.stats
from help_functions_wsc import rolling_window, rolling_window_upgrade, replace_zero
import warnings

warnings.filterwarnings('ignore')

__all__ = ['add2', 'div2', 'inv1', 'log', 'mul2', 'max2', 'min2', 'neg1', 'pairwise_corr_np', 'rolling_norm',
           'section_rank_np', 'sqrt', 'square', 'sub2', 'ts_argmax', 'ts_argmin', 'ts_corr', 'ts_cov',
           'ts_decay_linear', 'ts_delay', 'ts_delta', 'ts_ema', 'ts_ema_span', 'ts_max', 'ts_mean', 'ts_median',
           'ts_min', 'ts_pct_change', 'ts_pred', 'ts_pred_delta', 'ts_rank', 'ts_reg_alpha', 'ts_reg_beta',
           'ts_reg_residual', 'ts_skew', 'ts_std', 'ts_sum', 'ts_truncated_ema', 'ts_truncated_ema_span']


def add2(x1, x2):
    return np.add(x1, x2)


def div2(x1, x2):
    x2 = replace_zero(x2)
    return np.divide(x1, x2)


def inv1(df1):
    df1 = replace_zero(df1)
    return 1 / df1


def log(data):
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    data = replace_zero(data)
    output = np.log(data)
    return output


def mul2(x1, x2):
    return np.multiply(x1, x2)


def max2(x1, x2):
    return np.maximum(x1, x2)


def min2(x1, x2):
    return np.minimum(x1, x2)


def neg1(x):
    return -x


def pairwise_corr_np(data1, data2, axis=0):
    # 对两个相同shape的np.ndarray，计算对应行/列的相关性
    if not (isinstance(data1, np.ndarray) & isinstance(data2, np.ndarray)):
        raise TypeError('Only supports the following type: np.ndarray')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if data1.ndim not in [1, 2]:
        raise ValueError('`data1` and `data2` must be a 1D or 2D array')
    if data1.ndim == 1:
        return np.ma.corrcoef(np.ma.masked_invalid(data1), np.ma.masked_invalid(data2)).data[0, 1]
    else:
        flag = np.isnan(data1) | np.isnan(data2)
        data1[flag] = np.nan
        data2[flag] = np.nan
        if axis == 1:
            data1_centralized = data1 - np.nanmean(data1, axis=1, keepdims=True)
            data2_centralized = data2 - np.nanmean(data2, axis=1, keepdims=True)
            return np.nansum(data1_centralized * data2_centralized, axis=1) / np.sqrt(
                np.nansum(data1_centralized ** 2, axis=1) * np.nansum(data2_centralized ** 2, axis=1))
        elif axis == 0:
            data1_centralized = data1 - np.nanmean(data1, axis=0)
            data2_centralized = data2 - np.nanmean(data2, axis=0)
            return np.nansum(data1_centralized * data2_centralized, axis=0) / np.sqrt(
                np.nansum(data1_centralized ** 2, axis=0) * np.nansum(data2_centralized ** 2, axis=0))


def rolling_norm(data, window=1200):
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if window == 1:
        return data
    else:
        if isinstance(data, pd.DataFrame):
            data_max = pd.DataFrame(bk.move_max(data, window=window, min_count=int(window / 2), axis=0),
                                    index=data.index, columns=data.columns)
            data_min = pd.DataFrame(bk.move_min(data, window=window, min_count=int(window / 2), axis=0),
                                    index=data.index, columns=data.columns)
            temp = data_max - data_min
            temp[abs(temp) < 1e-8] = np.nan
            data = (data - data_min) / temp
        elif isinstance(data, pd.Series):
            data_max = pd.Series(bk.move_max(data, window=window, min_count=int(window / 2), axis=0),
                                 index=data.index, name=data.name)
            data_min = pd.Series(bk.move_min(data, window=window, min_count=int(window / 2), axis=0),
                                 index=data.index, name=data.name)
            temp = data_max - data_min
            temp[abs(temp) < 1e-8] = np.nan
            data = (data - data_min) / temp
        elif isinstance(data, np.ndarray):
            data_max = bk.move_max(data, window=window, min_count=int(window / 2), axis=0)
            data_min = bk.move_min(data, window=window, min_count=int(window / 2), axis=0)
            temp = data_max - data_min
            temp[abs(temp) < 1e-8] = np.nan
            data = (data - data_min) / temp
        return 2 * data - 1


def section_rank_np(data, pct=False):
    # 基于numpy的截面排序，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = data.argsort().argsort() + 1.  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


def shift_np(arr, num, fill_value=np.nan):
    # shift function for numpy
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result


def sqrt(data):
    # square root operation
    output = np.sqrt(data)
    return output


def square(data):
    # x**2
    output = data ** 2
    return output



def sub2(x1, x2):
    return np.subtract(x1, x2)


def ts_argmax(data, d):
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


def ts_argmin(data, d):
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


def ts_corr(data1, data2, d):
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


def ts_cov(data1, data2, d):
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


def ts_decay_linear(data, d, weight=None):
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


def ts_delay(data, d):
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


def ts_delta(data, d):
    # A_i - A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = data - ts_delay(data, d)
    else:
        output = data.diff(periods=d)
    return output


def ts_ema(df1, d):
    output = df1.ewm(alpha=d, adjust=False).mean()
    return output


def ts_ema_span(df1, d):
    output = df1.ewm(span=d, adjust=False).mean()
    return output


def ts_max(data, d):
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


def ts_mean(data, d):
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


def ts_median(data, d):
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


def ts_min(data, d):
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


def ts_pct_change(data, d=1):
    # (A_n - A_(n-d)) / A_(n-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance (data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d:] = ((data[d:]-data[:-d]) / replace_zero(data[:-d]))
    else:
        output = data.pct_change(d, fill_method=None)
    return output


def ts_pred(data, d, reg_x=None):
    """
    use rolling linear regression to predict value
    :param data: dataframe, series or ndarray
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe or series
        the predicted value of rolling linear regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    return reg_pred


def ts_pred_delta(data, d, reg_x=None):
    """
    the difference of the predicted value of rolling linear regression and real value
    :param data: dataframe, series or ndarray
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe, series or ndarray
        the difference of the predicted value of rolling linear regression and real value
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    reg_delta = data - reg_pred
    return reg_delta


def ts_rank(data, d):
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


def ts_reg_alpha(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到截距项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        intercept term of regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
        if data.ndim == 2:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], data_expanding.shape[1], 1))
        elif data.ndim == 1:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], 1))
    else:
        if len(reg_x) not in [data.shape[0], d]:
            raise ValueError('the length of `reg_x` must equals the length of data or d.')
        elif len(reg_x) == d:
            if data.ndim == 2:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], data_expanding.shape[1], 1))
            elif data.ndim == 1:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], 1))
        elif len(reg_x) == data.shape[0]:
            reg_x_expanding = rolling_window_upgrade(reg_x, d)

    flag = np.isnan(data_expanding) | np.isnan(reg_x_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    reg_x_expanding[flag] = np.nan
    data_expanding_centralized = data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)
    reg_x_expanding_centralized = reg_x_expanding - np.nanmean(reg_x_expanding, axis=-1, keepdims=True)
    reg_beta = np.nansum(data_expanding_centralized * reg_x_expanding_centralized, axis=-1) / np.nansum(
        reg_x_expanding_centralized ** 2, axis=-1)
    output_need = (np.nanmean(data_expanding, axis=-1) - reg_beta * np.nanmean(reg_x_expanding, axis=-1)) * flag2
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


def ts_reg_beta(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到斜率项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        slope term of regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
        if data.ndim == 2:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], data_expanding.shape[1], 1))
        elif data.ndim == 1:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], 1))
    else:
        if len(reg_x) not in [data.shape[0], d]:
            raise ValueError('the length of `reg_x` must equals the length of data or d.')
        elif len(reg_x) == d:
            if data.ndim == 2:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], data_expanding.shape[1], 1))
            elif data.ndim == 1:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], 1))
        elif len(reg_x) == data.shape[0]:
            reg_x_expanding = rolling_window_upgrade(reg_x, d)

    flag = np.isnan(data_expanding) | np.isnan(reg_x_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    reg_x_expanding[flag] = np.nan
    data_expanding_centralized = data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)
    reg_x_expanding_centralized = reg_x_expanding - np.nanmean(reg_x_expanding, axis=-1, keepdims=True)   
    output_need = np.nansum(data_expanding_centralized * reg_x_expanding_centralized, axis=-1) / np.nansum(
        reg_x_expanding_centralized ** 2, axis=-1) * flag2
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


def ts_reg_residual(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到的残差项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        residual term of regression
    """
    if reg_x is None:  # or (len(reg_x) == d):
        reg_x_expanding = np.full_like(data, d)
    elif len(reg_x) == d:
        reg_x_expanding = np.full_like(data, reg_x[-1])
    elif len(reg_x) == data.shape[0]:
        reg_x_expanding = reg_x
    reg_slope = ts_reg_beta(data, d, reg_x)
    reg_intercept = ts_reg_alpha(data, d, reg_x)
    output = data - reg_slope * reg_x_expanding - reg_intercept
    return output


def ts_skew(data, d):
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
            output = df1.rolling(d, min_periods=int(d / 2)).skew()
            output.iloc[:d - 1] = np.nan
    return output


def ts_std(data, d):
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


def ts_sum(data, d):
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


def ts_truncated_ema(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span(data, d, span):
    # truncated ema
    return ts_truncated_ema(data=data, d=d, alpha=2 / (span + 1))