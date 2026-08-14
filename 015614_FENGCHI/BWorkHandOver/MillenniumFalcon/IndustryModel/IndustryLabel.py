# @Time : 2021/10/11 11:13
# @Author : Zhichen Lu
# @File : IndustryLabel.py


import numpy as np
import pandas as pd
from CrossFT.basic.crossUtils import *
from CrossFT.basic.crossOperators import *
from online_conf import local_config_path
import itertools
from dataApi.LoadingTool import trans_df2arr
from tqdm import tqdm
from multiprocessing import Pool

def get_group_val(indicator, group, func):
    '''
    indicator:个股指标，用于合成组别指标
    group:个股分组情况，shape要和indicator相同
    func：组内计算方法, nansum, nanmean,nanmax,nanmin,nanmedian,nanstd,nanvar,nanquantile,自定义
    return: 返回的是个股横截面指标，index=time, columns= stock_pool
    '''
    groups = np.unique(group[np.isfinite(group)])
    shape = indicator.shape
    res = []
    for g in groups:
        val = group == g
        if len(shape) == 2:
            res.append(func(np.where(val, indicator, np.nan), axis=len(shape) - 1)[:,None])
        elif len(shape) == 3:
            res.append(func(np.where(val, indicator, np.nan), axis=len(shape) - 1)[:,:,None])
    return np.concatenate(tuple(res),axis=-1),groups.astype(int).tolist()



FACTOR_PATH = '/data/group/800080/FactorFactory/PICKLE_DAY/'
_date_list = get_date_range(20140701, 20210531)
_code_list = np.load('/arch1/group/800442/800319/AAcross/basic/code_list.npy').tolist()
out_path = '/data/group/800442/800319/HFfactor/DailySW2/'
factor_list = [x.replace('.pkl','') for x in os.listdir(FACTOR_PATH)]






###########






