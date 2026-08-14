# @Time : 2022/4/22 14:46
# @Author : Zhichen Lu
# @File : fix_analysis.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading/StockSelection', '/data/user/015664/TriggeredTrading'])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dataApi.tradeDate import get_date_range
from dataApi.getData import trans_windcode2int
from dataApi.stockList import get_stock_list
import itertools


def _load_pickle_frame(file_name, date_list, code_list):

    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'

    df_dic = {}
    for time in bar_list:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.loc[date_list[0]: date_list[-1]]
        df = df.reindex(columns=code_list)
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x].values for x in bar_list)].transpose(1, 0, 2)

availabel_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
date_list = get_date_range(20170101,20171231)
code_list = get_stock_list(20170101)

stk = 1

for f_name in availabel_factor_list:
    factor = _load_pickle_frame(f_name,date_list,code_list)
    factor = factor.reshape(factor.shape[0]*factor.shape[1],factor.shape[2])
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list,bar_list)))
    factor = pd.DataFrame(factor,index=index,columns=code_list)
    factor[stk].plot()
    plt.title(f'{stk}')
    plt.show()
    plt.hist(factor[stk],bins=40)
    plt.show()