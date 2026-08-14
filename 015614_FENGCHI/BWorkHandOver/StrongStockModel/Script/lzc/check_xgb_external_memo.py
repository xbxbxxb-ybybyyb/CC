# @Time : 2020/11/3 20:57
# @Author : Zhichen Lu
# @File : check_xgb_external_memo.py

import os

import numpy as np
from sklearn.datasets import make_regression
import xgboost as xgb

df_train = make_regression(n_samples=100000, n_features=100)
if os.path.exists('/data/user/015664/dummy_txt.train'):
    os.remove('/data/user/015664/dummy_txt.train')
np.savetxt('/data/user/015664/dummy_txt.train', np.hstack([df_train[1].reshape(-1,1), df_train[0]]), delimiter=',')

dtrain = xgb.DMatrix('/data/user/015664/dummy_txt.train?format=csv&label_column=0#dtrain.cache')

param = {'tree_method' : 'gpu_hist', 'subsample' : 0.2, 'sampling_method' : 'gradient_based'}

num_round = 5
bst = xgb.train(param, dtrain, num_round,verbose_eval=True)