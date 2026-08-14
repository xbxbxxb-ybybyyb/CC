from StrongStockModel.model.Modelmpl.CrossValidation.DataPrepare import  split_train_predict
from dataApi.tradeDate import get_date_range
import pandas as pd
import configparser
import gc,os,time
from tqdm import tqdm

test_split = 4


model_root = '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_c/'
tag = os.path.split('/'+model_root.strip('/'))[1]
integrated_root = f'{model_root}{tag}/'

for each in ['','_val_pred']:
    if not os.path.exists(f'{integrated_root[:-1]}{each}/'):
        os.mkdir(f'{integrated_root[:-1]}{each}/')


conf = configparser.ConfigParser()
conf.read('/data//group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
para_list = para_list[24:133]
model_date_list = {i:each[1] for i,each in enumerate(para_list)}

#40天定阈值
test_days = 40
freq = 7
score = []
sign = {}
for idx in tqdm(range(len(model_date_list))):
    test = []
    for test_id in range(test_split):
        test.append(pd.read_pickle(f'{model_root}/part{test_id}/test/{idx}.pkl'))
    test_yh = pd.concat(test).set_index(['date', 'time', 'code'])['yh'].unstack().tail(test_days * freq)
    test_y = pd.concat(test).set_index(['date', 'time', 'code'])['y'].unstack().tail(test_days * freq)
    sample = test_yh.count()
    mean = test_yh.mean()[sample > test_days * freq / 2]
    std = test_yh.std()[sample > test_days * freq / 2]

    test_yh = (test_yh[mean.index]-mean)/std


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
    pd.to_pickle(pred.rename(columns ={'y':'actual_label','yh':'prediction'}),
                 f'{integrated_root}{model_date_list[idx][1]}.pkl')
    pd.to_pickle(pd.DataFrame({'actual_label':test_y.stack(),'prediction':test_yh.stack()})
                 ,f'{integrated_root[:-1]}_val_pred/{model_date_list[idx][1]}.pkl')





score = pd.DataFrame(score, columns=['pre', 'pro'])
sign = pd.concat([sign[x] for x in sign])

stat = []
for rho in [1, 1.1, 1.2, 1.3, 1.4, 1.5]:
    temp = sign[sign['yh'] > rho]
    num = len(temp) / 1090
    ret = temp['y'].mean()
    stat.append([rho, num, ret])

df = sign['yh'].unstack()
pd.to_pickle(sign['yh'],f'/data/group/800442/800319/信号存储/{tag}_pred_stack.pkl')
df[df>1.25].to_pickle(f'/data/group/800442/800319/信号存储/{tag}.pkl')
sign.rename(columns ={'y':'actual_label','yh':'prediction'}).to_pickle(f'{integrated_root[:-1]}.pkl')
# sign = pd.read_pickle('/data//group/800442/800319/信号存储/XGB_MVK4_40d_yh.pkl')


total_res = {}
for each in ['XGB_ic_d','XGB_ic_t','XGB_ic_c']:
    total_res[each] = pd.read_pickle(f'/data/group/800442/800319/信号存储/{each}_pred_stack.pkl')

total_res = pd.DataFrame(total_res)
total_res = total_res.mean(axis=1).unstack()
total_res[total_res>1.25].to_pickle(f'/data/group/800442/800319/信号存储/CrossValXGBIndividualyIntegration.pkl')

