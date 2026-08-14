import numpy as np
import warnings
warnings.filterwarnings("ignore")
import sys
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/016385')
sys.path.append('/data/user/016385/test/digger_factor')
from sklearn import metrics
from sklearn.cluster import KMeans,DBSCAN,SpectralClustering

# 百分位分组
def percent_group(indicator, groupnum):
    '''
    :param indicator: np.array, index:datetime, col:stockpool, np.array:2d or 3d
    :param groupnum: int
    :return: np.array, index:datetime, col:stockpool
    '''
    res = np.full(indicator.shape, np.nan)
    shape = indicator.shape
    if groupnum <= shape[-1]:
        quantile = np.nanquantile(indicator, np.arange(1, groupnum) / groupnum, axis=len(shape) - 1, keepdims=True)
        for i in range(groupnum):
            if i == 0:
                group = indicator <= quantile[i]
            elif i == groupnum - 1:
                group = indicator > quantile[i - 1]
            else:
                group = (indicator > quantile[i - 1]) & (indicator <= quantile[i])
            res[group] = i
    else:
        res = np.argsort(np.argsort(indicator, axis=len(shape) - 1), axis=len(shape) - 1)
        res = np.where(np.isfinite(indicator), res, np.nan)
    return res

# 等分分组
def samenum_group(indicator, groupnum):
    '''
        :param indicator: np.array, index:datetime, col:stockpool, np.array:2d or 3d
        :param groupnum: int
        :return: np.array, index:datetime, col:stockpool
        '''
    shape = indicator.shape
    valid = np.isfinite(indicator)
    # 这个地方的计算是为了去除np.nan的影响
    num = valid.sum(axis=len(shape) - 1, keepdims=True)
    num = num // groupnum + (num % groupnum >= np.floor(groupnum * 0.5))
    num = np.where(num == 0, 1, num)
    res = np.argsort(np.argsort(indicator, axis=len(shape) - 1), axis=len(shape) - 1) // num
    res = np.where(res == groupnum, groupnum - 1, res)
    res = np.where(valid, res, np.nan)
    return res

def get_scores(x, y_pred):
    '''越大越好'''
    return metrics.calinski_harabaz_score(x, y_pred)

def Kmeans_group(indicator, groupnum):
    '''
    indicator:index-time,columns-stocks,且是二维数组,适用于凸数据集
    '''
    val = indicator.T
    group = KMeans(n_clusters=groupnum, random_state=9).fit_predict(val)
    return group

def DBSCAN_group(indicator, groupnum):
    '''
    indicator:index-time,columns-stocks
    不需要输入类别数K,可以发现任意形状的聚类簇，如果数据集是稠密的，并且数据集不是凸的，那么DBSCAN会比Kmeans聚类
    效果好的多
    这个还需要调参
    '''
    val = indicator.T
    group = DBSCAN(eps=0.1, min_samples=10, random_state=9).fit_predict(val)
    return group

def spectral_group(indicator, groupnum, gamma):
    '''
    indicator:index-time,columns-stocks,
    '''
    val = indicator.T
    y_pred = SpectralClustering(n_clusters=groupnum, gamma=gamma, random_state=9).fit_predict(val)
    return y_pred

def cluster(indicator, func, groupnum,**kwargs):
    '''
    :param indicator: 组因子
    :param func: Kmeans_group, DBSCAN_group, spectral_group
    :param groupnum: 自定义
    :param kwargs: func需要的值
    :return:
    '''
    res = np.apply_along_axis(func, 0, indicator)
    return res
