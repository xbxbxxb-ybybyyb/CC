# @Time : 2021/4/14 9:52
# @Author : Zhichen Lu
# @File : XGBTrainByFix.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import xgboost as xgb
import os, gc, time, datetime
from tqdm import tqdm
from multiprocessing import Process
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                      'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                      'subsample': 0.8, 'tree_method': 'gpu_hist'}

res = pd.read_pickle('/data/user/015664/AFuckingTrigger/FixFactorEvaluationFixly/res_integration/all_res.pkl')

exist_factor_list = list(map(lambda x : x.replace('.npy',''),os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))

def eval_factor(date, indicator, num, time_point, freq):
    # date, indicator,num,time_point,freq = 20151225,'ic_c_fix',400,1000,'quater'
    eval_res = res[indicator][freq].swaplevel(0, 1).loc[time_point].sort_index().loc[:date]
    if eval_res.shape[0] == 0:
        raise Exception('No available evaluation')
    inter_list = list(set(exist_factor_list).intersection(eval_res.columns))
    eval_res = eval_res[inter_list].iloc[-1].apply(abs).sort_values(ascending=False)
    return sorted(eval_res.index.tolist()[:num])


def fit_model(i, output_path, indicator, num, time_point, freq):
    if not os.path.exists(output_path):
        os.mkdir((output_path))
    output_path = f'{output_path}/{time_point}/'
    train_start, train_end, test_start, test_end = para_list[i][1]
    path_dict = dict(
        res_path=output_path,
        val_path=output_path[:-1] + 'val_pred_path/',
        model_conf_path=output_path[:-1] + 'model_conf/',
        feature_path=output_path[:-1] + 'feature_path/'
    )
    if os.path.exists(path_dict['res_path'] + '%d.pkl' % train_end):
        print(f'{train_end} exist')
        return
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])

    using_factor_list = eval_factor(train_end, indicator, num, time_point, freq)
    pd.to_pickle(using_factor_list, path_dict['feature_path'] + '%d.pkl' % train_end)
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [1, 3, 5, 7, 9]]
    dp = FixFactorRollPrepare(end_date=test_end, freq=7, model_time_len=1,
                              factor_list=using_factor_list, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
    if not os.path.exists(path_dict['model_conf_path'] + '%d.json' % train_end):
        X_train, y_train, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=train_start, end_date=train_end, return_idx=True)
        nolimit = nolimit & (idx_time == time_point)
        X_train, y_train, idx_date, idx_time, idx_code = dp.feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
        index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_code)))
        X_train, y_train = pd.DataFrame(X_train, index=index_train, columns=using_factor_list), pd.DataFrame(y_train, index=index_train, columns=['actual_label'])
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val, y_val = X_train.loc[val_date_list], y_train.loc[val_date_list]
        X_train, y_train = X_train.loc[date_list], y_train.loc[date_list]
        print('feature_shape', X_train.shape)
        d_train = xgb.DMatrix(X_train, label=y_train.values)
        d_eval = xgb.DMatrix(X_val, label=y_val['actual_label'])
        model = xgb.train(params=best_param_clf_xgb, dtrain=d_train, num_boost_round=best_param_clf_xgb['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15,
                          verbose_eval=False)

        model.save_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    else:
        print(train_end, 'model_exist')
        X_val, y_val, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=date_list[-9], end_date=date_list[-1], return_idx=True)
        nolimit = nolimit&(idx_time==time_point)
        X_val, y_val, idx_date, idx_time, idx_code = dp.feature_engineering(X_val, y_val, nolimit, idx_date, idx_time, idx_code)
        index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
        X_val, y_val = pd.DataFrame(X_val, index=index_train, columns=using_factor_list), pd.DataFrame(y_val, index=index_train, columns=['actual_label'])
        X_val, y_val = X_val.loc[val_date_list], y_val.loc[val_date_list]
        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)
    pd.to_pickle(y_val, path_dict['val_path'] + '%d.pkl' % train_end)

    X_test, y_test, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=test_start, end_date=test_end, return_idx=True)
    nolimit = nolimit &(idx_time==time_point)
    X_test, y_test, idx_date, idx_time, idx_code = dp.feature_engineering(X_test, y_test, nolimit, idx_date, idx_time, idx_code)
    index_test = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
    X_test, y_test = pd.DataFrame(X_test, index=index_test, columns=using_factor_list), pd.DataFrame(y_test, index=index_test, columns=['actual_label'])
    d_test = xgb.DMatrix(X_test)
    y_test['prediction'] = model.predict(d_test)
    print(train_end, y_test.corr())
    pd.to_pickle(y_test, path_dict['res_path'] + '%d.pkl' % train_end)
    print(path_dict['res_path'] + '%d.pkl' % train_end)
    return True


eval_indicator = 'ic_c_fix'
frq = 'month'
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
factor_num = 400

idx_list = list(range(73))  # [::-1]

for idx in tqdm(idx_list):
    out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelByFix/XGBAllFactor_train400_test10_factornum{factor_num}_eval_{eval_indicator}_freq_{frq}/'
    for time_point in bar_list:
        fit_model(idx, out_path, eval_indicator, factor_num, time_point, frq)
    # process = Process(target=fit_model, args=(idx, out_path, eval_indicator, factor_num,time_point,frq))
    # process.start()
    # process.join()
    # gc.collect()

# idx_list = range(73)
# split_idx_list = [idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3] for i in range(3)]
# split_idx_list = list(zip(*tuple(split_idx_list)))
# for idx_list in split_idx_list[::-1]:
#     for idx in idx_list:
#         process = Process(target=fit_model,args=(idx,out_path,eval_indicator,factor_num))
#         process.start()
#         process.join()
#         gc.collect()