# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')

import xgboost as xgb
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from tqdm import tqdm
from dataApi.FixFactorRollPrepare import load_dataset_from_multiple_add_selfdefine_label
import os, time, gc
import pandas as pd
from StrongStockModel.conf.path_config import root_path
import numpy as np
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date
import datetime



def get_dataset(train_idx, test_idx, fix_factor_lists,feature_addresses,label_path):
    # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
    #                                load_address=self.feature_address)
    gc.collect()
    e = time.time()
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        train_feature, train_label = load_dataset_from_multiple_add_selfdefine_label(train_idx[0],
                                        get_pre_trade_date(train_idx[-1]), fix_factor_lists, feature_addresses,label_path=label_path,return_1day_label=True)
    else:
        train_feature, train_label = load_dataset_from_multiple_add_selfdefine_label(train_idx[0],
                                        train_idx[-1], fix_factor_lists, feature_addresses,label_path=label_path,return_1day_label=True)
    if morning:
        today = get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))
    else:
        today = get_recent_trade_date()
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        test_feature, test_label = pd.DataFrame(), pd.DataFrame()
    else:
        if test_idx[-1] >= today:
            test_feature, test_label = load_dataset_from_multiple_add_selfdefine_label(test_idx[0],
                                today, fix_factor_lists, feature_addresses,tail_no_future=True,label_path=label_path,return_1day_label=True)
        else:
            test_feature, test_label = load_dataset_from_multiple_add_selfdefine_label(test_idx[0],
                                test_idx[-1], fix_factor_lists, feature_addresses,label_path=label_path,return_1day_label=True)
    print(train_feature.index[-1:],test_feature.index[-1:])
    return train_feature, train_label, test_feature, test_label, time.time() - e

class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None
                 ,label_path=None,future_bar_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)
        if label_path is None or future_bar_num is None:
            self.label_path = None
        else:
            self.label_path = f'{label_path}/future_{future_bar_num}_bar.npy'
        self.future_bar_num = future_bar_num

    def get_fix_factor_evaluation(self, num, end_index):
        restrict_path = '/data/group/800442/800319/junkData/StrongStock//external_data/problem_factor/'
        file_list = sorted(list(filter(lambda x: x <= f'{end_index}.pkl', os.listdir(restrict_path))))
        if file_list:
            unavailable_factor = pd.read_pickle(f'{restrict_path}{file_list[-1]}')
        else:
            unavailable_factor = []
        print(f'unavailable {unavailable_factor}')
        # inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list)) - set(unavailable_factor))
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/FutureBarBy30Min_8bar/Future_{self.future_bar_num}_bar/{self.eval_indicator}.pkl')
        print(f'{root_path}external_data/FutureBarBy30Min_8bar/Future_{self.future_bar_num}_bar/{self.eval_indicator}.pkl')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list))-set(unavailable_factor))
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
            model.set_param('predictor', 'cpu_predictor')
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            if not os.path.exists(params['model_conf_path']):
                os.mkdir(params['model_conf_path'])
            ########################
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000]['actual_label'])
            d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:]['actual_label'])
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
                fix_factor_list = sorted(list(set(map(lambda x : x[:-2],fix_factor_list))))
            else:
                fix_factor_list = self.get_fix_factor_evaluation(factor_nums//2, train_end_idx)
            # fix_factor_list = self.get_fix_factor_evaluation(factor_nums//2, train_end_idx)
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 [fix_factor_list,fix_factor_list],self.feature_address,self.label_path)
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
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label

import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i, indicator,future_bar_num,label_path):
    train_period = 200
    test_period = 10
    factor_num = 400
    target_file = 'XGB_SWMean_%s_train%d_test%d_factor_num%d' % (indicator, train_period, test_period, factor_num)
    out_file =f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{future_bar_num}_bar/{target_file}/{target_file}.pkl'
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    # test_end = 20220317
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(out_file, 'exist')
        # return
    print(out_file)

    best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = XGBRegressionFactorEvalYearly(train_start, test_end, None,
                                          feature_address=['/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                                    '/data/group/800442/800319/HFfactor/CrossIndutryMeanShift/data/'],
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num,label_path=label_path,future_bar_num=future_bar_num)
    import shutil
    for each in ['idx_date.npy','idx_time.npy','idx_code.npy','future.npy','nolimit.npy']:
        shutil.copy(f'/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/{each}',
                    f'/data/group/800442/800319/HFfactor/CrossIndutryMeanShift/data/{each}')
    if not os.path.exists(best_param_clf_xgb['model_conf_path']):
        os.mkdir(best_param_clf_xgb['model_conf_path'])
    if not os.path.exists(best_param_clf_xgb['feature_path']):
        os.mkdir(best_param_clf_xgb['feature_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=len(get_date_range(train_start,train_end)),
                                            predict_period=len(get_date_range(test_start,test_end)),
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(label.index[-1:],base_dir + '%d.pkl' % train_end)


from dataApi.sendInfo import send_message


train_start, train_end, test_start, test_end = para_list[-1][1]
hour = datetime.datetime.now().hour
if hour > 12:
    morning = False
else:
    morning = True
# morning = True
if train_end == test_start and train_end == test_end:
    if morning:
        idx = -2
    else:
        idx = -1
else:
    idx = -1
idx += len(para_list)
print(morning)
print(para_list[idx])
# idx = -1
idx_list = [idx]#list(range(147))[24:][::-1][:1]

for i in tqdm(idx_list):
    for f_bar in tqdm(list(range(1, 9))[::-1]):
        for ind_name in ['ic_d','ic_t','ic_c']:
            main_window_search(i, ind_name,f_bar,label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/')
            gc.collect()

send_message(['015664'],'XGBMatrix NonFix')


# idx_list = list(range(134))[24:][::-1]
# idx_list = list(range(134,152))[::-1]
# for f_bar in tqdm(list(range(1,9))[::-1]):
#     for i in tqdm(idx_list):
#         for ind_name in ['ic_d','ic_t','ic_c']:
#             main_window_search(i, ind_name,f_bar,label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/')
#             gc.collect()
# send_message(['015664'],'XGBMatrix done')