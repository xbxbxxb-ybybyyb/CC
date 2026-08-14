# @Time : 2022/5/9 8:33
# @Author : Zhichen Lu
# @File : res_analysis.py

import pandas as pd
import numpy as np
import os
base_dir = '/data/user/015664/ModelFile/lstm_fixFIXSEED/'
out_dir = f'{base_dir}/ParamSeeking/'

file_list = sorted(os.listdir(out_dir))

res_dict = {}
for each in file_list:
    temp = pd.read_pickle(f'{out_dir}{each}')
    loss_log = pd.DataFrame([list(map(lambda x :x.__float__(),x)) for x in temp['loss_log']],
                            columns='val_loss,val_mse,val_corr,val_sstd'.split(','))

    res_dict[each.replace(').pkl','').replace('Param(','')] = dict({x:temp[x] for x in [ 'loss','mse','corr','diff_sstd']},
                                                               **dict(loss_log[loss_log['val_loss']==loss_log['val_loss'].min()].iloc[0]))
    res_dict[each.replace(').pkl','').replace('Param(','')]['epoch'] = loss_log.shape[0]-15
res_df = pd.DataFrame(res_dict).T.sort_values('loss')
res_df.index = pd.MultiIndex.from_tuples([list(map(str,eval(x))) for x in res_df.index])
res_df = res_df.reset_index().rename(columns={'level_0':'recur_dim',
                                              'level_1':'recur_layers',
                                              'level_2':'full_conn_shape',
                                              'level_3':'dropout'})
res_df = res_df[res_df['epoch']>20]

import pandas as pd
import os

base_dir = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/TimeSeriesModel/LSTM_ic_dt_train100_test10_factor_num100/LSTM_ic_dt_train100_test10_factor_num100/'
file_list = os.listdir(base_dir)
corr_series = {}
res = []
for each in file_list:
    temp = pd.read_pickle(f'{base_dir}{each}')
    corr_series[each.replace('.pkl','')] = temp.corr().loc['prediction','actual_label']
    res.append(temp)
res = pd.concat(res)
corr_series = pd.Series(corr_series)
res.corr()



