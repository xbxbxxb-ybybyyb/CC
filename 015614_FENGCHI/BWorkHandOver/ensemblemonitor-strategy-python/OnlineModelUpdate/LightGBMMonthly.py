# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : CatMonthly.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import lightgbm as lgb
import os, gc, time, datetime
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from sklearn.externals import joblib
from StrongStockModel.conf.path_config import root_path
from dataApi.tradeDate import get_date_range
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

    def predict(self, model, X_test, end_date=None):
        pre_label = model.predict(X_test)
        return pre_label

    def train_model(self, X_train, y_train, params, end_date=None):
        key_list = set(params.keys()).intersection(
            set(['boosting_type', 'class_weight', 'colsample_bytree', 'importance_type', 'learning_rate',
                 'max_depth', 'min_child_samples', 'min_child_weight', 'min_split_gain',
                 'n_estimators', 'n_jobs', 'num_leaves', 'objective', 'random_state',
                 'reg_alpha', 'reg_lambda', 'silent', 'subsample', 'subsample_for_bin', 'subsample_freq']))

        args_param = {x: params[x] for x in key_list}

        print(args_param)
        date_list = get_date_range(X_train.index[0][0], end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]

        date_list = list(set(date_list) - set(val_date))

        factor_list = X_train.columns.tolist()
        pd.to_pickle(factor_list, params['feature_path'] + '%d.pkl' % end_date)

        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.json' % end_date):

            model = joblib.load(params['model_conf_path'] + '%d.pkl' % end_date)
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            if not os.path.exists(params['model_conf_path']):
                os.mkdir(params['model_conf_path'])
            ########################
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]

            model = lgb.LGBMRegressor()
            model.set_params(**args_param)
            model.fit(X=train_features[:-50000], y=train_label[:-50000]['actual_label'],
                      eval_set=[(train_features[-50000:], train_label[-50000:]['actual_label'])],
                      verbose=True,early_stopping_rounds=15)
            joblib.dump(model, params['model_conf_path'] + '%d.pkl' % end_date)
            print(params['model_conf_path'] + '%d.json' % end_date)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date[1:]], y_train.loc[val_date[1:]]
            # d_val = model.predict(val_features)
            val_labels['prediction'] = model.predict(val_features)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        return model

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
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
            if os.path.exists(params['feature_path'] + '%d.pkl' % train_end_idx):
                fix_factor_list = pd.read_pickle(params['feature_path'] + '%d.pkl' % train_end_idx)
            else:
                fix_factor_list = self.get_fix_factor_evaluation(factor_nums, train_end_idx)
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, label_param, kernel=kernel)
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

    out_file = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightEarlyStopV4FactorList_%s_train%d_test%d_factor_num%d.pkl' % (
        indicator, train_period, test_period, factor_num)
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)

    best_param_clf_xgb = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.45, 'importance_type': 'split', 'learning_rate': 0.01, 'max_depth': -1,
                          'min_child_samples': 20, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 100, 'n_jobs': -1, 'num_leaves': 400,
                          'objective': 'regression', 'random_state': None, 'reg_alpha': 0.0, 'reg_lambda': 0.0, 'silent': True, 'subsample': 1.0, 'subsample_for_bin': 200000,
                          'subsample_freq': 0}

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

# import datetime
#
# if datetime.datetime.now()>datetime.datetime(2021, 9, 7, 6, 0, 49, 694356):
#     pass
# else:
#     from xquant.compute.aimr import AIMR
#
#     i = int(AIMR.getParam())
#
#     for ind_name in ['ic_t']:#['ic_dt', 'ic_tc', 'ic_dtc']:
#         # for ind_name in ['top_ret'][::-1]:
#         main_window_search(i, ind_name)



idx_list = list(range(138))[24:]
for i in tqdm(idx_list):
    for ind_name in ['ic_t']:#['ic_dt', 'ic_tc', 'ic_dtc']:
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
