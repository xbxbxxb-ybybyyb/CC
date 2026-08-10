import numpy as np
import pandas as pd
import pickle
import bottleneck as bn
from joblib import Parallel, delayed


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.array(np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides))
    return rolling_table


def auto_corr(df1, nlags):
    # 计算df每列滞后nlags阶的自相关系数, 返回一个Series
    df_temp1 = df1.iloc[:(-nlags)]
    df_temp2 = df1.iloc[nlags:]
    df_temp2.index = df_temp1.index
    output = ((df_temp1 - df1.mean()) * (df_temp2 - df1.mean())).sum() / (df1.var() * (df1.shape[0] - 1))
    return output


def get_max_drawdown(ret_list, type='cumsum'):
    """
    calculate max drawdown, start date and end date of the max drawdown
    :param ret_list: array_like, one dimension
        yield curve or cumulative yield curve
    :param type: str
        可选cumsum或share，对应的输入分别是累计收益和分笔收益
    :return: float, datetime, datetime
        max_drawdown, max_drawdown_start_time, max_drawdown_end_time
    """
    assert isinstance(ret_list, pd.Series) or isinstance(ret_list, np.ndarray) or isinstance(ret_list, list)
    if isinstance(ret_list, np.ndarray):
        assert ret_list.shape[1] == 1
    if any([isinstance(ret_list, np.ndarray), isinstance(ret_list, list)]):
        ret_list = pd.Series(ret_list)
    if type == 'time_share':
        ret_list = ret_list.cumsum()
    ret_list1 = ret_list.expanding().max()
    ret_list2 = ret_list - ret_list1
    max_drawdown = ret_list2.min()
    if max_drawdown == 0:
        print('no drawdown')
        return
    else:
        max_drawdown_end_time = ret_list2.argmin()
        max_drawdown_start_time = ret_list[:ret_list2.argmin()].argmax()
        return max_drawdown, max_drawdown_start_time, max_drawdown_end_time


def get_low_corr_factors(factor_df, corr_threshold):
    """
    对输入的因子值矩阵(index: dt, columns: factor_name)根据相关性阈值筛选因子
    :param factor_df: dataframe
        因子值拼接而成的矩阵，每一列是一个单因子，其中排序顺序是某个指标，即越往左的因子该指标越高
    :param corr_threshold: 因子相关性阈值
    :return: dataframe
        去除了高相关性因子后的因子值矩阵
    """
    components = list(np.arange(factor_df.shape[1]))
    indices = list(np.arange(factor_df.shape[1]))

    factors_corr = factor_df.corr().values
    np.fill_diagonal(factors_corr, 0.)  # 把相关性矩阵的对角线元素替换为0

    while factors_corr.max() > corr_threshold:
        most_correlated = np.unravel_index(np.argmax(factors_corr), factors_corr.shape)
        worst = max(most_correlated)  # 由于原始因子值矩阵越往左的因子指标值越高，因此取max可以从相关性过高的两个因子中删除指标值较低的那个
        components.pop(worst)
        indices.remove(worst)
        factors_corr = factors_corr[:, indices][indices, :]
        indices = list(range(len(components)))
    factor_df_low_corr = factor_df.iloc[:, components]

    return factor_df_low_corr


def ic_calc(df_factor, return_data):
    df_final = df_factor.corrwith(return_data)
    return df_final


def multi_processing_joblib(df, func, n_jobs=12, **kwargs):
    """
    cross-section multi-process for the dataframe
    :param df: dataframe
        the raw data
    :param func:
        the function acting on dataframe
    :param n_jobs: int
        the number of cores used, if n_jobs=-1, all cores will be used
    :param kwargs:
        the parameters in the param func.
    :return: dataframe
        the data after the use of function
    """
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal
        elif method == 'bn_move_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bn.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bn.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            else:
                signal = bn.move_rank(sig, window=window, min_count=int(window / 2), axis=0)
            return signal


def save_pickle(save_dict, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict, input, protocol=pickle.HIGHEST_PROTOCOL)
    return


def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def replace_inf(data, x=np.nan):
    """
    replace inf to a predefined number for the input data
    :param data: dataframe, series or np.ndarray
        the data which contains inf
    :param x: int, float or np.nan, optional (default=np.nan)
        the value used to replace inf
    :return: input data whose inf has been replaced
    """
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal'
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
        'the data structure of input is illegal'
    data = data.copy()
    data[abs(data) < 1e-8] = x
    return data


class ActivationFunction(object):
    @staticmethod
    def sigmoid(df1):
        output = 1 / (1 + np.exp(-df1))
        return output

    @staticmethod
    def tanh(df1):
        output = (np.exp(df1) - np.exp(-df1)) / (np.exp(df1) + np.exp(-df1))
        return output

    @staticmethod
    def relu(df1):
        output = np.maximum(df1, 0)
        return output

    @staticmethod
    def leaky_relu(df1, a):
        output = np.maximum(a * df1, df1)
        return output

    @staticmethod
    def exponential_linear_units(df1, a):
        def f(x, a1):
            if x > 0:
                return x
            else:
                return a1 * (np.exp(x) - 1)

        output = df1.applymap(lambda x: f(x, a))
        return output


def multiple_linear_regression(y, X, d):
    """
    Multiple linear regression
    :param y: array_like, one dimension
        regressand
    :param X: array_like, two dimension
        regressor
    :param d: int
        rolling interval
    :return: list
        regression coefficients
    """
    pass
