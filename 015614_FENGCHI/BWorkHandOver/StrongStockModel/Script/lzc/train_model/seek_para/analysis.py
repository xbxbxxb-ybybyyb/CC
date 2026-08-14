# @Time : 2020/12/16 8:48
# @Author : Zhichen Lu
# @File : analysis.py


import pandas as pd
import os
from sklearn import metrics
import logging
logging.basicConfig(filename='/data/user/015664/AFuckingTrigger/seek_para/seek_para_log/lstm_seek_para_aimr.log',level=logging.DEBUG,datefmt='%Y-%m-%d %A %H:%M:%S')

para_list = []
for hidden_dim in [(16,), (32,), (32, 16), (16, 8)]:
    for full_conn_dim in [8, 16, 32]:
        for learning_rate_init in [0.070311]:
            for dropout in [0.2, 0.4]:
                para_list.append(dict(
                    hidden_dim=hidden_dim,
                    full_conn_dim=full_conn_dim,
                    learning_rate_init=learning_rate_init,
                    dropout=dropout
                ))

corr_series = {}
mae_series = {}

for idx in list(range( 24))+[24,25,26]:
    temp = pd.read_pickle('/data/user/015664/AFuckingTrigger/seek_para/pred_res/%d.pkl' % idx)
    corr_series[idx] = temp.corr().values[0, 1]
    mae_series[idx] = metrics.mean_absolute_error(temp['future'], temp['prediction'])
    # params = para_list[idx]
    # logging.info('*******************************************************')
    # logging.info(params)
    # logging.info('corr %f | mae %f' % (corr_series[idx], mae_series[idx]))
    # logging.info('*******************************************************')

corr_series = pd.Series(corr_series)
mae_series = pd.Series(mae_series)