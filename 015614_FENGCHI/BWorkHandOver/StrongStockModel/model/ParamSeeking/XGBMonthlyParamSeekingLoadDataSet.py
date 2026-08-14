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
from dataApi.tradeDate import get_date_range
from tqdm import tqdm


class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{self.eval_indicator}.pkl')
        restrict_path = '/data/group/800442/800319/junkData/StrongStock//external_data/problem_factor/'
        file_list = sorted(list(filter(lambda x : x<=f'{end_index}.pkl',os.listdir(restrict_path))))
        if file_list:
            unavailable_factor = pd.read_pickle(f'{restrict_path}{file_list[-1]}')
        else:
            unavailable_factor = []
        print(f'unavailable {unavailable_factor}')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list)) - set(unavailable_factor))
        factor_evaluation = factor_evaluation[inter_col]
        target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index.tolist())))
        print(f'target eval date {target_date}')
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
        _,cell_idx = rolling_train_test_idx_list[0]
        train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
            cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
        print(train_start_idx, train_end_idx, test_start_idx, test_end_idx)
        fix_factor_list = self.get_fix_factor_evaluation(factor_nums, train_end_idx)
        X_train, y_train, X_test, y_test, feature_engineering_time = \
            self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                             fix_factor_list, None, label_methodology, label_param, kernel=kernel)
        gc.collect()
        return X_train, y_train, X_test, y_test


from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(indicator,base_dir):
    train_period = 100
    test_period = 100
    factor_num = 400
    train_start, test_end = 20170101,20171231
    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num)

    X_train, y_train, X_test, y_test = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)

    if not os.path.exists(f'{base_dir}/'):
        os.makedirs(base_dir)
    pd.to_pickle([X_train, y_train, X_test, y_test],f'{base_dir}/{indicator}_{train_start}_{test_end}.pkl')
    print(f'{base_dir}/{indicator}_{train_start}_{test_end}.pkl')

for ind_name in ['ic_d','ic_c', 'ic_t']:
    # for ind_name in ['top_ret'][::-1]:
    b_dir = f'/data/user/015664/AFuckingTrigger/ParamSeeking/XGB20220427/{ind_name}/'
    main_window_search(ind_name,b_dir)

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



