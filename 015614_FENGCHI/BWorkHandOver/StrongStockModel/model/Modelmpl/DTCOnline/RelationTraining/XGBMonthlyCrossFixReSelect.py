# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import xgboost as xgb
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from tqdm import tqdm
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
import os, time, gc
import pandas as pd
from StrongStockModel.conf.path_config import root_path
import numpy as np
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date
import datetime

class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
        #                                load_address=self.feature_address)
        gc.collect()
        e = time.time()
        if train_idx[1] <= 20210812:
            factor_direction = pd.read_pickle('/data/group/800442/800319/strategy_local_path/factor_direction_before20210813.pkl')[fix_factor_list].values
            print('using factor direction old part neg')
        else:
            factor_direction = pd.read_pickle('/data/group/800442/800319/strategy_local_path/factor_direction.pkl')[fix_factor_list].values
            print('using factor direction all pos')
        print(f'min direction {factor_direction.min()}')

        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], get_pre_trade_date(train_idx[-1]),
                                                                                                                      fix_factor_list,address=self.feature_address)
        else:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], train_idx[-1], fix_factor_list,address=self.feature_address)
        train_feature, train_label, train_idx_date, train_idx_time, train_idx_code = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                         train_idx_time, train_idx_code)
        train_feature = train_feature * factor_direction
        index_train = pd.MultiIndex.from_tuples(list(zip(train_idx_date.tolist(), train_idx_time.tolist(), train_idx_code.tolist())))
        train_feature, train_label = pd.DataFrame(train_feature, index=index_train, columns=fix_factor_list), pd.DataFrame({'actual_label': train_label}, index=index_train)

        today = int(datetime.date.today().strftime('%Y%m%d'))
        today = get_recent_trade_date(today)
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            test_feature, test_label = pd.DataFrame(columns=fix_factor_list), pd.DataFrame(columns=fix_factor_list)
        else:
            if test_idx[-1] >= today:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=get_pre_trade_date(today),
                                                                                                                    factor_list=fix_factor_list, return_idx=True,address=self.feature_address)
            else:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=test_idx[-1],
                                                                                                                    factor_list=fix_factor_list, return_idx=True,address=self.feature_address)
            test_nolimit[np.isnan(test_label)] = True
            test_label[np.isnan(test_label)] = 0
            test_feature, test_label, test_idx_date, test_idx_time, test_idx_code = feature_engineering(test_feature, test_label, test_nolimit,
                                                                                                        test_idx_date,test_idx_time,test_idx_code)
            test_feature = test_feature * factor_direction
            index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))
            test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=fix_factor_list), pd.DataFrame({'actual_label': test_label}, index=index_test)

        return train_feature, train_label, test_feature, test_label, time.time() - e


    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_sw1_cross_norm/{self.eval_indicator}.pkl')
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
    factor_num = 400

    out_file = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_%s_train%d_test%d_factor_num%d.pkl' % (
        indicator, train_period, test_period, factor_num)
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)

    best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollCrosslize/data/',
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
    for ind_name in ['ic_d','ic_t','ic_c']:
        # for ind_name in ['top_ret'][::-1]:
        main_window_search(i, ind_name)