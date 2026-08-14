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
from FactorEvaluation.DailyFactorFixEvaluation.FixlizeDailyFactorLoading import loadFixlizedDailyFactor
import configparser
import numpy as np

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                      'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                      'subsample': 0.8, 'tree_method': 'gpu_hist'}

res = pd.read_pickle('/data/user/015664/AFuckingTrigger/FixFactorEvaluationFixly/res_integration/all_res.pkl')

exist_factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))


def eval_factor(date, indicator, num, time_point, freq):
    # date, indicator,num,time_point,freq = 20151225,'ic_c_fix',400,1000,'quater'
    eval_res = res[indicator][freq].swaplevel(0, 1).loc[time_point].sort_index().loc[:date]
    if eval_res.shape[0] == 0:
        raise Exception('No available evaluation')
    inter_list = list(set(exist_factor_list).intersection(eval_res.columns))
    eval_res = eval_res[inter_list].iloc[-1].apply(abs).sort_values(ascending=False)
    return sorted(eval_res.index.tolist()[:num])


def get_daily_factor_evaluation(num, end_index, eval_indicator, time_point):
    res = pd.read_excel('/data/user/015664/AFuckingTrigger/DailyFactotrFixEvaluation2_res/结果汇总.xlsx', sheet_name='ic_abs', index_col=0)
    col = list(filter(lambda x: eval_indicator in x, res.columns.tolist()))
    col = list(filter(lambda x: x < f'{eval_indicator}_{end_index}' and x.endswith(str(time_point)), col))
    col = max(col)
    indicator_value = res[col].apply(abs).sort_values(ascending=False)
    return indicator_value.index.tolist()[:num]


def load_dataset(dp, start_date, end_date, fix_factor_list, daily_factor_list, time_point):
    X_train, y_train, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=start_date, end_date=end_date, return_idx=True)
    nolimit = nolimit & (idx_time == time_point)
    X_train_daily, index_daily = loadFixlizedDailyFactor(daily_factor_list, start_date, end_date)
    X_train_daily = X_train_daily.reshape((X_train_daily.shape[0] // 7, 7, X_train_daily.shape[1])).transpose(2, 0, 1)
    X_train = np.concatenate((X_train, X_train_daily), axis=0)
    del X_train_daily
    gc.collect()
    X_train, y_train, idx_date, idx_time, idx_code = dp.feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
    index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
    daily_name_list = []
    for i, daily_f in enumerate(daily_factor_list):
        if daily_f in fix_factor_list:
            daily_name_list.append(daily_f + '_daily_involved_in_fix')
        else:
            daily_name_list.append(daily_f)
    X_train, y_train = pd.DataFrame(X_train, index=index_train, columns=fix_factor_list + daily_name_list), pd.DataFrame(y_train, index=index_train, columns=['actual_label'])
    return X_train, y_train


def fit_model(i, output_path, fix_indicator, daily_indicator, num, time_point, freq):
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
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    if os.path.exists(path_dict['res_path'] + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return

    fix_factor_list = eval_factor(train_end, fix_indicator, num // 2, time_point, freq)
    daily_factor_list = get_daily_factor_evaluation(num // 2, train_end, daily_indicator, time_point)
    pd.to_pickle({'daily': daily_factor_list, 'fix': fix_factor_list}, path_dict['feature_path'] + '%d.pkl' % train_end)
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [1, 3, 5, 7, 9, 11]]
    dp = FixFactorRollPrepare(end_date=test_end, freq=7, model_time_len=1,
                              factor_list=fix_factor_list, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
    if not os.path.exists(path_dict['model_conf_path'] + '%d.json' % train_end):
        X_train, y_train = load_dataset(dp, date_list[0], date_list[-2], fix_factor_list, daily_factor_list, time_point)
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val, y_val = X_train.loc[val_date_list[1:]], y_train.loc[val_date_list[1:]]
        X_train, y_train = X_train.loc[date_list], y_train.loc[date_list]
        d_eval = xgb.DMatrix(X_val, label=y_val['actual_label'])
        d_train = xgb.DMatrix(X_train, label=y_train.values)
        model = xgb.train(params=best_param_clf_xgb, dtrain=d_train, num_boost_round=best_param_clf_xgb['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15,
                          verbose_eval=False)
        # eval_res = pd.DataFrame(
        #     {each: pd.Series(model.get_score(importance_type=each)) for each in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']}
        # )
        # eval_res['fscore'] = pd.Series(model.get_fscore())
        # pd.to_pickle(eval_res, path_dict['feature_eval_path'] + '%d.pkl' % train_end)

        model.save_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    else:
        print(train_end, 'model_exist')
        X_val, y_val = load_dataset(dp, date_list[-11], date_list[-2], fix_factor_list, daily_factor_list, time_point)
        X_val, y_val = X_val.loc[val_date_list[1:]], y_val.loc[val_date_list[1:]]
        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)
    pd.to_pickle(y_val, path_dict['val_path'] + '%d.pkl' % train_end)

    X_test, y_test = load_dataset(dp, test_start, test_end, fix_factor_list, daily_factor_list, time_point)
    d_test = xgb.DMatrix(X_test)
    y_test['prediction'] = model.predict(d_test)
    print(train_end, y_test.corr())
    pd.to_pickle(y_test, path_dict['res_path'] + '%d.pkl' % train_end)
    print(path_dict['res_path'] + '%d.pkl' % train_end)
    return True


fix_eval_indicator = 'ic_d_fix'
daily_eval_indicator = 'ic_d_fix_year'
frq = 'year'
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
factor_num = 400

idx_list = list(range(73))  # [::-1]

from multiprocessing import Pool

pool = Pool(2)

bar = tqdm(total=len(idx_list) * len(bar_list))


def update(*p):
    bar.update()
    if bar.last_print_n >= bar.total:
        bar.close()


res_dict = {}
for idx in idx_list[::-1]:
    out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelByFix/XGBAllFactor_train400_test10_factornum{factor_num}_fix_eval_{fix_eval_indicator}_daily_eval_{daily_eval_indicator}_freq_{frq}/'
    for time_point in bar_list[::-1]:
        res_dict[f'{idx}_{time_point}'] = pool.apply_async(fit_model, (idx, out_path, fix_eval_indicator, daily_eval_indicator, factor_num, time_point, frq))
        # fit_model(idx, out_path, fix_eval_indicator,daily_eval_indicator, factor_num, time_point, frq)
    # process = Process(target=fit_model, args=(idx, out_path, eval_indicator, factor_num,time_point,frq))
    # process.start()
    # process.join()
    # gc.collect()
pool.close()
pool.join()
for each in res_dict:
    res_dict[each] = res_dict[each].get()

# idx_list = range(73)
# split_idx_list = [idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3] for i in range(3)]
# split_idx_list = list(zip(*tuple(split_idx_list)))
# for idx_list in split_idx_list[::-1]:
#     for idx in idx_list:
#         process = Process(target=fit_model,args=(idx,out_path,eval_indicator,factor_num))
#         process.start()
#         process.join()
#         gc.collect()

