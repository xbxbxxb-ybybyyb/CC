import pandas as pd
import numpy as np
import pickle
import os

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict

def pd_writer(sig, savepath):
    sig_name = sig.columns[0]
    file_name = os.path.join(savepath, sig_name + '.h5')
    if os.path.exists(file_name):
        #sigold = IO.read_data(alt = file_name)
        sigold = pd.read_hdf(file_name)
        sigold = sigold[~sigold.index.isin(sig.index)]
        signew = pd.concat([sigold,sig],axis=0).sort_index()
    else:
        signew = sig
    signew.to_hdf(file_name,key=sig_name)

def sig_trans(sig, longin = 0.5, longout = 0.4, drawdownout = -0.2):
    if len(sig) == 0:
        return 0
    sig.iloc[0] = 0
    assert longin >= longout
    tradesignal = 0
    pos = 0
    sighigh = 0
    for i in range(1,len(sig)):
        if pos == 0:
            if (sig.iloc[i] > longin) & (sig.iloc[i-1]<= longin):
                pos = 1
                tradesignal = 1
                sighigh = sig.iloc[i]
        elif pos == 1:
            if sighigh < sig.iloc[i]:
                sighigh = sig.iloc[i]
            if ((sig.iloc[i] <= longout) & (sig.iloc[i-1]>longout)):
                pos = 0
                tradesignal = 0
                sighigh = 0
            if sig.iloc[i] - sighigh < drawdownout:
                tradesignal = 0
    return tradesignal

def max_drawdown_ts(cum_return_ps, interest_type='SIMPLE', return_drawdown_period=False):
    assert isinstance(cum_return_ps, pd.Series)
    cum_return_ps = cum_return_ps.fillna(0)
    cum_max = np.maximum.accumulate(cum_return_ps)
    if interest_type == 'SIMPLE':
        mdd_ts = cum_return_ps - cum_max
    else:
        mdd_ts = (cum_return_ps - cum_max) / cum_max
    mdd_idx = mdd_ts.idxmin()
    mdd_max_level = cum_max.loc[mdd_idx]
    _ = cum_return_ps.loc[:mdd_idx]
    try:
        mdd_begin_idx = _[_ == mdd_max_level].index[-1]
    except IndexError:
        mdd_begin_idx = pd.NaT
    _ = cum_return_ps.loc[mdd_idx:]
    try:
        mdd_end_idx = _[_ >= mdd_max_level].index[0]
    except IndexError:
        mdd_end_idx = pd.NaT
    if return_drawdown_period:
        return mdd_ts, (mdd_begin_idx, mdd_end_idx)
    else:
        return mdd_ts