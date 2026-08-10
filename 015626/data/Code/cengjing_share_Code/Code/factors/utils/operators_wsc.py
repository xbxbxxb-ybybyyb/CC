import pandas as pd
import numpy as np
import bottleneck as bk
from help_functions_wsc import rolling_window, replace_zero, multi_processing_joblib
import warnings
warnings.filterwarnings('ignore')


def add2(x1, x2):
    return np.add(x1, x2)


def div2(x1, x2):
    x2 = replace_zero(x2)
    return np.divide(x1, x2)


def inv(df1):
    df1 = replace_zero(df1)
    return 1 / df1


def log(df1):
    output = np.log(df1[df1 > 0])
    output = output.reindex(df1.index)
    return output


def mul2(x1, x2):
    return np.multiply(x1, x2)


def max2(x1, x2):
    return np.maximum(x1, x2)


def min2(x1, x2):
    return np.minimum(x1, x2)


def neg(x):
    return -x


def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal


def sqrt(df1):
    # square root operation
    output = np.sqrt(df1[df1 > 0])
    output = output.reindex(df1.index)
    return output


def square(df1):
    # x**2
    output = df1 ** 2
    return output



def sub(x1, x2):
    return np.subtract(x1, x2)


def ts_argmax(df1, d):
    # which moment ts_max(x, d) occurred on.
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmax(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_argmax(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return (d - 1) - output


def ts_argmin(df1, d):
    # which moment ts_min(x, d) occurred on.
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmin(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_argmin(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return (d - 1) - output


def ts_corr(df1, df2, d):
    # df1, df2过去d条数据的时序相关系数
    output = df1.rolling(d, min_periods=int(d / 2)).corr(df2)
    output.iloc[:d - 1] = np.nan
    return output


def ts_cov(df1, df2, d):
    # df1, df2过去d条数据的时序协方差
    output = df1.rolling(d, min_periods=int(d / 2)).cov(df2)
    output.iloc[:d - 1] = np.nan
    return output


def ts_decay_linear(df1, d, weight=None):
    # weighted moving average over the past d periods
    # default weight: linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if weight is None:
        weight = np.arange(d) + 1.0
    if isinstance(df1, pd.Series):
        output = pd.Series(np.nan, index=df1.index, name=df1.name)
        temp_y = rolling_window(df1, d)
        temp_x = np.tile(weight, (temp_y.shape[0], 1))
        flag = np.isnan(temp_x) | np.isnan(temp_y)
        flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
        flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
        temp_x[flag] = np.nan
        temp_y[flag] = np.nan
        output.iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    elif isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        for i in df1.columns:
            temp_y = rolling_window(df1[i], d)
            temp_x = np.tile(weight, (temp_y.shape[0], 1))
            flag = np.isnan(temp_x) | np.isnan(temp_y)
            flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
            flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
            temp_x[flag] = np.nan
            temp_y[flag] = np.nan
            output[i].iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    return output


def ts_delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def ts_delta(df1, d):
    # A_i - A_(i-d)
    output = df1.diff(periods=d)
    return output


def ts_max(df1, d):
    # moving time-series max for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_max(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output


def ts_median(df1, d):
    # moving time-series meidan for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_median(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_median(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return output


def ts_min(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_min(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return output


def ts_pct_change(df1, d):
    # (A_n - A_(n-d)) / A_(n-d)
    output = df1.pct_change(d, fill_method=None)
    return output


def ts_pred(df1, d, reg_x=None):
    """
    use rolling linear regression to predict value
    :param df1: dataframe or series
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe or series
        the predicted value of rolling linear regression
    """
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    reg_beta = ts_reg_beta(df1, d, reg_x)
    reg_alpha = ts_reg_alpha(df1, d, reg_x)
    reg_pred = (reg_beta * (d + 1) + reg_alpha).shift(1)
    return reg_pred


def ts_pred_delta(df1, d, reg_x=None):
    """
    the difference of the predicted value of rolling linear regression and real value
    :param df1: dataframe or series
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe or series
        the difference of the predicted value of rolling linear regression and real value
    """
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    reg_beta = ts_reg_beta(df1, d, reg_x)
    reg_alpha = ts_reg_alpha(df1, d, reg_x)
    reg_pred = (reg_beta * (d + 1) + reg_alpha).shift(1)
    reg_delta = df1 - reg_pred
    return reg_delta


def ts_rank(df1, d):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output


def ts_reg_alpha(df1, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到的截距项
    :param df1: dataframe or series
        regressand
    :param d: int
        rolling interval
    :param reg_x: series, np.ndarray or list
        regressor
    :return: dataframe or series
        intercept term of regression
    """
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
    if isinstance(df1, pd.DataFrame):
        intercept = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        for i in df1.columns:
            temp_y = rolling_window(df1[i], d)
            if reg_x is None:
                temp_x = np.tile(reg_x1, (temp_y.shape[0], 1))
            else:
                temp_x = rolling_window(reg_x, d)
            flag = np.isnan(temp_x) | np.isnan(temp_y)
            flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
            flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
            temp_x[flag] = np.nan
            temp_y[flag] = np.nan
            y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
            x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
            intercept[i].iloc[d - 1:] = (np.nanmean(temp_y, axis=1) - (y / x) * np.nanmean(temp_x, axis=1)) * flag1
    elif isinstance(df1, pd.Series):
        intercept = pd.Series(np.nan, index=df1.index, name=df1.name)
        temp_y = rolling_window(df1, d)
        if reg_x is None:
            temp_x = np.tile(reg_x1, (temp_y.shape[0], 1))
        else:
            temp_x = rolling_window(reg_x, d)
        flag = np.isnan(temp_x) | np.isnan(temp_y)
        flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
        flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
        temp_x[flag] = np.nan
        temp_y[flag] = np.nan
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        intercept.iloc[d - 1:] = (np.nanmean(temp_y, axis=1) - (y / x) * np.nanmean(temp_x, axis=1)) * flag1
    return intercept


def ts_reg_beta(df1, d, reg_x=None):
    # 过去d期A对reg_x或者1:d回归的回归系数
    # 默认自变量：1,2,...,d
    # return: reg_beta and reg_residual
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
    if isinstance(df1, pd.DataFrame):
        beta = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        for i in df1.columns:
            temp_y = rolling_window(df1[i], d)
            if reg_x is None:
                temp_x = np.tile(reg_x1, (temp_y.shape[0], 1))
            else:
                temp_x = rolling_window(reg_x, d)
            flag = np.isnan(temp_x) | np.isnan(temp_y)
            flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
            flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
            temp_x[flag] = np.nan
            temp_y[flag] = np.nan
            y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
            x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
            beta[i].iloc[d - 1:] = (y / x) * flag1
    elif isinstance(df1, pd.Series):
        beta = pd.Series(np.nan, index=df1.index, name=df1.name)
        temp_y = rolling_window(df1, d)
        if reg_x is None:
            temp_x = np.tile(reg_x1, (temp_y.shape[0], 1))
        else:
            temp_x = rolling_window(reg_x, d)
        flag = np.isnan(temp_x) | np.isnan(temp_y)
        flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
        flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
        temp_x[flag] = np.nan
        temp_y[flag] = np.nan
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        beta.iloc[d - 1:] = (y / x) * flag1
    return beta


def ts_reg_residual(df1, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到的截距项
    :param df1: dataframe or series
        regressand
    :param d: int
        rolling interval
    :param reg_x: series, np.ndarray or list
        regressor
    :return: dataframe or series
        residual term of regression
    """
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
    if isinstance(df1, pd.DataFrame):
        residual = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        for i in df1.columns:
            temp_y = rolling_window(df1[i], d)
            if reg_x is None:
                temp_x = np.tile(reg_x1, (temp_y.shape[0], 1))
            else:
                temp_x = rolling_window(reg_x, d)
            flag = np.isnan(temp_x) | np.isnan(temp_y)
            flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
            flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
            temp_x[flag] = np.nan
            temp_y[flag] = np.nan
            y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
            x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
            beta = y / x
            intercept = np.nanmean(temp_y, axis=1) - (y / x) * np.nanmean(temp_x, axis=1)
            residual[i].iloc[d - 1:] = (temp_y[:, -1] - beta * temp_x[:, -1] - intercept) * flag1
    elif isinstance(df1, pd.Series):
        residual = pd.Series(np.nan, index=df1.index, name=df1.name)
        temp_y = rolling_window(df1, d)
        if reg_x is None:
            temp_x = np.tile(reg_x1, (temp_y.shape[0], 1))
        else:
            temp_x = rolling_window(reg_x, d)
        flag = np.isnan(temp_x) | np.isnan(temp_y)
        flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
        flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
        temp_x[flag] = np.nan
        temp_y[flag] = np.nan
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        beta = y / x
        intercept = np.nanmean(temp_y, axis=1) - (y / x) * np.nanmean(temp_x, axis=1)
        residual.iloc[d - 1:] = (temp_y[:, -1] - beta * temp_x[:, -1] - intercept) * flag1
    return residual


def ts_skew(df1, d):
    # moving time-series skew over the past d periods
    output = df1.rolling(d, min_periods=int(d / 2)).skew()
    return output


def ts_sma(df1, alpha):
    # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output




def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output


def ts_sum(df1, d):
    # moving time-series average for the past d periods
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_sum(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_sum(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output


def ts_truncated_ema(df1, d, alpha):
    # truncated ema
    assert isinstance(df1, pd.Series), 'the data structure of input is illegal, must be series'
    assert 0 < alpha <1
    # df1_copy = df1.copy()
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    output = pd.Series(np.nan, index=df1.index, name=df1.name)
    temp_y = rolling_window(df1, d)
    temp_x = np.tile(weight, (temp_y.shape[0], 1))
    flag = np.isnan(temp_x) | np.isnan(temp_y)
    flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
    flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
    temp_x[flag] = np.nan
    temp_y[flag] = np.nan
    output.iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    return output
    
def ts_truncated_ema_span(df1, d, span):
    # truncated ema
    assert isinstance(df1, pd.Series), 'the data structure of input is illegal, must be series'
    alpha = 2 / (span + 1)
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    output = pd.Series(np.nan, index=df1.index, name=df1.name)
    temp_y = rolling_window(df1, d)
    temp_x = np.tile(weight, (temp_y.shape[0], 1))
    flag = np.isnan(temp_x) | np.isnan(temp_y)
    flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
    flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
    temp_x[flag] = np.nan
    temp_y[flag] = np.nan
    output.iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    return output