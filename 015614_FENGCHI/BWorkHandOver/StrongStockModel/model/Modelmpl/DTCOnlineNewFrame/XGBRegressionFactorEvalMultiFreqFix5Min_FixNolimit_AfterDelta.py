# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
import pandas as pd
import xgboost as xgb
import os, gc, time
from tqdm import tqdm
from dataApi.tradeDate import get_date_range
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering, load_fixes_data
from dataApi.diff_factor_concat import load_mix_data
from StrongStockModel.conf.path_config import root_path
import numpy as np
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442//800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                      'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                      'subsample': 0.8, 'tree_method': 'gpu_hist'}
using_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3_file/available_factor_list.pkl')
available_factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/arch1/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/')))
using_factor_list = sorted(list(set(using_factor_list).intersection(set(available_factor_list))))


# Old_HX_Factor = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/external_data/factor5min_eval_revised/dtc_union_factor.pkl')

def get_fix_factor_evaluation(num, end_index, eval_indicator):
    factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{eval_indicator}.pkl')
    inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(using_factor_list)))
    factor_evaluation = factor_evaluation[inter_col]
    target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index.tolist())))
    if 'ret' in eval_indicator:
        print('ret')
        factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
    elif 'ic' in eval_indicator:
        print('ic')
        factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
    else:
        raise Exception('')
    factor_list = factor_evaluation.index.tolist()[:num]
    return sorted(factor_list)


def get_5min_factor_evaluation(num, end_index, eval_indicator,
                               eval_res_path='/data/group/800442/800319/junkData/StrongStock/external_data/factor5min_eval_revised/'):
    eval_res = pd.read_pickle(f'{eval_res_path}/{eval_indicator}.pkl')
    target_date = max(list(filter(lambda x: x < end_index, eval_res.index)))
    # inter_col = set(eval_res.columns).intersection(set(Old_HX_Factor))
    # eval_res = eval_res[list(inter_col)]
    factor_list = eval_res.loc[target_date].apply(abs).sort_values(ascending=False).index.to_list()[:num]
    factor_list = [f'M5{x}' for x in factor_list]
    return sorted(factor_list)


def load_dataset(start_date, end_date_, fix_factor_list, min5_factor_list, min5_adress='/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/'):
    if end_date_ > 20210901:
        end_date = 20210901
    else:
        end_date = end_date_
    X_5min, y_5min, nolimit_5min, idx_date_5min, idx_code_5min, idx_time_5min = load_fix_data(start_date=start_date, end_date=end_date, factor_list=min5_factor_list,
                                                                                              address=min5_adress)
    X_fix, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix = load_fix_data(start_date=start_date, end_date=end_date, factor_list=fix_factor_list)

    if X_5min.shape != X_fix.shape:
        raise Exception('Fix shape is not equal to 5min shape')
    X = np.concatenate((X_fix, X_5min), axis=0)
    if (idx_date_5min != idx_date_fix).sum() > 0 or (idx_time_5min != idx_time_fix).sum() > 0 or (idx_code_5min != idx_code_fix).sum() > 0:
        raise Exception('idx are not match')
    nolimit_count = (nolimit_5min != nolimit_fix).sum()
    if nolimit_count > 0:
        print('nolimit not match', nolimit_count)
    X, y, idx_date, idx_code, idx_time = feature_engineering(X, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
    return pd.DataFrame(X, index=index, columns=fix_factor_list + min5_factor_list), pd.DataFrame({'actual_label': y}, index=index)


def fit_model(i, output_path, indicator_fix, indicator_daily):
    train_start, train_end, test_start, test_end = para_list[i][1]
    print(para_list[i])
    path_dict = dict(
        res_path=output_path,
        val_path=output_path[:-1] + '_val_pred/',
        model_conf_path=output_path[:-1] + '_model_conf/',
        feature_eval_path=output_path[:-1] + '_feature_eval/',
        feature_path=output_path[:-1] + '_factor_list/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    if os.path.exists(path_dict['res_path'] + '%d.pkl' % train_end):
        print(path_dict['res_path'] + '%d.pkl' % train_end, 'exist')
        return
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [3, 5, 7, 9, 11]]
    fix_factor_list = get_fix_factor_evaluation(200, train_end, eval_indicator=indicator_fix)
    min5_factor_list = get_5min_factor_evaluation(200, train_end, eval_indicator=indicator_daily)
    pd.to_pickle([fix_factor_list, min5_factor_list], path_dict['feature_path'] + '%d.pkl' % train_end)

    if not os.path.exists(path_dict['model_conf_path'] + '%d.json' % train_end):
        # X_train,y_train = load_dataset(dp,date_list[0],date_list[-2],fix_factor_list,min5_factor_list)
        X_train, y_train = load_dataset(date_list[0], date_list[-2], fix_factor_list, min5_factor_list)
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val, y_val = X_train.loc[val_date_list], y_train.loc[val_date_list]
        X_train, y_train = X_train.loc[date_list], y_train.loc[date_list]

        d_train = xgb.DMatrix(X_train[:-50000], label=y_train[:-50000].values)
        d_eval = xgb.DMatrix(X_train[-50000:], label=y_train[-50000:].values)
        model = xgb.train(params=best_param_clf_xgb, dtrain=d_train, num_boost_round=best_param_clf_xgb['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15,
                          verbose_eval=False)
        eval_res = pd.DataFrame(
            {each: pd.Series(model.get_score(importance_type=each)) for each in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']}
        )
        eval_res['fscore'] = pd.Series(model.get_fscore())
        pd.to_pickle(eval_res, path_dict['feature_eval_path'] + '%d.pkl' % train_end)

        model.save_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    else:
        X_val, y_val = load_dataset(date_list[-11], date_list[-2], fix_factor_list, min5_factor_list)

        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)
    pd.to_pickle(y_val, path_dict['val_path'] + '%d.pkl' % train_end)

    if test_start==test_end and test_start==train_end:
        return True
    X_test, y_test = load_dataset(test_start, test_end, fix_factor_list, min5_factor_list)
    d_test = xgb.DMatrix(X_test)
    y_test['prediction'] = model.predict(d_test)
    print(train_end, y_test.corr())
    pd.to_pickle(y_test, path_dict['res_path'] + '%d.pkl' % train_end)
    print(path_dict['res_path'] + '%d.pkl' % train_end)
    return True


# while len(os.listdir('/arch1/group/800442/800319/FixlizeDailyFactor/dataShift/'))<936:
#     print(len(os.listdir('/arch1/group/800442/800319/FixlizeDailyFactor/dataShift/')))
#     time.sleep(120)


# i=0
import datetime

idx_list = list(range(144))[24:][::-1][:1]
# idx_list = idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3]
base_path = '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/'
if not os.path.exists(base_path):
    os.mkdir(base_path)
for idx in tqdm(idx_list):
    fix_indicator, daily_indicator = 'ic_d', 'ic_half_d'
    out_path = f'{base_path}XGBMultiFreqFix5minFixNolimit_train200_test10_{fix_indicator}_{daily_indicator}/'
    fit_model(idx, out_path, fix_indicator, daily_indicator)
    gc.collect()

    fix_indicator, daily_indicator = 'ic_t', 'ic_half_t'
    out_path = f'{base_path}XGBMultiFreqFix5minFixNolimit_train200_test10_{fix_indicator}_{daily_indicator}/'
    fit_model(idx, out_path, fix_indicator, daily_indicator)
    gc.collect()

    fix_indicator, daily_indicator = 'ic_c', 'ic_half_c'
    out_path = f'{base_path}XGBMultiFreqFix5minFixNolimit_train200_test10_{fix_indicator}_{daily_indicator}/'
    fit_model(idx, out_path, fix_indicator, daily_indicator)
    gc.collect()

# all_m5factor = set()
# for fix_indicator, daily_indicator in [('ic_d', 'ic_half_d'),('ic_t', 'ic_half_t'),('ic_c', 'ic_half_c')]:
#     _,train_end,_,_ = para_list[139][1]
#     fix_factor,m5factor = pd.read_pickle(f'{base_path}XGBMultiFreqFix5minFixNolimit_train200_test10_{fix_indicator}_{daily_indicator}_factor_list/{train_end}.pkl')
#     all_m5factor = all_m5factor.union(set(m5factor))
#
# pd.to_pickle(sorted(list(all_m5factor)),f'/data/group/800442/800319/strategy_HFfactor/subscript_factor_list/desample_factor_list20210802.pkl')
#
# from dataApi.sendInfo import send_message
#
# send_message(['015664'],f'/data/group/800442/800319/strategy_HFfactor/subscript_factor_list/desample_factor_list20210802.pkl')

