import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import itertools
import multifactor.utility.dt as udt


ticker = 'IC.CFE'


a = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/cfg_hf_data/%s_cfg_hf_new_161130_200101_h5.pkl' % ticker[:2])
b = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/cfg_hf_data/%s_cfg_hf_2020.pkl' % ticker[:2])
a = a.append(b)
a = a.sort_index()

a = a.loc['20161201':'20200930']
outdf = a

suffix_dict = {'IC.CFE':'_500','IF.CFE':'_300'}

outdf = outdf.reset_index().set_index(['dt','Ticker']).sort_index()
outdf2 = outdf.unstack(level = 1)
out_dict = {}
for col in outdf2.columns.get_level_values(0).unique():
    a = outdf2[col]
    idx = a.index
    a = a.loc[~((idx.hour==14)&(idx.minute==57))]
    out_dict[col+suffix_dict[ticker]] = a

import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
outsample_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/'
save_pickle(out_dict, os.path.join(outsample_path, '%s_cfg_hf_data_insample.pkl' % ticker[:2]))