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
from xquant.factordata import FactorData

s = FactorData()
wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD', S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT', 'S_DQ_CLOSE']].set_index('TRADE_DT')
wind_a = wind_a.sort_index().loc['20151231':]
wind_a.index = wind_a.index.astype(int)
wind_a = wind_a['S_DQ_CLOSE'].sort_index().pct_change()



class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None,val_days=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)
        self.val_days = val_days
    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{self.eval_indicator}.pkl')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list)))
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
        period_wind_a = wind_a.loc[date_list[:-1]].sort_values()
        val_date = period_wind_a.iloc[list(range(5,199,10))].index.tolist()
        recent_5 = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]

        date_list = list(set(date_list) - set(val_date) - set(recent_5))

        factor_list = X_train.columns.tolist()
        pd.to_pickle(factor_list, params['feature_path'] + '%d.pkl' % end_date)

        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.json' % end_date):
            model = xgb.Booster(args_param)
            model.load_model(params['model_conf_path'] + '%d.json' % end_date)

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
        model.set_param('predictor', 'cpu_predictor')
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            recent_5_features,recent_5_label = X_train.loc[recent_5[1:]], y_train.loc[recent_5[1:]]
            d_recent_5 = xgb.DMatrix(recent_5_features)
            d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(d_val)
            recent_5_label['prediction'] = model.predict(d_recent_5)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
            if not os.path.exists(params['val_pred_path'][:-1]+'recent_5/'):
                os.mkdir(params['val_pred_path'][:-1]+'recent_5/')
            pd.to_pickle(recent_5_label,params['val_pred_path'][:-1]+f'recent_5/{end_date}.pkl')
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
    val_days = 20
    out_file = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_Val%d_%s_train%d_test%d_factor_num%d.pkl' % (
        val_days,indicator, train_period, test_period, factor_num)
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
    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num,val_days=val_days)
    if not os.path.exists(best_param_clf_xgb['model_conf_path']):
        os.mkdir(best_param_clf_xgb['model_conf_path'])
    if not os.path.exists(best_param_clf_xgb['feature_path']):
        os.mkdir(best_param_clf_xgb['feature_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)


train_start, train_end, test_start, test_end = para_list[-1][1]
hour = datetime.datetime.now().hour

from tqdm import tqdm
for i in tqdm(list(range(24,152))[::-1]):
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



