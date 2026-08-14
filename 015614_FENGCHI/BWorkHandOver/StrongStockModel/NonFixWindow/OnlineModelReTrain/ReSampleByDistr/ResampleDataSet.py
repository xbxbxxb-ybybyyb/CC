# @Time : 2022/6/1 8:53
# @Author : Zhichen Lu
# @File : ResampleDataSet.py

import pandas as pd
import numpy as np
import random
import scipy.stats as scs
import matplotlib.pyplot as plt
from tqdm import tqdm

def Gaussian(x,m,v):
    return np.exp(-(x-m)**2/(2 * v**2))/(2*np.pi)**0.5/v

def get_distr_prob(m,v,clip_range=5):
    target_list = [round(-clip_range+(x*0.01)*(2*clip_range),3)*v for x in range(101)]
    prob_dense = pd.DataFrame({'prob_dense':[Gaussian(x,m,v) for x in target_list],
                               'val':target_list},index=target_list)
    prob_dense['sub_prob'] = prob_dense['val'].diff()*prob_dense['prob_dense'].rolling(2).mean()
    left = 1 - prob_dense['sub_prob'].sum()
    prob_dense.loc[target_list[0],'sub_prob'] = left/2
    prob_dense['cum_prob'] = prob_dense['sub_prob'].cumsum()
    prob_dense['start'] = [-np.inf] + prob_dense.index.tolist()[:-1]
    prob_dense['end'] = prob_dense.index.tolist()
    # prob_dense['sub_prob'].sum() +left/2
    return prob_dense

def get_gaussian_dataset(label,val_ratio,clip_range=5):
    mean,std = label.mean(),label.std()
    prob_dense =  get_distr_prob(mean,std,clip_range)
    period_count = []
    period_info = {}
    for start,end,prob in tqdm(list(zip(*[prob_dense[x] for x in [ 'start', 'end','sub_prob']]))):
        # print(start,end,prob)
        period_info[(start,end)] = label.apply(lambda x : x>start and x<=end)
        period_count.append(period_info[(start,end)].sum())
    prob_dense['period_count'] = period_count
    prob_dense['sampled_total'] = (prob_dense['period_count']/prob_dense['sub_prob']).apply(int)
    sample_num = (prob_dense['sub_prob'] * prob_dense['sampled_total'].min()).apply(int)

    idx = pd.Series(list(range(label.shape[0])),index=label.index)
    target = []
    val_target = []
    for start,end,num in tqdm(zip(*[prob_dense[x] for x in [ 'start', 'end']],sample_num)):
        if num==0:
            continue
        temp = idx[period_info[(start,end)]].sample(num,random_state=0)#.tolist()
        temp_val = temp.sample(int(num*val_ratio),random_state=0)
        target += temp.tolist()
        val_target += temp_val.tolist()
    return sorted(list(set(target)-set(val_target))),sorted(val_target)

if __name__ == '__main__':
    X_train,y_train,X_test,y_test = pd.read_pickle('/data/user/015664/temp/dataset20180809.pkl')
    idx_train,idx_val = get_gaussian_dataset(y_train['actual_label'],0.05)

