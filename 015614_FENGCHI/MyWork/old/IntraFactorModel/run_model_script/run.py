# @Time : 2020/5/25 9:10
# @Author : Zhichen Lu
# @File : run.py

import pandas as pd

from HyperoptApi import hyperopt_wrapper
from dataApi.stockList import clean_stock_list
from conf.model_param_config import *



def run(model_type, metrics_type, stk_list, label):
    if model_type not in model_choice:
        raise Exception('Undefined model type')
    model = model_choice[model_type][0]()

    def objective(params):
        metrics_list = []
        print(params)
        for stk in stk_list:
            _, metrics_result = model.training_methodology(stk, label, params)
            print(params, metrics_result)
            metrics_list.append(metrics_result[metrics_type])
        return np.nanmean(metrics_list)

    best = hyperopt_wrapper(objective, model_choice[model_type][1], max_evals=100)
    return best


pool = clean_stock_list('HS300')
isin = pool.sum(axis=0)
pool = pool[isin[isin > 0].index]

best = run('mlp', 'acc', pool.columns.tolist(), 'rise_down_zero')
pd.to_pickle(best, '/data/group/800319/junkClassification/best.pkl')
