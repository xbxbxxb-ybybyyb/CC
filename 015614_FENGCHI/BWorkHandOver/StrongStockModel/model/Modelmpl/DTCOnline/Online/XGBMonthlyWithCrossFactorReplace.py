# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from xgboost import XGBRegressor
import xgboost as xgb
import os, gc, time, datetime
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from StrongStockModel.conf.model_param_config import best_param_clf_xgb
from StrongStockModel.conf.path_config import root_path
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
from dataApi.tradeDate import get_date_range,get_pre_trade_date
# from dataApi.LoadingTool import load_cross_factor
import numpy as np
from tqdm import tqdm


class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{self.eval_indicator}.pkl')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list)))
        factor_evaluation = factor_evaluation[inter_col]
        target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index.tolist())))
        if 'ret' in self.eval_indicator:
            print('ret')
            factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
        elif 'ic' in self.eval_indicator:
            print('ic')
            factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
        else:
            raise Exception('')
        factor_list = factor_evaluation.index.tolist()[:num]
        return sorted(factor_list)

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        e = time.time()
        col_list = fix_factor_list+interday_factor
        inter_factor = set(fix_factor_list).intersection(interday_factor)
        if interday_factor:
            for each in inter_factor:
                col_list[len(fix_factor_list)+interday_factor.index(each)] = each+'_cross'

        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], get_pre_trade_date(train_idx[-1]),
                                                                                                                      fix_factor_list)

            train_cross_feature,train_cross_label,nolimit_cross,train_idx_date_cross, train_idx_code_cross, train_idx_time_cross = \
                load_fix_data(train_idx[0], get_pre_trade_date(train_idx[-1]),interday_factor,address='/data/group/800442/800319/HFfactor/CrossFactor/data/')
        else:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], train_idx[-1], fix_factor_list)
            train_cross_feature, train_cross_label, nolimit_cross, train_idx_date_cross, train_idx_code_cross, train_idx_time_cross = \
                load_fix_data(train_idx[0], train_idx[-1], interday_factor, address='/data/group/800442/800319/HFfactor/CrossFactor/data/')

        train_feature = np.concatenate((train_feature,train_cross_feature),axis=0)
        train_feature, train_label, train_idx_date, train_idx_time, train_idx_code = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                         train_idx_time, train_idx_code)

        index_train = pd.MultiIndex.from_tuples(list(zip(train_idx_date.tolist(), train_idx_time.tolist(), train_idx_code.tolist())))
        train_feature, train_label = pd.DataFrame(train_feature, index=index_train, columns=col_list), pd.DataFrame({'actual_label': train_label}, index=index_train)

        # cross_factor = train_feature[interday_factor]
        # cross_factor_real = load_cross_factor(interday_factor[0],start=train_idx[0],end=train_idx[-1],
        #                                 address='/arch1/group/800442/800319/AAcross/factor_result/1min/20140701_20210531/xq/',return_type='df')
        # val =cross_factor_real.stack().loc[[train_idx[0]]]
        # a = dict(factor_name=interday_factor[0],start=train_idx[0],end=train_idx[-1],
        #                                 address='/arch1/group/800442/800319/AAcross/factor_result/1min/20140701_20210531/xq/',return_type='df')
        # compare = pd.DataFrame({'real':val,'reload':cross_factor[interday_factor[0]].loc[[train_idx[0]]]})
        today = int(datetime.date.today().strftime('%Y%m%d'))

        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            test_feature, test_label = pd.DataFrame(columns=col_list), pd.DataFrame(columns=['actual_label'])
        else:
            if test_idx[-1] >= today:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=get_pre_trade_date(today),
                                                                                                                    factor_list=fix_factor_list, return_idx=True)
                test_cross_feature, _, _, _, _, _ = \
                    load_fix_data(start_date=test_idx[0], end_date=get_pre_trade_date(today),factor_list=interday_factor, return_idx=True, address='/data/group/800442/800319/HFfactor/CrossFactor/data/')


            else:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=test_idx[-1],
                                                                                                                    factor_list=fix_factor_list, return_idx=True)
                test_cross_feature, _, _, _, _, _ = \
                    load_fix_data(start_date=test_idx[0], end_date=test_idx[-1],factor_list=interday_factor, return_idx=True,
                                  address='/data/group/800442/800319/HFfactor/CrossFactor/data/')

            # test_label = np.concatenate((test_label, np.zeros((test_feature.shape[1] - test_label.shape[0], 7))))
            test_feature = np.concatenate((test_feature,test_cross_feature),axis=0)
            test_nolimit[np.isnan(test_label)] = True
            test_label[np.isnan(test_label)] = 0
            test_feature, test_label, test_idx_date, test_idx_time, test_idx_code = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
                                                                                                        test_idx_time,
                                                                                                        test_idx_code)
            if len(test_feature)>0:
                index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))

                test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=col_list), pd.DataFrame({'actual_label': test_label}, index=index_test)
            else:
                test_feature, test_label = pd.DataFrame(columns=col_list), pd.DataFrame(columns=['actual_label'])
        return train_feature, train_label, test_feature, test_label, time.time() - e

    def predict(self, model, X_test, end_date=None):
        dtest = xgb.DMatrix(X_test)
        pre_label = model.predict(dtest)
        return pre_label

    def train_model(self, X_train, y_train, params, end_date=None):
        key_list = set(params.keys()).intersection(
            set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
        args_param = {x: params[x] for x in key_list}
        train_end = sorted(list(set([x[0] for x in X_train.index])))[-1]

        print(args_param)
        date_list = get_date_range(X_train.index[0][0], end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]

        date_list = list(set(date_list) - set(val_date))

        factor_list = X_train.columns.tolist()
        pd.to_pickle(factor_list, params['feature_path'] + '%d.pkl' % end_date)

        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.json' % end_date):
            model = xgb.Booster(args_param)
            model.load_model(params['model_conf_path'] + '%d.json' % end_date)
            model.set_param('predictor','cpu_predictor')
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            if not os.path.exists(params['model_conf_path']):
                os.mkdir(params['model_conf_path'])
            ########################
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000].values)
            d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15, verbose_eval=False)
            eval_res = pd.DataFrame(
                {each: pd.Series(model.get_score(importance_type=each)) for each in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']}
            )
            if not os.path.exists(params['model_conf_path'] + '/eval_res/'):
                os.mkdir(params['model_conf_path'] + '/eval_res/')
            pd.to_pickle(eval_res, params['model_conf_path'] + f'/eval_res/{end_date}.pkl')

            model.save_model(params['model_conf_path'] + '%d.json' % end_date)
            print(params['model_conf_path'] + '%d.json' % end_date)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date[1:]], y_train.loc[val_date[1:]]
            d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(d_val)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(d_train)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date)
        return model

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10,cross_res_path='/arch1/group/800442/800319/AAcross/factor_result/1min/20140701_20210531/'):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None

        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])
            # if test_end_idx!= 20170607:
            #     continue

            cross_res_path = '/arch1/group/800442/800319/AAcross/factor_result_rerun3/1min/20140701_20210531/'
            cross_factor_list = []
            for each in os.listdir(cross_res_path):
                if each=='daily':
                    continue
                cross_factor_list += os.listdir(f'{cross_res_path}/{each}')
            cross_factor_list = list(filter(lambda x : os.path.exists(f'/data/group/800442/800319/HFfactor/CrossFactor/data/{x}'),cross_factor_list))
            print(f'cross {len(cross_factor_list)}')
            cross_factor_list = [x.replace('.npy', '') for x in cross_factor_list]

            fix_factor_list = self.get_fix_factor_evaluation(factor_nums, train_end_idx)





            label_param['cross_res_path'] = cross_res_path
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, cross_factor_list, label_methodology, label_param, kernel=kernel)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()

            if len(X_train) > 2000 and len(set(y_train[y_train.columns[0]])) > 1:
                print('re-train in this round')
                model = self.train_model(X_train, y_train, params, train_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test, train_end_idx)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label


from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i, indicator):
    train_period = 200
    test_period = 10
    factor_num = 200

    out_file = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_%s_train%d_test%d_factor_num%d.pkl' % (
        indicator, train_period, test_period, factor_num)
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if test_end>20210531:
        test_end = 20210531
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(out_file, 'exist')
        return
    print(out_file)

    best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num)
    if not os.path.exists(best_param_clf_xgb['model_conf_path']):
        os.mkdir(best_param_clf_xgb['model_conf_path'])
    if not os.path.exists(best_param_clf_xgb['feature_path']):
        os.mkdir(best_param_clf_xgb['feature_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)

for i in tqdm(list(range(134))[24:]):
    for ind_name in ['ic_d','ic_c', 'ic_t']:
        # for ind_name in ['top_ret'][::-1]:
        main_window_search(i, ind_name)



# import shutil,os
# from dataApi.sendInfo import send_message
# # os.mkdir('/arch0/group/800442/ExperimentParam/')
# factor_list_path = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_%s_train200_test10_factor_num400_factor_list/'
#
# for each in ['ic_c','ic_t','ic_d']:
#     shutil.copytree(factor_list_path%each,f'/arch0/group/800442/ExperimentParam/{each}_factor_list/')
#
# for each in ['ic_c','ic_t','ic_d']:
#     send_message(['015664','015836'],f'/arch0/group/800442/ExperimentParam/{each}_factor_list/')
#

from dataApi.sendInfo import  send_message

eval_res = [
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_d_train200_test10_factor_num400_model_conf/eval_res/'
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_t_train200_test10_factor_num400_model_conf/eval_res/'
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_c_train200_test10_factor_num400_model_conf/eval_res/'
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_d_train200_test10_factor_num200_model_conf/eval_res/'
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_t_train200_test10_factor_num200_model_conf/eval_res/'
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_c_train200_test10_factor_num200_model_conf/eval_res/'
]
send_message(['015664'],str(eval_res))