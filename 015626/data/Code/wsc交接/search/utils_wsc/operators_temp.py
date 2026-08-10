"""存放一些临时的算子，在经过测试后移至operators_wsc"""
import numpy as np
from scipy.stats import norm
from .operators_wsc import *
from .help_functions_wsc import replace_zero, rolling_window_upgrade, type_convertor

__all__ = ['auto_corr', 'up_outlier_ratio', 'down_outlier_ratio', 'outlier_ratio', 'coefficient_of_variation',
           'long_short_ma_ratio', 'up_down_ratio', 'cross_hub_num', 'distance_to_variation', 'ts_midpoint',
           'ts_maxmin_distance', 'ts_distance_from_mean', 'ts_ratio_from_mean']


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


def distance_to_variation(data, d, need_abs=False):
    # 两个点之间的直线距离和走过位移之比
    data_distance = ts_delta(data, d)
    data_journey = ts_sum(abs(ts_delta(data, 1)), d)
    if need_abs:
        data_distance = abs(data_distance)
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


@type_convertor
def ts_convolution(data1, data2, d, convolution_type='sum'):
    # 滚动卷积：\sum(x_i * y_{n-i})
    assert convolution_type in ['sum', 'mean']
    try:
        data1_expanding = rolling_window_upgrade(data1.values, d)
        data2_expanding = rolling_window_upgrade(data2.values, d)
    except AttributeError:
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
    data2_expanding_flip = np.flip(data2_expanding, axis=-1)
    if convolution_type == 'sum':
        output_need = np.nansum(data1_expanding * data2_expanding_flip, axis=-1)
    else:
        output_need = np.nanmean(data1_expanding * data2_expanding_flip, axis=-1)
    output = np.full(data1.shape, np.nan)
    output[d - 1:] = output_need
    return output


@type_convertor
def ts_divergence_to_snd_l2_cdf(data, d):
    # 过去n期data作标准化后得到累计分布函数F(x)，考察该分布与标准正态分布的欧式距离（L2范数）
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    data_expanding_norm = (data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)) / np.nanstd(
        data_expanding, axis=-1, keepdims=True)
    data_expanding_norm_snd_cdf = norm.cdf(data_expanding_norm)
    data_expanding_norm_snd_cdf_sorted = np.sort(data_expanding_norm_snd_cdf, axis=-1)
    output_need = np.nansum((data_expanding_norm_snd_cdf_sorted - np.arange(1, d + 1) / d) ** 2, axis=-1)
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output


@type_convertor
def ts_divergence_to_snd_l2_ppf(data, d):
    # 与ts_divergence_to_snd_l2_cdf互为反函数
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    data_expanding_norm = (data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)) / np.nanstd(
        data_expanding, axis=-1, keepdims=True)
    data_expanding_norm_sorted = np.sort(data_expanding_norm, axis=-1)
    snd_ppf = norm.ppf(np.arange(1, d + 1) / (d + 1))
    output_need = np.nansum((data_expanding_norm_sorted - snd_ppf) ** 2, axis=-1)
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output
