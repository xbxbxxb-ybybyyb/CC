# @Time : 2021/7/29 15:14
# @Author : Zhichen Lu
# @File : HyperParamChanging.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from online_conf import holding_info_path,hyper_param_path,code_list_path
import pandas as pd
import numpy as np
import os,shutil
date = 20220331

holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
holding = pd.Series(holding).drop('cash')
print(f'{holding_info_path}{date}.pkl')
if not os.path.exists(f'{hyper_param_path}mean{date}_backup.pkl'):
    shutil.copy(f'{hyper_param_path}mean{date}.pkl',f'{hyper_param_path}mean{date}_backup.pkl')
if not os.path.exists(f'{hyper_param_path}std{date}_backup.pkl'):
    shutil.copy(f'{hyper_param_path}std{date}.pkl',f'{hyper_param_path}std{date}_backup.pkl')

mean = pd.read_pickle(f'{hyper_param_path}mean{date}.pkl')
std = pd.read_pickle(f'{hyper_param_path}std{date}.pkl')

mean[holding.index] = np.nan
std[holding.index] = np.nan
print(len(holding))
pd.to_pickle(mean,f'{hyper_param_path}mean{date}.pkl')
pd.to_pickle(std,f'{hyper_param_path}std{date}.pkl')

# code_list = pd.read_pickle(f'{code_list_path}{date}.pkl')
# code_list.remove('300705.SZ')
# pd.to_pickle(code_list,f'{code_list_path}{date}.pkl')





