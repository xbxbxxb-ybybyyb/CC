import numpy as np
import pandas as pd
import bottleneck as bk
from skimage.util import view_as_windows

def replace_zero(data, x=np.nan):
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal, must be pd.Series, pd.DataFrame or np.ndarray'
    if isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
    data[abs(data) < 1e-8] = x
    return data


def type_convertor(func):
    def wrapper(*args, **kwargs):
        data = args[0]
        if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
            raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
        output = func(*args, **kwargs)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(output, index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(output, index=data.index, name=data.name)
        return output
    return wrapper


def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    else:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding


def abs1(data):
    return np.abs(data)


def add2(data1, data2):
    return np.add(data1, data2)


def div2(x1, x2):
    x2 = replace_zero(x2)
    return np.divide(x1, x2)


def div2(data1, data2):
    data2 = replace_zero(data2)
    return np.divide(data1, data2)


def inv1(data):
    data = replace_zero(data)
    return 1 / data


def log(data):
    data = replace_zero(data)
    output = np.log(data)
    return output


def mul2(data1, data2):
    return np.multiply(data1, data2)


def max2(data1, data2):
    return np.maximum(data1, data2)


def min2(data1, data2):
    return np.minimum(data1, data2)


def neg1(data):
    return -data


@type_convertor
def rolling_norm(data, window=1200):
    if window == 1:
        return data
    else:
        data_max = bk.move_max(data, window=window, min_count=int(window / 2), axis=0)
        data_min = bk.move_min(data, window=window, min_count=int(window / 2), axis=0)
        data = (data - data_min) / replace_zero(data_max - data_min)
        return 2 * data - 1


def sqrt(data):
    # square root operation
    output = np.sqrt(data)
    return output


def square(data):
    # x**2
    output = data ** 2
    return output


def sub2(data1, data2):
    return np.subtract(data1, data2)


@type_convertor
def ts_argmax(data, d):
    # which moment ts_max(x, d) occurred on.
    output = bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output


@type_convertor
def ts_argmin(data, d):
    # which moment ts_min(x, d) occurred on.
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
        output[d - 1:] = np.nansum(data1_expanding_centralized * data2_expanding_centralized, axis=-1) * flag2 / (
                d - 1 - flag1)
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).cov(data2)
        output.iloc[:d - 1] = np.nan
    return output


@type_convertor
def ts_decay_linear(data, d, weight=None):
    # weighted moving average over the past d periods
    # default weight: linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
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
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
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


@type_convertor
def ts_max(data, d):
    # moving time-series max for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_max(data, window=d, min_count=int(d / 2), axis=0)
    return output


@type_convertor
def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
    return output


@type_convertor
def ts_median(data, d):
    # moving time-series meidan for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_median(data, window=d, min_count=int(d / 2), axis=0)
    return output


@type_convertor
def ts_min(data, d):
    # moving time-series minimum for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_min(data, window=d, min_count=int(d / 2), axis=0)
    return output


def ts_pct_change(data, d=1):
    # (A_n - A_(n-d)) / A_(n-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d:] = ((data[d:] - data[:-d]) / replace_zero(data[:-d]))
    else:
        output = data.pct_change(d, fill_method=None)
    return output


@type_convertor
def ts_position(data, d):
    if not isinstance(data, np.ndarray):
        data = data.values
    data_expanding = rolling_window_upgrade(data, d)
    output_need = (data_expanding[..., -1] - np.nanmin(data_expanding, axis=-1)) / (
            np.nanmax(data_expanding, axis=-1) - np.nanmin(data_expanding, axis=-1))
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output


@type_convertor
def ts_reg_alpha(data, d, reg_x=None):
    # 过去d期A对reg_x或者1:d滚动回归得到截距项
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
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output


@type_convertor
def ts_reg_beta(data, d, reg_x=None):
    # 过去d期A对reg_x或者1:d滚动回归得到斜率项
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
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output


def ts_reg_residual(data, d, reg_x=None):
    # 过去d期A对reg_x或者1:d滚动回归得到的残差项
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

# 当日数据不参与建模
def ts_reg_residual_shift1(data, d, reg_x=None):
    # 过去d期A对reg_x或者1:d滚动回归得到的残差项
    if reg_x is None:  # or (len(reg_x) == d):
        reg_x_expanding = np.full_like(data, d)
    elif len(reg_x) == d:
        reg_x_expanding = np.full_like(data, reg_x[-1])
    elif len(reg_x) == data.shape[0]:
        reg_x_expanding = reg_x
    assert reg_x_expanding.ndim == 1
    _data = pd.Series(data).shift(1).values
    _reg_x = pd.Series(reg_x).shift(1).values
    reg_slope = ts_reg_beta(_data, d, _reg_x)
    reg_intercept = ts_reg_alpha(_data, d, _reg_x)
    output = data - reg_slope * reg_x_expanding - reg_intercept
    return output


def ts_pred(data, d, reg_x=None):
    # use rolling linear regression to predict value
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    return reg_pred


def ts_pred_delta(data, d, reg_x=None):
    # the difference of the predicted value of rolling linear regression and real value
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    reg_delta = data - reg_pred
    return reg_delta


@type_convertor
def ts_rank(data, d=1200):
    # moving time-series rank for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
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
            output = data.rolling(d, min_periods=int(d / 2)).skew()
            output.iloc[:d - 1] = np.nan
    return output


@type_convertor
def ts_std(data, d):
    # moving time-series std for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1)
    return output


@type_convertor
def ts_sum(data, d):
    # moving time-series sum for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_sum(data, window=d, min_count=int(d / 2), axis=0)
    return output


def sigmoid(x1):
    # Special case of logistic function to transform to probabilities.
    with np.errstate(over='ignore', under='ignore'):
        return 1 / (1 + np.exp(-x1))


def auto_corr(data, d1, d2):
    # as follows
    return ts_corr(data, ts_delay(data, d1), d2)


def up_outlier_ratio(data, d1, d2, n=1.5):
    # 对过去d1长度的数据集，求n倍std以外的异常点比例，其中用于计算均值、方差从而衡量异常点的数据长度为d2
    data_mean = ts_mean(data, d2)
    data_std = ts_std(data, d2)
    up_flag = data > (data_mean + n * data_std)
    up_ratio = ts_mean(up_flag.astype('int'), d1)
    return up_ratio


def down_outlier_ratio(data, d1, d2, n=1.5):
    # 对过去d1长度的数据集，求n倍std以外的异常点比例，其中用于计算均值、方差从而衡量异常点的数据长度为d2
    data_mean = ts_mean(data, d2)
    data_std = ts_std(data, d2)
    down_flag = data < (data_mean - n * data_std)
    down_ratio = ts_mean(down_flag.astype('int'), d1)
    return down_ratio


def outlier_ratio(data, d1, d2, n=1.5):
    # 对过去d1长度的数据集，求n倍std以外的异常点比例，其中用于计算均值、方差从而衡量异常点的数据长度为d2
    up_ratio = up_outlier_ratio(data, d1, d2, n)
    down_ratio = down_outlier_ratio(data, d1, d2, n)
    return up_ratio + down_ratio


def coefficient_of_variation(data, d):
    # 滚动变异系数
    return ts_std(data, d) / replace_zero(ts_mean(data, d))


def long_short_ma_ratio(data, d1, d2):
    return ts_mean(data, d1) / ts_mean(data, d2)


def up_down_ratio(data, d1, d2=1):
    data_delta = (ts_delta(data, d2) > 0).astype('int')
    up_ratio = ts_mean(data_delta, d1)
    return up_ratio


def cross_hub_num(data, d):
    # 过去一段时间曲线穿越中枢的次数
    data_centralized = data - ts_mean(data, d)
    flag = (data_centralized * ts_delay(data_centralized, 1) < 0).astype('int')  # 若该点和上一个点符号相反，则表示穿越中枢
    output = ts_sum(flag, d)
    return output


def bbands_up(price, time_period=5, a=1.5):
    # Bollinger Bands：过去一段时间的均价加上/减去过去一段时间价格的标准差
    price_ma = ts_mean(price, time_period)
    price_std = ts_std(price, time_period)
    price_up_track = price_ma + a * price_std
    return price_up_track


def bbands_down(price, time_period=5, a=1.5):
    # Bollinger Bands：过去一段时间的均价加上/减去过去一段时间价格的标准差
    price_ma = ts_mean(price, time_period)
    price_std = ts_std(price, time_period)
    price_down_track = price_ma - a * price_std
    return price_down_track


def dema(price, time_period=30):
    price_ema = ts_mean(price, time_period)
    price_dema = 2 * price_ema - ts_mean(price_ema, time_period)
    return price_dema


def midpoint(price, time_period):
    # (highest value + lowest value)/2
    highest_price = ts_max(price, time_period)
    lowest_price = ts_min(price, time_period)
    price_midpoint = (highest_price + lowest_price) / 2
    return price_midpoint


def midprice(price_high, price_low, time_period):
    _price_high = np.maximum(price_high, price_low)
    _price_low = np.minimum(price_high, price_low)
    highest_price = ts_max(_price_high, time_period)
    lowest_price = ts_min(_price_low, time_period)
    price_midprice = (highest_price + lowest_price) / 2
    return price_midprice


def trima(price, time_period):
    if time_period % 2 == 0:
        price_trima = ts_mean(ts_mean(price, int(time_period / 2 + 1)), int(time_period / 2))
    else:
        price_trima = ts_mean(ts_mean(price, int((time_period + 1) / 2)), int((time_period + 1) / 2))
    return price_trima


def di(price_high, price_low, price_close, time_period=14):
    # 动量指标，但是看不懂在干嘛，而且不同版本的公式还不一样
    price_high = np.maximum(np.maximum(price_high, price_low), price_close)
    price_low = np.minimum(np.minimum(price_high, price_low), price_close)
    max_high = ts_delta(price_high, 1)
    max_high[max_high < 0] = 0
    max_low = -ts_delta(price_low, 1)
    max_low[max_low < 0] = 0
    xpdm = ts_delta(price_high, 1)
    xpdm[max_high <= max_low] = 0
    pdm = ts_mean(xpdm, time_period)
    xndm = -ts_delta(price_low, 1)
    xndm[max_low <= max_high] = 0
    ndm = ts_mean(xndm, time_period)
    price_atr = atr(price_high, price_low, price_close, time_period)
    di_plus = pdm / price_atr
    di_minus = ndm / price_atr
    return di_plus, di_minus


def di_plus(price_high, price_low, price_close, time_period=14):
    return di(price_high, price_low, price_close, time_period)[0]


def di_plus(price_high, price_low, price_close, time_period=14):
    return di(price_high, price_low, price_close, time_period)[1]


def dx(price_high, price_low, price_close, time_period=14):
    di_plus, di_minus = di(price_high, price_low, price_close, time_period)
    price_dx = abs(di_plus - di_minus) / abs(di_plus + di_minus)
    return price_dx


def po(price, fast_time_period=12, slow_time_period=26):
    # PO(price oscillator), the difference between two moving averages.
    slow_ma = ts_mean(price, slow_time_period)
    fast_ma = ts_mean(price, fast_time_period)
    price_po = slow_ma - fast_ma
    return price_po


def aroon(price_high, price_low, time_period=14):
    """
    The word aroon is Sanskrit for "dawn's early night".
    The Aroon indicator attempts to show when is a new trend is dawning.
    The indicator consists of two lines(up and down) that measures how long it has been since the highest high/lowest
    low has occurred within a period range.
    """
    price_high = np.maximum(price_high, price_low)
    price_low = np.minimum(price_high, price_low)
    price_aroon_up = 1 + ts_argmax(price_high, time_period)
    price_aroon_down = 1 + ts_argmin(price_low, time_period)
    price_aroon = price_aroon_up - price_aroon_down
    return price_aroon_up, price_aroon_down, price_aroon


def cci(typical_price, time_period=14):
    """
    CCI(commodity channel index)指标用来衡量典型价格与其一段时间的移动平均的偏离程度，可以用来反映市场的超买超卖状态；
    一般认为，CCI超过100则市场处于超买状态，低于-100则市场处于超卖状态。
    """
    typical_price_ma = ts_mean(typical_price, time_period)
    typical_price_mean_deviation = ts_mean(abs(typical_price - typical_price_ma), time_period)
    price_cci = (typical_price - typical_price_ma) / (0.015 * typical_price_mean_deviation)
    return price_cci


def cmo(price_close, time_period=14):
    """
    CMO(Chande momentum oscillator)指标，用于衡量动量，分子表示总的动量（向上的动量-向下的动量），分母表示这段时间价格的
    移动距离。可以认为是RSI指标的变形。
    There are several ways to interpret the CMO. Values over 0.5 indicate overbought conditions, while values under -0.5
    indicate oversold conditions. High CMO values indicate strong trends. When the CMO crosses above a moving average of
    CMO, it is a buy signal, crossing down is a sell signal.
    """
    price_delta_up = ts_delta(price_close, 1)
    price_delta_up[price_delta_up < 0] = 0
    price_delta_down = -ts_delta(price_close, 1)
    price_delta_down[price_delta_down < 0] = 0
    price_delta_up_sum = ts_sum(price_delta_up, time_period)
    price_delta_down_sum = ts_sum(price_delta_down, time_period)
    price_cmo = (price_delta_up_sum - price_delta_down_sum) / replace_zero(price_delta_up_sum + price_delta_down_sum)
    return price_cmo


def ppo(price_close, fast_period=12, slow_period=26):
    """
    PPO(Percentage Price Oscillator) shows the percentage difference between two moving averages.
    """
    slow_ma = ts_mean(price_close, slow_period)
    fast_ma = ts_mean(price_close, fast_period)
    price_ppo = (slow_ma - fast_ma) / fast_ma
    return price_ppo



def rocr(price_close, time_period=10):
    """
    rocr(rate fo change ratio)技术指标，当前价格与上一时段价格的比值
    """
    price_rocr = ts_pct_change(price_close, time_period) + 1
    return price_rocr



def rsi(price_close, time_period=14):
    """
    rsi(relative strength index) calculates a ratio of the recent upward price movements to the absolute price movement.
    """
    close_up = ts_delta(price_close, 1)
    close_up[close_up < 0] = 0
    close_down = -ts_delta(price_close, 1)
    close_down[close_down < 0] = 0
    close_up_ma = ts_mean(close_up, time_period)
    close_down_ma = ts_mean(close_down, time_period)
    price_rsi = close_up_ma / (close_up_ma + close_down_ma)
    return price_rsi


def distance_to_variation(data, d):
    # 两个点之间的直线距离和走过位移之比
    data_distance = ts_delta(data, d)
    data_journey = ts_sum(abs(ts_delta(data, 1)), d)
    return data_distance / replace_zero(data_journey)


def distance_to_variation_abs(data, d):
    data_distance = abs(ts_delta(data, d))
    data_journey = ts_sum(abs(ts_delta(data, 1)), d)
    return data_distance / replace_zero(data_journey)


def ts_midpoint(data, d):
    return (data + ts_delay(data, d)) / 2


def ts_maxmin_distance(data, d):
    data_rolling_max = ts_argmax(data, d)
    data_rolling_min = ts_argmin(data, d)
    return data_rolling_max - data_rolling_min


def ts_distance_from_mean(data, d):
    return data - ts_mean(data, d)


def ts_ratio_from_mean(data, d):
    return data / replace_zero(ts_mean(data, d)) - 1


def macd(price_close, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD(moving average convergence divergence)指标衡量快速均线与慢速均线的差值，是一个动量指标。
    上涨趋势中快速均线会比慢速均线涨得快，反之亦然，因此MACD上穿/下穿0可以用于构造交易信号，或是用其值衡量超买/超卖状态；
    另一种构造信号的方式是求MACD与其移动平均线的差得到MACD柱，并与MACD柱上穿/下穿0来构造交易信号。
    """
    price_macd = ts_mean(price_close, fast_period) - ts_mean(price_close, slow_period)
    price_macd_signal = ts_mean(price_macd, signal_period)
    price_macd_histogram = price_macd - price_macd_signal
    return price_macd_histogram


def atr(price_high, price_low, price_close, time_period=14):
    # ATR(average true range)技术指标，用于衡量市场波动，波动越大则值越大
    price_high = np.maximum(np.maximum(price_high, price_low), price_close)
    price_low = np.minimum(np.minimum(price_high, price_low), price_close)
    price_tr = tr(price_high, price_low, price_close)
    price_atr = ts_mean(price_tr, time_period)
    return price_atr


def mfi(typical_price, volume, time_period=14):
    money_flow_pos = typical_price * volume
    money_flow_pos[ts_delta(typical_price, 1) < 0] = 0
    money_flow_neg = typical_price * volume
    money_flow_neg[ts_delta(typical_price, 1) > 0] = 0
    money_flow_pos_sum = ts_sum(money_flow_pos, time_period)
    money_flow_neg_sum = ts_sum(money_flow_neg, time_period)
    price_mfi = money_flow_pos_sum / replace_zero(money_flow_pos_sum + money_flow_neg_sum)
    return price_mfi