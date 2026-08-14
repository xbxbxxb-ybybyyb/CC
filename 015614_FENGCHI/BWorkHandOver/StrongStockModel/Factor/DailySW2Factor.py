# @Time : 2021/9/1 14:15
# @Author : Zhichen Lu
# @File : DailySW2Factor.py
import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading'])


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

def out_factor(factor_name):
    factor = pd.read_pickle(f'{FACTOR_PATH}{factor_name}.pkl')
    factor.index = factor.index.astype(int)
    factor.columns = factor.columns.map(trans_windcode2int)
    factor = factor.loc[_date_list,_code_list].values[:,None,:]
    # group_factor = load_material('sw2', _date_list[0], _date_list[-1],freq='daily', address='/arch1/group/800442/800319/AAcross/basic/groups/')

    group_factor = get_daily_1factor('SW2').shift(1)
    group_factor = group_factor.loc[_date_list,_code_list].values[:,None,:]

    sw_mean,group_list1 = get_group_val(factor,group_factor,cross_mean)#[:,0,:]
    sw_std,group_list2 = get_group_val(factor,group_factor,cross_std)#[:,0,:]
    if group_list1!=group_list2:
        print('group list not equal')
        raise Exception('gorup list not euqal')

    sw_mean = sw_mean[:,0,:]
    sw_std = sw_std[:,0,:]

    sw_sharpe = sw_mean/sw_std

    pd.DataFrame(sw_mean,index=_date_list,columns=group_list1).to_pickle(f'{out_path}mean/{factor_name}.pkl')
    pd.DataFrame(sw_std,index=_date_list,columns=group_list2).to_pickle(f'{out_path}std/{factor_name}.pkl')
    pd.DataFrame(sw_sharpe,index=_date_list,columns=group_list1).to_pickle(f'{out_path}zscore/{factor_name}.pkl')
    print(factor_name,'done')

# out_factor(factor_list[0])

def main(n):
    bar = tqdm(total=len(factor_list))

    def update(*para):
        bar.update()
        if bar.last_print_n >= bar.total:
            bar.close()

    pool = Pool(n)
    for fname in factor_list:
        if os.path.exists(f'{out_path}zscore/{fname}.pkl'):
            continue
        pool.apply_async(out_factor, (fname,), callback=update)

    pool.close()
    pool.join()

main(36)