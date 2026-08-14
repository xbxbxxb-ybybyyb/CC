# @Time : 2022/1/4 10:30
# @Author : Zhichen Lu
# @File : eval_res_integration.py
import pandas as pd
import numpy as np

# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
import os, gc, time, datetime, random
from tqdm import tqdm

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
params = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607, 'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100,
          'sampling_method': 'gradient_based', 'subsample': 0.8, 'tree_method': 'gpu_hist',
          'val_pred_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_val_pred/',
          'model_conf_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_model_conf/',
          'feature_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_factor_list/',
          'load local model': True}


def eval_feature(end_date=None):
    EVAL_PATH = params['val_pred_path'].replace('val_pred','EvalRes')
    if os.path.exists(f'{EVAL_PATH}/{end_date}.pkl'):
        print(f'{end_date} exist')
        return
    _, val_label = pd.read_pickle(params['val_pred_path'] + f'{end_date}.pkl')
    # idx = val_features.columns.tolist().index(factor_name)
    factor_list = pd.read_pickle(params['feature_path']+f'{end_date}.pkl')
    for factor_name in tqdm(factor_list):
        factor_arr = np.load(f'{EVAL_PATH}/{end_date}/{factor_name}.npy')
        val_label[factor_name] = factor_arr
        del factor_arr
        gc.collect()

    mae_arr = val_label.values - val_label[['actual_label']].values
    mae_arr = abs(mae_arr)

    gain = np.nanmean(mae_arr - mae_arr[:,[1]],axis=0)/np.nanstd(mae_arr -  mae_arr[:,[1]],axis=0)
    gain = pd.Series(gain,index=val_label.columns)

    mae = np.nanmean(mae_arr,axis=0)

    del mae_arr
    gc.collect()

    mae = pd.Series(mae,index=val_label.columns)
    mae_diff = mae - mae['prediction']

    corr = val_label.corrwith(val_label['actual_label'])
    corr_diff = corr['prediction'] - corr

    res = pd.DataFrame({
        'DEGain':gain,
        'corr_diff':corr_diff,
        'mae_diff':mae_diff
    })
    res = res.drop(['actual_label','prediction'])
    pd.to_pickle(res,f'{EVAL_PATH}/{end_date}.pkl')
    print(end_date,'done')
    # return res

from multiprocessing import Pool

pool = Pool(10)
period_list = sorted(map(lambda x : x.replace('.pkl',''),os.listdir(params['val_pred_path'])))

bar = tqdm(total=len(period_list))

def update(*param):
    if bar.last_print_n>=bar.total:
        bar.close()
    else:
        bar.update()

for p_id in period_list:
    pool.apply_async(eval_feature,(p_id,),callback=update)

pool.close()
pool.join()





