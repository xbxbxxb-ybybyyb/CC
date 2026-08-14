# @Time : 2021/4/23 9:41
# @Author : Zhichen Lu
# @File : DoubleEnsemble.py
import pandas as pd
# import numpy as np
# import os,gc
# import xgboost as xgb

# import random
# from tqdm import tqdm
# from multiprocessing import Pool,Manager
# os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
def SR(res,alpha1,alpha2,gamma,bin_num,k):

    C = res.rank(pct=True,ascending=True)
    window = max(len(C)//10,1)
    sample_C = (C[-window:].mean()/C[:window].mean()).rank(pct=True)
    L = res.iloc[-1].rank(pct=True,ascending=True)*-1
    h = alpha1*L + alpha2* sample_C

    bin_id = (h.rank()//bin_num).astype(int)
    bin_info = pd.DataFrame({'bin_id':bin_id,'bin_val':h})
    bin_val = dict(bin_info.groupby('bin_id').mean()['bin_val'])
    bin_info['bin_val'] = bin_info['bin_id'].apply(lambda x : bin_val[x])
    bin_info['sample_weight'] = 1/((gamma**k) * bin_info['bin_val'] + 0.1)

    return bin_info['sample_weight']
#
# end_date = 20151225
# train_features,train_label,params = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/backup_data/round_1.pkl')
# pre_model_path = params['model_conf_path'].replace('round_%d'%params['round_num'],'round_%d'%(params['round_num']-1))+'%d/'%end_date
# d_train = xgb.DMatrix(train_features)
# res = []
# for i in range(1,params['n_estimators']+1):
#     model = xgb.Booster(model_file=pre_model_path+'model_%d.json'%i)
#     model.set_param({'predictor':'cpu_predictor'})
#     res.append(model.predict(d_train)[None,:])
# res = np.concatenate(tuple(res))
# res = pd.DataFrame((res - train_label.values[:,0])**2,index=list(range(1,params['n_estimators']+1)),columns=train_label.index)
# sample_weight = SR(res,alpha1=1,alpha2=1,gamma=0.5,bin_num = params['bin_num'],k=params['round_num'])
# def calc_feature_random(idx, col):
#     model = xgb.XGBRegressor()
#     model.load_model(pre_model_path + 'model_%d.json' % params['n_estimators'])
#     train_arr,random_idx = pool_dict['train_arr']._getvalue(),pool_dict['random_idx']._get_value()
#     train_arr[:,idx] = train_arr[:,idx][random_idx]
#     col_res[col] = model.predict(train_arr)
#     del train_arr,model
