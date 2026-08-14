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
from StrongStockModel.model.Modelmpl.DTCOnline.DoubleEnsemble.DoubleEnsemble import SR
from StrongStockModel.conf.path_config import root_path
from dataApi.tradeDate import get_date_range
from tqdm import tqdm
import numpy as np




class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)


    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(root_path + 'external_data/ic_half.pkl')  # .set_index('name')
        factor_evaluation = pd.DataFrame(factor_evaluation)
        if not self.eval_indicator in factor_evaluation.index.levels[0]:
            raise Exception('Unavailable indicator')
        factor_evaluation = factor_evaluation.loc[self.eval_indicator]
        target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index)))
        factor_evaluation = factor_evaluation.loc[target_date]
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
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

        if False:#'load local model' in params and os.path.exists(params['model_conf_path'] + '%d/model_%d.json' % (end_date,params['n_estimators'])):
            model = xgb.Booster(args_param)
            model.load_model(params['model_conf_path'] + '%d/model_%d.json' % (end_date,params['n_estimators']))
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            if not os.path.exists(params['model_conf_path']):
                os.mkdir(params['model_conf_path'])
            if not os.path.exists(params['model_conf_path'] + '%d/' % end_date):
                os.mkdir(params['model_conf_path'] + '%d/' % end_date)
            ########################
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            # pd.to_pickle([train_features,train_label,params],'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/backup_data/round_1.pkl')

            # d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)
            if params['round_num']>0:
                # os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
                d_train = xgb.DMatrix(train_features, label=train_label.values)
                res = []
                pre_model_path = params['model_conf_path'].replace('round_%d'%params['round_num'],'round_%d'%(params['round_num']-1))
                # params['model_conf_path'].replace('round_%d' % params['round_num'], 'round_%d' % (params['round_num'] - 1)) + '%d/' % end_date
                print(f'calc SR from {pre_model_path}')
                model_len = len(os.listdir(f'{pre_model_path}{train_end}/'))
                for i in range(1,model_len+1):
                    model = xgb.Booster(model_file=  f'{pre_model_path}{train_end}/model_{i}.json' )
                    model.set_param({'predictor':'cpu_predictor'})
                    res.append(model.predict(d_train)[None,:])
                res = np.concatenate(tuple(res))
                res = pd.DataFrame((res - train_label.values[:,0])**2,index=list(range(1,model_len+1)),columns=train_label.index)
                sample_weight = SR(res,alpha1=0,alpha2=1,gamma=0.5,bin_num = params['bin_num'],k=params['round_num'])
                del d_train
                gc.collect()
                os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
            else:
                sample_weight = None

            if sample_weight is None:
                d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000].values)
                d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)
            else:
                d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000].values,weight=sample_weight[:-50000])
                d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)
            check_point = xgb.callback.TrainingCheckPoint(params['model_conf_path'] + '%d/' % end_date,iterations=1)
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'],callbacks=[check_point],evals=[(d_eval,'d_eval')],early_stopping_rounds=15)
            final = len(os.listdir(params['model_conf_path'] + '%d/' % end_date))+1
            model.save_model(params['model_conf_path'] + '%d/model_%d.json' % (end_date,final))
            print(params['model_conf_path'] + '%d.json' % end_date)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date[1:]], y_train.loc[val_date[1:]]
            d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(d_val)
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

def main_window_search(i,round_num, indicator):
    train_period = 200
    test_period = 10
    factor_num = 400
    N = 40
    # indicator = 'ic_all_dtc'

    #######in smaple
    # all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d_and_binary/' % N
    # model = XGBRegressionFactorEval(20150309, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path,factor_eval_indicator=indicator)
    # out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
    # indicator, train_period, test_period, factor_num, N)

    # out sample

    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_%s_train%d_test%d_factor%d.pkl' % (
        indicator, train_period, test_period, factor_num)
    out_file = out_file.replace('.pkl', '/')
    if not os.path.exists(out_file):
        os.mkdir(out_file)
    if not os.path.exists(out_file+'round_%d/'%round_num):
        os.mkdir(out_file+'round_%d/'%round_num)
    out_file = out_file+'round_%d/round_%d.pkl'%(round_num,round_num)
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)
    # best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'max_depth': 4, 'nthread': -1, 'scale_pos_weight': 1,
    #                       'subsample': 1, 'tree_method': 'gpu_hist', 'sampling_method': 'gradient_based','n_estimators':100}
    best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist','bin_num':1000,'round_num':round_num}
    # best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/',
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
    # lm.sendMessage(indicator + " " + out_file)

import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

from xquant.compute.aimr import AIMR

# idx = int(AIMR.getParam())
# main_window_search(idx)
ind_name ='ic_half_c'
gpu_id = '1'
os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
for round_id in range(6):
    for i in tqdm(list(range(73,123))):
        main_window_search(i,round_id, ind_name)
        gc.collect()
# lm = link.LinkMessage()
# lm.sendMessage('%s done'%ind_name)

# for i in [129]:
#     for ind_name in ['ic_half_d', 'ic_half_t', 'ic_half_c'][::-1]:
#         main_window_search(i, ind_name),