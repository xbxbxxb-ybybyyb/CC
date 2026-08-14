# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import xgboost as xgb
import os, gc, time
from tqdm import tqdm
from dataApi.tradeDate import get_date_range
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
from FactorEvaluation.DailyFactorFixEvaluation.FixlizeDailyFactorLoading import loadFixlizedDailyFactor
from StrongStockModel.conf.path_config import root_path
import numpy as np
import configparser
conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
available_factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))
using_factor_list = sorted(list(set(using_factor_list).intersection(set(available_factor_list))))


def get_fix_factor_evaluation(num, end_index, eval_indicator):
    factor_evaluation = pd.read_pickle(root_path + 'external_data/ic_half.pkl')  # .set_index('name')
    factor_evaluation = pd.DataFrame(factor_evaluation)
    if not eval_indicator in factor_evaluation.index.levels[0]:
        raise Exception('Unavailable indicator')
    factor_evaluation = factor_evaluation.loc[eval_indicator]
    target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index)))
    factor_evaluation = factor_evaluation.loc[target_date]
    inter_col = list(set(factor_evaluation.index).intersection(set(using_factor_list)))
    factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
    return sorted(factor_list)

def get_daily_factor_evaluation(num, end_index, eval_indicator):
    res = pd.read_excel('/data/user/015664/AFuckingTrigger/DailyFactotrFixEvaluation2_res/结果汇总.xlsx',sheet_name='ic_abs',index_col=0)
    col = list(filter(lambda x : eval_indicator in x,res.columns.tolist()))
    col = list(filter(lambda x : x<f'{eval_indicator}_{end_index}',col))
    col = max(col)
    indicator_value = res[col].apply(abs).sort_values(ascending=False)
    return indicator_value.index.tolist()[:num]

def load_dataset(dp,start_date,end_date,fix_factor_list,daily_factor_list):
    X_train, y_train, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=start_date, end_date=end_date, return_idx=True)
    X_train_daily, index_daily = loadFixlizedDailyFactor(daily_factor_list, start_date, end_date)
    X_train_daily = X_train_daily.reshape((X_train_daily.shape[0] // 7, 7, X_train_daily.shape[1])).transpose(2,0,1)
    X_train = np.concatenate((X_train, X_train_daily), axis=0)
    del X_train_daily
    gc.collect()
    X_train, y_train, idx_date, idx_time, idx_code = dp.feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
    index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
    daily_name_list = []
    for i,daily_f in enumerate(daily_factor_list):
        if daily_f in fix_factor_list:
            daily_name_list.append(daily_f+'_daily_involved_in_fix')
        else:
            daily_name_list.append(daily_f)
    X_train, y_train = pd.DataFrame(X_train, index=index_train, columns=fix_factor_list + daily_name_list), pd.DataFrame(y_train, index=index_train, columns=['actual_label'])
    return X_train,y_train

def fit_model(i,output_path,indicator_fix,indicator_daily):
    train_start,train_end,test_start,test_end = para_list[i][1]
    path_dict = dict(
    res_path=output_path,
    val_path=output_path[:-1] + '_val_pred/',
    model_conf_path = output_path[:-1] + '_model_conf/',
    feature_eval_path = output_path[:-1] + '_feature_eval/',
    feature_path = output_path[:-1] + '_factor_list/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    if os.path.exists(path_dict['res_path']+'%d.pkl'%train_end):
        print(train_end,'exist')
        return
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [3,5,7,9,11]]
    fix_factor_list = get_fix_factor_evaluation(200,train_end,eval_indicator=indicator_fix)
    daily_factor_list = get_daily_factor_evaluation(200,train_end,eval_indicator=indicator_daily)
    pd.to_pickle([fix_factor_list, daily_factor_list], path_dict['feature_path'] + '%d.pkl' % train_end)

    dp = FixFactorRollPrepare(start_date=date_list[0], end_date=test_end, freq=7, model_time_len=1,
                              factor_list=fix_factor_list, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
    if not os.path.exists(path_dict['model_conf_path']+'%d.json'%train_end):
        X_train,y_train = load_dataset(dp,date_list[0],date_list[-2],fix_factor_list,daily_factor_list)
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
        X_val,y_val = load_dataset(dp,date_list[-11],date_list[-2],fix_factor_list,daily_factor_list)

        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path']+'%d.json'%train_end)
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)
    pd.to_pickle(y_val,path_dict['val_path']+'%d.pkl'%train_end)

    X_test, y_test = load_dataset(dp,test_start,test_end,fix_factor_list,daily_factor_list)
    d_test = xgb.DMatrix(X_test)
    y_test['prediction'] = model.predict(d_test)
    print(train_end,y_test.corr())
    pd.to_pickle(y_test,path_dict['res_path']+'%d.pkl'%train_end)
    print(path_dict['res_path']+'%d.pkl'%train_end)
    return True

# while len(os.listdir('/data/group/800319/FixlizeDailyFactor/dataShift/'))<936:
#     print(len(os.listdir('/data/group/800319/FixlizeDailyFactor/dataShift/')))
#     time.sleep(120)


# i=0
idx_list = list(range(73,118))#[::-1]
# idx_list = idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3]
for idx in tqdm(idx_list):
    fix_indicator, daily_indicator = 'ic_half_c', 'ic_c_half_year'
    out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_{fix_indicator}_{daily_indicator}/'
    fit_model(idx,out_path,fix_indicator,daily_indicator)
    gc.collect()

    fix_indicator, daily_indicator = 'ic_half_d', 'ic_d_half_year'
    out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_{fix_indicator}_{daily_indicator}/'
    fit_model(idx, out_path, fix_indicator, daily_indicator)
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