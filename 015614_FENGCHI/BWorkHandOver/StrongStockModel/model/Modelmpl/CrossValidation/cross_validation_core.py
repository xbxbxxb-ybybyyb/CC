from StrongStockModel.model.Modelmpl.CrossValidation.DataPrepare import  split_train_predict
from dataApi.tradeDate import get_date_range
import pandas as pd
import gc
import os
import time

test_split = 4


model_root = '/data/user/015836/HFmodel/NNResearch/20210629XGBCompare/'

model_date_list = split_train_predict(
    train_days=200, predict_days=10, future_day=1,
    pred_start=20161221, pred_end=20210616,
    load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')

#40天定阈值
test_days = 40
freq = 7
score = []
sign = {}
for idx in range(len(model_date_list)):
    test = []
    for test_id in range(test_split):
        test.append(pd.read_pickle(f'{model_root}/part{test_id}/test/{idx}.pkl'))
    test = pd.concat(test).set_index(['date', 'time', 'code'])['yh'].unstack().tail(test_days * freq)
    sample = test.count()
    mean = test.mean()[sample > test_days * freq / 2]
    std = test.std()[sample > test_days * freq / 2]

    pred = pd.read_pickle(f'{model_root}/part0/pred/{idx}.pkl').set_index(['date', 'time', 'code'])
    for test_id in range(1, test_split):
        pred['yh'] += pd.read_pickle(f'{model_root}/part{test_id}/pred/{idx}.pkl').set_index(['date', 'time', 'code'])['yh']
    pred['yh'] /= test_split
    ic1 = pred['yh'].corr(pred['y'])
    pred_yh = pred['yh'].unstack().reindex(columns=mean.index)
    pred_yh = (pred_yh - mean) / std
    pred_y = pred['y'].unstack().reindex(columns=std.index)
    pred = pd.concat([pred_yh.stack(), pred_y.stack()], axis=1, keys=['yh', 'y'])
    ic2 = pred['yh'].corr(pred['y'])
    score.append([ic1, ic2])
    sign[idx] = pred
score = pd.DataFrame(score, columns=['pre', 'pro'])
sign = pd.concat([sign[x] for x in sign])

stat = []
for rho in [1, 1.1, 1.2, 1.3, 1.4, 1.5]:
    temp = sign[sign['yh'] > rho]
    num = len(temp) / 1090
    ret = temp['y'].mean()
    stat.append([rho, num, ret])

df = sign['yh'].unstack()
df[df > 1.25].to_pickle('/data/group/800319/信号存储/XGB_MVK4_40d_tho125.pkl')
sign.to_pickle('/data/group/800319/信号存储/XGB_MVK4_40d_yh.pkl')
sign = pd.read_pickle('/data/group/800319/信号存储/XGB_MVK4_40d_yh.pkl')


