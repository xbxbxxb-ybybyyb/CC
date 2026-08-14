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
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
from FactorEvaluation.DailyFactorFixEvaluation.FixlizeDailyFactorLoading import loadFixlizedDailyFactor
from StrongStockModel.conf.path_config import root_path
import numpy as np
import configparser
from StrongStockModel.model.Modelmpl.DTCOnline.DoubleEnsemble.DoubleEnsemble import SR
from multiprocessing import Pool

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                      'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                      'subsample': 0.8, 'tree_method': 'gpu_hist'}
using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
available_factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))
using_factor_list = sorted(list(set(using_factor_list).intersection(set(available_factor_list))))

def get_model(file_name):
    model = xgb.Booster(model_file=file_name)
    model.set_param('predictor','cpu_predictor')
    return model

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
    res = pd.read_excel('/data/user/015664/AFuckingTrigger/DailyFactotrFixEvaluation2_res/结果汇总.xlsx', sheet_name='ic_abs', index_col=0)
    col = list(filter(lambda x: eval_indicator in x, res.columns.tolist()))
    col = list(filter(lambda x: x < f'{eval_indicator}_{end_index}', col))
    col = max(col)
    indicator_value = res[col].apply(abs).sort_values(ascending=False)
    return indicator_value.index.tolist()[:num]


def load_dataset(start_date, end_date, fix_factor_list, daily_factor_list):
    X_train, y_train, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=start_date, end_date=end_date, factor_list=fix_factor_list)
    X_train_daily, index_daily = loadFixlizedDailyFactor(daily_factor_list, start_date, end_date)
    X_train_daily = X_train_daily.reshape((X_train_daily.shape[0] // 7, 7, X_train_daily.shape[1])).transpose(2, 0, 1)
    X_train = np.concatenate((X_train, X_train_daily), axis=0)
    del X_train_daily
    gc.collect()
    X_train, y_train, idx_date, idx_time, idx_code = feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
    index_train = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
    daily_name_list = []
    for i, daily_f in enumerate(daily_factor_list):
        if daily_f in fix_factor_list:
            daily_name_list.append(daily_f + '_daily_involved_in_fix')
        else:
            daily_name_list.append(daily_f)
    X_train, y_train = pd.DataFrame(X_train, index=index_train, columns=fix_factor_list + daily_name_list), pd.DataFrame(y_train, index=index_train, columns=['actual_label'])
    return X_train, y_train


def fit_model(i, out_path, indicator_fix, indicator_daily, round_num, bin_num=1000):
    train_start, train_end, test_start, test_end = para_list[i][1]
    output_path = f'{out_path}/round_{round_num}/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)
        os.mkdir(output_path)
    path_dict = dict(
        res_path=output_path,
        val_path=output_path + 'val_pred/',
        model_conf_path=output_path + 'model_conf/',
        feature_eval_path=output_path + 'feature_eval/',
        feature_path=output_path + 'factor_list/',
        SR_res_path=output_path + 'SR_res_path/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    if os.path.exists(path_dict['res_path'] + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [3, 5, 7, 9, 11]]
    fix_factor_list = get_fix_factor_evaluation(200, train_end, eval_indicator=indicator_fix)
    daily_factor_list = get_daily_factor_evaluation(200, train_end, eval_indicator=indicator_daily)
    pd.to_pickle([fix_factor_list, daily_factor_list], path_dict['feature_path'] + '%d.pkl' % train_end)

    if True:  # not os.path.exists(path_dict['model_conf_path']+'%d.json'%train_end):
        if not os.path.exists(path_dict['model_conf_path'] + '%d/' % train_end):
            os.mkdir(path_dict['model_conf_path'] + '%d/' % train_end)

        X_train, y_train = load_dataset(date_list[0], date_list[-2], fix_factor_list, daily_factor_list)
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val, y_val = X_train.loc[val_date_list], y_train.loc[val_date_list]
        X_train, y_train = X_train.loc[date_list], y_train.loc[date_list]

        # d_eval = xgb.DMatrix(X_train[-50000:], label=y_train[-50000:].values)

        if round_num > 0:
            if os.path.exists(path_dict['SR_res_path'] + f'{train_end}.pkl'):
                res = pd.read_pickle(path_dict['SR_res_path'] + f'{train_end}.pkl')
            else:
                res = []
                d_train = xgb.DMatrix(X_train, label=y_train.values)
                pre_model_path = path_dict['model_conf_path'].replace('round_%d' % round_num, 'round_%d' % (round_num - 1))
                model_len = len(os.listdir(f'{pre_model_path}{train_end}/'))
                if model_len == 0:
                    return False
                model_dict = {}
                pool=Pool(min(10,model_len))
                for i in range(1, model_len + 1):
                    model_dict[i] = pool.apply_async(get_model,(f'{pre_model_path}{train_end}/model_{i}.json',))
                pool.close()
                pool.join()

                for i in range(1, model_len + 1):
                    # model = xgb.Booster(model_file=f'{pre_model_path}{train_end}/model_{i}.json')
                    # model.set_param({'predictor': 'cpu_predictor'})
                    res.append(model_dict[i].get().predict(d_train)[None, :])
                res = np.concatenate(tuple(res))
                res = pd.DataFrame((res - y_train.values[:, 0]) ** 2, index=list(range(1, model_len + 1)), columns=y_train.index)
                pd.to_pickle(res, path_dict['SR_res_path'] + f'{train_end}.pkl')
                del d_train
            # e = time.time()
            # sample_weight = SR(res, alpha1=0, alpha2=1, gamma=0.5, bin_num=bin_num, k=round_num)
            # print('SR', time.time() - e)
        else:
            sample_weight = None
    return True

def wrapper(*p):
    res = fit_model(*p)
    gc.collect()
    return res


pool = Pool(4)

bar = tqdm(total=73 * 2)


def update(*p):
    if bar.last_print_n < bar.total:
        bar.update()
    else:
        bar.close()


i = 0
os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
idx_list = list(range(73))[::-1]
# res_dict = {}
# for round_num in range(3, 4):
#     for idx in idx_list:
#         fix_indicator, daily_indicator = 'ic_half_d', 'ic_d_half_year'
#         out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_{fix_indicator}_{daily_indicator}/'
#
#         # fit_model(idx, out_path, fix_indicator, daily_indicator, round_num, 1000)
#         res_dict[(idx, out_path, fix_indicator, daily_indicator, round_num, 1000)] = pool.apply_async(wrapper, (idx, out_path, fix_indicator, daily_indicator, round_num, 1000),
#                                                                                                       callback=update)
#         fix_indicator, daily_indicator = 'ic_half_c', 'ic_c_half_year'
#         out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_{fix_indicator}_{daily_indicator}/'
#         res_dict[(idx, out_path, fix_indicator, daily_indicator, round_num, 1000)] = pool.apply_async(wrapper, (idx, out_path, fix_indicator, daily_indicator, round_num, 1000),
#                                                                                                       callback=update)
#         # fit_model(idx, out_path, fix_indicator, daily_indicator, round_num, 1000)
# pool.close()
# pool.join()

#
#
# for each in res_dict:
#     res_dict[each] = res_dict[each].get()
# idx_list = idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3]
bar = tqdm(total=73*2)
for round_num in range(3, 4):
    for idx in tqdm(idx_list):
        fix_indicator, daily_indicator = 'ic_half_d', 'ic_d_half_year'
        out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_{fix_indicator}_{daily_indicator}/'

        fit_model(idx, out_path, fix_indicator, daily_indicator, round_num, 1000)
        bar.update()
        fix_indicator, daily_indicator = 'ic_half_c', 'ic_c_half_year'
        out_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_{fix_indicator}_{daily_indicator}/'

        fit_model(idx, out_path, fix_indicator, daily_indicator, round_num, 1000)
        bar.update()
        gc.collect()
# process = Process(target=fit_model,args=(idx,out_path,'ic_half_c','ic_c_half_year'))
# process.start()
# process.join()
# gc.collect()

# idx_list = range(73)
# split_idx_list = [idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3] for i in range(3)]
# split_idx_list = list(zip(*tuple(split_idx_list)))
# for idx_list in split_idx_list[::-1]:
#     for idx in idx_list:
#         process = Process(target=fit_model,args=(idx,out_path))
#         process.start()
#         process.join()


