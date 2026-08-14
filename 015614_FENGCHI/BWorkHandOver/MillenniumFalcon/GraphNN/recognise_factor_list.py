# @Time : 2021/12/1 14:31
# @Author : Zhichen Lu
# @File : recognise_factor_list.py

import pandas as pd
import os
import numpy as np
import itertools
from tqdm import tqdm
import configparser
from dataApi.tradeDate import get_date_range

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def get_res_val(res):
    best_valid_pred, best_valid_gt, best_valid_mask, \
    best_test_pred, best_test_gt, best_test_mask = res['res']
    date_list, code_list, time_list = res['idx']
    nolimit = res['nolimit']
    test_nolimit = nolimit[:, 200*7:].T
    val_nolimit = nolimit[:, 189*7: 200*7].T
    val_date_list = [date_list[:200][i] for i in val_idx]

    index = list(itertools.product(date_list, time_list))
    index_val = pd.MultiIndex.from_tuples(index[189*7: 200*7])
    index_test = pd.MultiIndex.from_tuples(index[200*7:])

    val_label, val_pred = pd.DataFrame(best_valid_gt.T, index=index_val, columns=code_list), pd.DataFrame(best_valid_pred.T, index=index_val, columns=code_list)
    test_label, test_pred = pd.DataFrame(best_test_gt.T, index=index_test, columns=code_list), pd.DataFrame(best_test_pred.T, index=index_test, columns=code_list)
    test_nolimit, val_nolimit = pd.DataFrame(test_nolimit, index=index_test, columns=code_list), pd.DataFrame(val_nolimit, index=index_val, columns=code_list)

    val_label, val_pred, test_label, test_pred = val_label[val_nolimit], val_pred[val_nolimit], test_label[test_nolimit], test_pred[test_nolimit]
    val_label, val_pred = val_label.loc[val_date_list], val_pred.loc[val_date_list]

    val = pd.DataFrame({'actual_label': val_label.stack(dropna=False), 'prediction': val_pred.stack(dropna=False)})
    test = pd.DataFrame({'actual_label': test_label.stack(dropna=False), 'prediction': test_pred.stack(dropna=False)})
    return test.dropna(),val.dropna()

res_path = '/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix/'
out_path = '/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix_ic_c'
for each in ['','_val_pred']:
    if not os.path.exists(f'{out_path}{each}'):
        os.mkdir(f'{out_path}{each}')

file_list = sorted(os.listdir(res_path))
val_idx = [-3,-5,-7,-9,-11]
for each in tqdm(file_list):
    res_ = pd.read_pickle(f'{res_path}{each}')
    pred,val_pred = get_res_val(res_)
    pd.to_pickle(pred,f'{out_path}/{each}')
    pd.to_pickle(val_pred,f'{out_path}_val_pred/{each}')





