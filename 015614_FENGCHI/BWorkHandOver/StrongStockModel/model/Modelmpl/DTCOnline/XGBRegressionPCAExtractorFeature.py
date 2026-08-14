# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : XGBRegressionFactorEvalRollingSelectFactorWithNNExtractorFeature.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from xgboost import XGBRegressor
import xgboost as xgb
import os, gc, time, datetime
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from StrongStockModel.conf.path_config import root_path
from dataApi.tradeDate import get_date_range
from tqdm import tqdm


from keras.callbacks import *
from keras.layers import Dropout, Dense
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
import keras.backend as K
from keras.models import load_model


def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.mean((y_true - K.mean(y_true,axis=0))*(y_pred-K.mean(y_pred,axis=0)),axis=0)/( K.std(y_true,axis=0) * K.std(y_pred,axis=0))

def myloss(y_true_, y_pred_):

    corr = K_corr(y_true_, y_pred_)
    mean_corr = K.mean(corr)
    std_corr = K.std(corr)
    return 1 -0.5*mean_corr#+std_corr

# best_param_clf_nn = {'activation': 'relu',
#  'alpha': 9.756090506594905e-05,
#  'batch_size': 131072,
#  'dropout': 0.2,
#  'hidden_layer_sizes': (100,),
#  'learning_rate': 'adaptive',
#  'learning_rate_init': 0.1,
#  'momentum': 0.5,
#  'nb_epoch': 300,
#  'solver': 'sgd'}

best_param_clf_nn = {
    'activation': 'sigmoid',
    'alpha': 9.756090506594905e-05,
    'hidden_layer_sizes': (100,),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.15,#0.0703114914234283,
    'momentum': 0.1669382592981298, 'solver': 'sgd',
    'nb_epoch': 200,
    'batch_size': 2 ** 17
}
def NN(input_dim, params=best_param_clf_nn):
    print('CorrOnly')
    hidden_layer_sizes = params['hidden_layer_sizes']
    model = Sequential()
    model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
    for dim in hidden_layer_sizes[1:]:
        model.add(Dense(dim, activation=params['activation']))
    optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
    compile_model(model, optimizer, [])
    # print(model.summary())
    return model

def compile_model(model4compile, opt_er, metrics_eval):
    model4compile.compile(loss=myloss, \
                          optimizer=opt_er, metrics=metrics_eval)
    return model4compile

class XGBRegressionFactorEvalRollingSelectFactorWithNNExtractorFeature(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def get_fix_factor_evaluation(self, num,end_index):
        factor_evaluation = pd.read_pickle(root_path+'external_data/ic_half.pkl')#.set_index('name')
        factor_evaluation = pd.DataFrame(factor_evaluation)
        if not self.eval_indicator in factor_evaluation.index.levels[0]:
            raise Exception('Unavailable indicator')
        factor_evaluation = factor_evaluation.loc[self.eval_indicator]
        target_date = max(list(filter(lambda x :x<end_index,factor_evaluation.index)))
        factor_evaluation = factor_evaluation.loc[target_date]
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        self.sorted_fix_factor = factor_list.copy()
        return sorted(factor_list)

    def predict(self, model, X_test, end_date=None):

        feature_to_extract = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/NNExtractorSigmoid_%s_train200_test10_factor_num700_norm_window_40_feature_path/%d.pkl'%(self.eval_indicator,end_date))
        model,model_extracted = model
        extracted_test_feature = model_extracted.predict(X_test[feature_to_extract])
        factor_list = X_test.columns.tolist()
        feature_use_direct = sorted(list(set(factor_list) - set(feature_to_extract)))

        X_test = pd.concat([X_test[feature_use_direct],pd.DataFrame(extracted_test_feature,index=X_test.index)],axis=1)

        dtest = xgb.DMatrix(X_test)
        pre_label = model.predict(dtest)
        return pre_label

    def train_model(self, X_train, y_train, params, end_date=None):
        key_list = set(params.keys()).intersection(set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
        args_param = {x:params[x] for x in key_list}
        train_end = sorted(list(set([x[0] for x in X_train.index])))[-1]
        feature_to_extract = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/NNExtractorSigmoid_%s_train200_test10_factor_num700_norm_window_40_feature_path/%d.pkl'%(self.eval_indicator,end_date))
        print(args_param)
        date_list = get_date_range(X_train.index[0][0],end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]

        date_list = list(set(date_list) - set(val_date))

        factor_list = X_train.columns.tolist()
        pd.to_pickle(factor_list,params['feature_path']+'%d.pkl'%end_date)

        feature_use_direct = sorted(list(set(factor_list) - set(feature_to_extract)))
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        model_extracted = NN(len(feature_to_extract))
        model_extracted.load_weights(
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/NNExtractorSigmoid_%s_train200_test10_factor_num700_norm_window_40_model_conf/%d.h5' % (self.eval_indicator,end_date))

        extracted_train_feature = model_extracted.predict(X_train[feature_to_extract].values)

        X_train = pd.concat([X_train[feature_use_direct], pd.DataFrame(extracted_train_feature, index=X_train.index)], axis=1)
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

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

            gc.collect()
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'],evals=[(d_eval,'d_eval')],early_stopping_rounds=15,verbose_eval=False)
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
        return model,model_extracted

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
            fix_factor_list = self.get_fix_factor_evaluation(factor_nums,train_end_idx)
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
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i,indicator):
    train_period = 200
    test_period = 10
    factor_num = 700
    N = 40
    # indicator = 'ic_all_dtc'

    #######in smaple
    # all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d_and_binary/' % N
    # model = XGBRegressionFactorEval(20150309, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path,factor_eval_indicator=indicator)
    # out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
    # indicator, train_period, test_period, factor_num, N)

    # out sample

    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
        indicator, train_period, test_period, factor_num, N)
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
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
    # best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = XGBRegressionFactorEvalRollingSelectFactorWithNNExtractorFeature(train_start, test_end, None, feature_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/',
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


from xquant.compute.aimr import AIMR

#idx = int(AIMR.getParam())
#main_window_search(idx)
# ind_name = 'ic_half_t'
# for i in list(range(74)):
#      main_window_search(i,ind_name)
#      gc.collect()
# lm = link.LinkMessage()
# lm.sendMessage('%s done'%ind_name)


# idx_list = list(range(73))
# i=0
# idx_list = idx_list[len(idx_list)*i//3 + 1:len(idx_list)*(i+1)//3]
# print(idx_list)
# for idx in idx_list:
#     main_window_search(idx, 'ic_half_dtc')
#     gc.collect()



# main_window_search(48, 'ic_half_t')
idx_list = list(range(73))
idx_list_list = [idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3] for i in range(3)]
idx_list = list(zip(*tuple(idx_list_list)))
for idx_tuple in idx_list[::-1]:
    for idx in idx_tuple:
        main_window_search(idx, 'ic_half_dtc')
        gc.collect()
