# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import xgboost as xgb
import os, gc, time, datetime
from tqdm import tqdm
from multiprocessing import Process
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
import configparser
conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}

def fit_model(i,output_path):
    train_start,train_end,test_start,test_end = para_list[i][1]
    path_dict = dict(
    res_path=output_path,
    val_path=output_path[:-1] + 'val_pred/',
    model_conf_path = output_path[:-1] + 'model_conf/',
    feature_eval_path = output_path[:-1] + 'feature_eval/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])

    using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
    factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))
    using_factor_list = sorted(list(set(using_factor_list).intersection(set(factor_list))))

    date_list = get_date_range(get_pre_trade_date(train_end,50), train_end)
    val_date_list = [date_list[-i] for i in [1,3,5,7,9]]
    if not os.path.exists(path_dict['model_conf_path']+'%d.json'%train_end):
        dp = FixFactorRollPrepare(start_date=date_list[0], end_date=test_end, freq=7, model_time_len=1,
                                  factor_list=using_factor_list, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
        X_train, y_train, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=date_list[0], end_date=date_list[-2], return_idx=True)
        X_train, y_train, idx_date, idx_time, idx_code = dp.feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
        index_train = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
        X_train,y_train = pd.DataFrame(X_train,index=index_train,columns=using_factor_list),pd.DataFrame(y_train,index=index_train,columns=['actual_label'])
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val,y_val = X_train.loc[val_date_list],y_train.loc[val_date_list]
        X_train,y_train = X_train.loc[date_list],y_train.loc[date_list]

        d_train = xgb.DMatrix(X_train[:-50000],label=y_train[:-50000].values)
        d_eval = xgb.DMatrix(X_train[-50000:],label=y_train[-50000:].values)
        model = xgb.train(params=best_param_clf_xgb,dtrain=d_train,num_boost_round=best_param_clf_xgb['n_estimators'],evals=[(d_eval,'d_eval')],early_stopping_rounds=15,verbose_eval=False)
        eval_res = pd.DataFrame(
            {each : pd.Series(model.get_score(importance_type=each)) for each in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']}
        )
        eval_res['fscore'] = pd.Series(model.get_fscore())
        pd.to_pickle(eval_res,path_dict['feature_eval_path']+'%d.pkl'%train_end)
        model.save_model(path_dict['model_conf_path']+'%d.json'%train_end)
    else:
        dp = FixFactorRollPrepare(start_date=date_list[0], end_date=test_end, freq=7, model_time_len=1,
                                  factor_list=using_factor_list, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
        X_val, y_val, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=date_list[-9], end_date=date_list[-1], return_idx=True)
        X_val, y_val, idx_date, idx_time, idx_code = dp.feature_engineering(X_val, y_val, nolimit, idx_date, idx_time, idx_code)
        index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
        X_val, y_val = pd.DataFrame(X_val, index=index_train, columns=using_factor_list), pd.DataFrame(y_val, index=index_train, columns=['actual_label'])
        X_val, y_val = X_val.loc[val_date_list], y_val.loc[val_date_list]
        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path']+'%d.json'%train_end)
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)
    pd.to_pickle(y_val,path_dict['val_path']+'%d.pkl'%train_end)

    X_test, y_test, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=test_start, end_date=test_end, return_idx=True)
    X_test, y_test, idx_date, idx_time, idx_code = dp.feature_engineering(X_test, y_test, nolimit, idx_date, idx_time, idx_code)
    index_test = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
    X_test,y_test = pd.DataFrame(X_test,index=index_test,columns=using_factor_list),pd.DataFrame(y_test,index=index_test,columns=['actual_label'])
    d_test = xgb.DMatrix(X_test)
    y_test['prediction'] = model.predict(d_test)
    print(train_end,y_test.corr())
    pd.to_pickle(y_test,path_dict['res_path']+'%d.pkl'%train_end)
    return True

out_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train50_test50/'

# i=0
idx_list = range(73,128)
# idx_list = idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3]
for idx in tqdm(idx_list):
    process = Process(target=fit_model,args=(idx,out_path))
    process.start()
    process.join()
    gc.collect()

# idx_list = range(73)
# split_idx_list = [idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3] for i in range(3)]
# split_idx_list = list(zip(*tuple(split_idx_list)))
# for idx_list in split_idx_list[::-1]:
#     for idx in idx_list:
#         process = Process(target=fit_model,args=(idx,out_path))
#         process.start()
#         process.join()
#         gc.collect()
