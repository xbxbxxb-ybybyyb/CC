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
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
from FactorEvaluation.DailyFactorFixEvaluation.FixlizeDailyFactorLoading import loadFixlizedDailyFactor
import configparser
from StrongStockModel.conf.path_config import root_path
import numpy as np

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                      'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                      'subsample': 0.8, 'tree_method': 'gpu_hist'}

# exist_factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))

"""
def eval_factor(date, indicator, num, time_point, freq):
    res = pd.read_pickle('/data/user/015664/AFuckingTrigger/FixFactorEvaluationFixly/res_integration/all_res.pkl')
    # date, indicator,num,time_point,freq = 20151225,'ic_c_fix',400,1000,'quater'
    eval_res = res[indicator][freq].swaplevel(0, 1).loc[time_point].sort_index().loc[:date]
    if eval_res.shape[0] == 0:
        raise Exception('No available evaluation')
    inter_list = list(set(exist_factor_list).intersection(eval_res.columns))
    eval_res = eval_res[inter_list].iloc[-1].apply(abs).sort_values(ascending=False)
    return sorted(eval_res.index.tolist()[:num])
"""


def get_fix_factor_evaluation(eval_indicator, num, end_index):
    using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
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


def get_daily_factor_evaluation(num, end_index, eval_indicator, time_point):
    res = pd.read_excel('/data/user/015664/AFuckingTrigger/DailyFactotrFixEvaluation2_res/结果汇总.xlsx', sheet_name='ic_abs', index_col=0)
    col = list(filter(lambda x: eval_indicator in x, res.columns.tolist()))
    col = list(filter(lambda x: x < f'{eval_indicator}_{end_index}' and x.endswith(str(time_point)), col))
    col = max(col)
    indicator_value = res[col].apply(abs).sort_values(ascending=False)
    return indicator_value.index.tolist()[:num]


def load_dataset(start_date, end_date, fix_factor_list):
    X_train, y_train, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=start_date, end_date=end_date, factor_list=fix_factor_list)
    gc.collect()
    X_train, y_train, idx_date, idx_time, idx_code = feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
    index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
    X_train, y_train = pd.DataFrame(X_train, index=index_train, columns=fix_factor_list), pd.DataFrame(y_train, index=index_train, columns=['actual_label'])
    return X_train, y_train


def fit_model(i, output_path, fix_indicator, num, back_window=5):
    if not os.path.exists(output_path):
        os.mkdir((output_path))
    output_path = f'{output_path}/'
    train_start, train_end, test_start, test_end = para_list[i][1]
    path_dict = dict(
        res_path=output_path[:-1] + 'res/',
        val_path=output_path[:-1] + 'val_pred_path/',
        model_conf_path=output_path[:-1] + 'model_conf/',
        feature_path=output_path[:-1] + 'feature_path/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    if os.path.exists(path_dict['res_path'] + '%d.pkl' % train_end):
        print(train_end, fix_indicator, 'exist')
        return

    fix_factor_list = get_fix_factor_evaluation(fix_indicator, num, train_end)
    pd.to_pickle(fix_factor_list, path_dict['feature_path'] + '%d.pkl' % train_end)
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [1, 3, 5, 7, 9, 11]]

    if not os.path.exists(path_dict['model_conf_path'] + '%d.json' % train_end):
        X_train, y_train = load_dataset(date_list[0], date_list[-2], fix_factor_list)
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val, y_val = X_train.loc[val_date_list[1:]], y_train.loc[val_date_list[1:]]
        X_train, y_train = X_train.loc[date_list], y_train.loc[date_list]
        d_eval = xgb.DMatrix(X_val, label=y_val['actual_label'])
        d_train = xgb.DMatrix(X_train, label=y_train.values)
        model = xgb.train(params=best_param_clf_xgb, dtrain=d_train, num_boost_round=best_param_clf_xgb['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15,
                          verbose_eval=False)
        model.save_model(path_dict['model_conf_path'] + '%d.json' % train_end)
    else:
        print(train_end, 'model_exist')
        X_val, y_val = load_dataset(date_list[-11], date_list[-2], fix_factor_list)
        X_val, y_val = X_val.loc[val_date_list[1:]], y_val.loc[val_date_list[1:]]
        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path'] + '%d.json' % train_end)
        model.set_param('predictor', 'cpu_predictor')
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)

    past_model_list = list(filter(lambda x: x < f'{train_end}.json', os.listdir(path_dict['model_conf_path'])))
    if past_model_list:
        past_model_list = sorted(past_model_list)[-back_window:]
        for model_idx, each in enumerate(past_model_list[::-1]):
            temp_model = xgb.Booster(model_file=path_dict['model_conf_path'] + each)
            temp_model.set_param('predictor', 'cpu_predictor')
            y_val[f'predicton_by_{model_idx}_{each[:-5]}'] = temp_model.predict(d_val)
    past_corr = y_val.corr().loc['actual_label'].drop('actual_label')
    best_idx = past_corr.idxmax()
    y_val = pd.DataFrame({'actual_label': y_val['actual_label'], 'prediction': y_val[best_idx]})

    if best_idx != 'prediction':
        model = xgb.Booster(model_file=path_dict['model_conf_path'] + best_idx[-8:] + '.json')
        print(fix_indicator, train_end, best_idx)
    else:
        print(fix_indicator, train_end, 'current bset')
    model.set_param('predictor', 'cpu_predictor')
    pd.to_pickle(y_val, path_dict['val_path'] + '%d.pkl' % train_end)

    X_test, y_test = load_dataset(test_start, test_end, fix_factor_list)
    d_test = xgb.DMatrix(X_test)
    y_test['prediction'] = model.predict(d_test)
    print(train_end, y_test.corr())
    pd.to_pickle(y_test, path_dict['res_path'] + '%d.pkl' % train_end)
    print(path_dict['res_path'] + '%d.pkl' % train_end)
    return True


def make_base_dir(output_path):
    if not os.path.exists(output_path):
        os.mkdir((output_path))
    output_path = f'{output_path}/'
    path_dict = dict(
        res_path=output_path[:-1] + 'res/',
        val_path=output_path[:-1] + 'val_pred_path/',
        model_conf_path=output_path[:-1] + 'model_conf/',
        feature_path=output_path[:-1] + 'feature_path/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])


def main():
    factor_num = 400

    idx_list = list(range(73))  # [::-1]

    from multiprocessing import Pool
    import shutil

    pool = Pool(5)

    bar = tqdm(total=73 * 3)

    def update(*p):
        bar.update()
        if bar.last_print_n >= bar.total:
            bar.close()

    res_dict = {}
    for idx in idx_list:
        for fix_eval_indicator in ['ic_half_d', 'ic_half_t', 'ic_half_c']:
            out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelReCheck/XGBSelectBestPastTop_fix_eval_{fix_eval_indicator}_{factor_num}/'
            # fit_model(idx, out_path, fix_eval_indicator, factor_num)
            res_dict[(idx, fix_eval_indicator)] = pool.apply_async(fit_model, (idx, out_path, fix_eval_indicator, factor_num), callback=update)
        # process = Process(target=fit_model, args=(idx, out_path, eval_indicator, factor_num,time_point,frq))
        # process.start()
        # process.join()
        # gc.collect()
    pool.close()
    pool.join()
    for each in res_dict:
        res_dict[each] = res_dict[each].get()


main()
# idx_list = range(73)
# split_idx_list = [idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3] for i in range(3)]
# split_idx_list = list(zip(*tuple(split_idx_list)))
# for idx_list in split_idx_list[::-1]:
#     for idx in idx_list:
#         process = Process(target=fit_model,args=(idx,out_path,eval_indicator,factor_num))
#         process.start()
#         process.join()
#         gc.collect()

#################
# import pandas as pd
# import os
#
# val_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelReCheck/XGBRecheck_fix_eval_ic_half_c_400/val_pred_path/'
# file_list = sorted(os.listdir(val_path))
# val_pred_corr = {}
# for each in file_list:
#     val_pred_corr[int(each[:-4])] = pd.read_pickle(val_path+each)#.corr()
#     val_pred_corr[int(each[:-4])].columns = [x[:14] for x in val_pred_corr[int(each[:-4])].columns]
#     val_pred_corr[int(each[:-4])] = val_pred_corr[int(each[:-4])].corr()
# val_pred_corr = pd.Panel(val_pred_corr)
# actual_label_corr = val_pred_corr.minor_xs('actual_label').T
# prediction_corr = val_pred_corr.minor_xs('prediction').T



