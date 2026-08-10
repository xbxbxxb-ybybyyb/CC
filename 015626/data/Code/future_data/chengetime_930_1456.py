import pandas as pd
import numpy as np
import os
from multifactor.IO import IO

import pickle

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
    
rootpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/'
targetpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/INSAMPLE_930_1456/'

for x in os.listdir(rootpath):
    if not x.endswith('pkl'):
        continue
    print(x)
    temp = pd.read_pickle(os.path.join(rootpath, x))
    tempdict = {}
    for k in temp.keys():
        a = temp[k]
        idx = a.index
        a = a.loc[~((idx.hour==14)&(idx.minute==57))]
        tempdict[k] = a
    save_pickle(tempdict, os.path.join(targetpath, x))