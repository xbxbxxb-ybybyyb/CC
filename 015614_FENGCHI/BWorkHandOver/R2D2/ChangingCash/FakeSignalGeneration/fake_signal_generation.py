# @Time : 2022/4/8 10:46
# @Author : Zhichen Lu
# @File : fake_signal_generation.py
import numpy as np
import pandas as pd
import os
from dataApi.tradeDate import get_date_range
import itertools
import random
label_path = '/data/group/800442/800319/Timing/FixFactor/FixFactor/label/'
# label_list = os.listdir(label_path)
date_list = get_date_range(20140601,20211231)
def generate_fake_signal(presision,signal_ratio,real_signal):
# presision = 0.6
    real_pos = real_signal[real_signal==2].index.tolist()
    real_neg = real_signal[real_signal==0].index.tolist()
    pos_neg_num = int(real_signal.shape[0]*signal_ratio)
    print(len(real_pos),len(real_neg))
    correct_pos = random.sample(real_pos,int(presision*pos_neg_num))
    wrong_pos = random.sample(real_neg,int((1-presision)*pos_neg_num))
    real_pos,real_neg = set(real_pos) - set(correct_pos),set(real_neg) - set(wrong_pos)
    print(len(real_pos),len(real_neg))
    correct_neg = random.sample(real_neg,int(presision*pos_neg_num))
    wrong_neg = random.sample(real_pos,int((1-presision)*pos_neg_num))
    real_pos,real_neg = set(real_pos) - set(wrong_neg),set(real_neg) - set(correct_neg)
    print(len(real_pos),len(real_neg))

    signal = pd.Series(1,index = real_signal.index)
    signal.loc[correct_pos+wrong_pos] = 2
    signal.loc[correct_neg+wrong_neg] = 0
    return signal

if __name__ == '__main__':
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    wf1d1000 = np.load(f'{label_path}wf1d1000.npy')
    wf1d1000 = pd.Series(wf1d1000.flatten(), index=index)
    rank = wf1d1000.rank(pct=True)
    r_signal = wf1d1000.apply(lambda x : x>0)* 2
    out_dir = '/data/group/800442/800319/MarketTiming/fake_signal/'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    signal = pd.read_pickle('/data/group/800442/800319/Timing/BackTest/Signal/XGB300.pkl')
    signal = signal.stack()
    signal = signal[signal.columns[0]]+1
    pos_pred = signal[signal==2]
    neg_pred = signal[signal==0]
    # for p in [0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9]:
    #     fake_signal = generate_fake_signal(presision=p,real_signal=r_signal)
    #     pd.to_pickle(fake_signal,f'{out_dir}/fake_{p:.2f}.pkl')
    #     # signal = pd.Series(pd.read_pickle('/data/group/800442/800319/Timing/BackTest/Signal/XGB300.pkl'))
    #     pos_pred = fake_signal[fake_signal==2]
    #     neg_pred = fake_signal[fake_signal==0]
    print((r_signal.loc[pos_pred.index]==2).sum()/pos_pred.shape[0],\
        (r_signal.loc[neg_pred.index]==0).sum()/neg_pred.shape[0])



