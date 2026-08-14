import numpy as np
from .crossUtils import sameshape

def cross_sum(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nansum(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nansum(x, axis)


def cross_mean(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nanmean(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nanmean(x, axis)

def cross_max(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nanmax(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nanmax(x, axis)


def cross_min(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nanmin(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nanmin(x, axis)

def cross_median(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nanmedian(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nanmedian(x, axis)

def cross_std(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nanstd(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nanstd(x, axis)

def cross_var(x, axis, group=None, **kwargs):
    if isinstance(group, np.ndarray):
        return np.nanvar(np.where(group, x, np.nan), axis=axis)
    else:
        return np.nanvar(x, axis)

def cross_topnum(x, axis, group, y, thred=0.1, dfunc=np.nanmean):
    '''
    :param x:
    :param axis:
    :param y: 参考指标, 选取y越大的前几位
    :param thred: 参考指标筛选阈值,前n%个
    :return:
    '''
    groupy = np.where(group, sameshape(x,y), np.nan)
    n = (np.sum(np.isfinite(groupy), axis=axis, keepdims=True) * thred).astype(int)
    yrank = np.argsort(np.argsort(-groupy, axis=axis), axis=axis)  # [3,1,2]-->[0,2,1]
    groupx = np.where(yrank <= n, x, np.nan)
    return dfunc(groupx, axis=axis)

def cross_topval(x, axis, group, y, thred=0.3, dfunc=np.nanmean):
    groupy = np.where(group, sameshape(x, y), np.nan)
    groupy/= np.nansum(groupy, axis=axis, keepdims=True) # 变成百分百占比
    yrank = np.argsort(np.argsort(-groupy, axis=axis), axis=axis)  # [3,1,2]-->[0,2,1]
    ythred = np.fmax(1,np.nansum((-np.cumsum(np.sort(-groupy, axis=axis),axis=axis))<=thred,axis=axis, keepdims=True))
    groupx = np.where(yrank<=ythred, x, np.nan)
    return dfunc(groupx, axis=axis)
