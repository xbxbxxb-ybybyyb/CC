# @Time : 2021/7/16 10:07
# @Author : Zhichen Lu
# @File : NNExtractorAll.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from keras.callbacks import *
from keras.layers import Dropout, Dense,BatchNormalization
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
import os,time,gc,datetime
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from xquant.compute.aimr import AIMR

# y_true_ = train_label[:10000].values
# y_pred_ = model.predict(train_features[:10000].values)
def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.mean((y_true - K.mean(y_true,axis=0))*(y_pred-K.mean(y_pred,axis=0)),axis=0)/( K.std(y_true,axis=0) * K.std(y_pred,axis=0))

def myloss(y_true_, y_pred_):

    corr = K_corr(y_true_, y_pred_)
    mean_corr = K.mean(corr)
    # std_corr = K.std(corr)
    return 1 - mean_corr#+std_corr
    # y_true, y_pred = K.cast(y_true_,dtype='float32'),K.cast(y_pred_,dtype='float32')
    # return mean_squared_error(y_pred,y_true) + 2*K_corr(y_true_,y_pred_)


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
    'hidden_layer_sizes': (200,100),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.2,#0.0703114914234283,
    'momentum': 0.5, 'solver': 'sgd',
    'nb_epoch': 200,
    'batch_size': 2 ** 19
}


class NN_redefine(ModelNewLoading):

    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address='/data//group/800442/800319/LittleJunkFix/', factor_eval_indicator=None, factor_num=None):
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

    def NN(self, input_dim, params):
        print('CorrOnly')
        hidden_layer_sizes = params['hidden_layer_sizes']
        model = Sequential()
        model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
        model.add(BatchNormalization(momentum=0.5))
        for dim in hidden_layer_sizes[1:]:
            model.add(Dense(dim, activation=params['activation']))
        optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
        self.compile_model(model, optimizer, [])
        # print(model.summary())
        return model

    def compile_model(self, model4compile, opt_er, metrics_eval):
        model4compile.compile(loss=myloss, \
                              optimizer=opt_er, metrics=metrics_eval)
        return model4compile

    def train_model(self, X_train, y_train, params, end_date=None):
        if not os.path.exists(params['train_log_path']):
            os.mkdir(params['train_log_path'])
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        if not os.path.exists(params['feature_path']):
            os.mkdir(params['feature_path'])
        pd.to_pickle(X_train.columns.tolist(),params['feature_path']+'%d.pkl'%end_date)
        model = self.NN(input_dim=X_train.shape[1], params=params)
        early_stopping = EarlyStopping(monitor='val_loss', patience=15)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=5, min_lr=0.001)
        train_log = CSVLogger(params['train_log_path'] + '%d.csv' % end_date)
        callbacks_list = [early_stopping, reduce_lr, train_log]
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.h5' % end_date):
            model.load_weights(params['model_conf_path'] + '%d.h5' % end_date)
            print('load model from local')
        else:
            model.fit(X_train.values, y_train.values, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=1, \
                      shuffle=True, callbacks=callbacks_list, validation_split=0.1)
            model.save_weights(params['model_conf_path'] + '%d.h5' % end_date)

        return model

    def predict(self, model, X_test, end_date_idx=None):
        pre_label = model.predict(X_test.values)
        return pre_label

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = (pd.DataFrame(),pd.DataFrame())
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
                model = self.train_model(X_train, y_train, params, test_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test, train_end_idx)
                pred_label = pd.DataFrame(pred_label,index=y_test.index)
                # pred_label['actual_label'] = y_test['actual_label']
                corr = pred_label.corrwith(y_test[y_test.columns[0]]).apply(abs)
                print('ic_mean',corr.mean(),'ic_max',corr.max(),'ic_min',corr.min())
                label = (pd.concat([label[0],pred_label]),pd.concat([label[1],y_test]))
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label


import configparser

conf = configparser.ConfigParser()
conf.read('/data//group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

def main(i):
    train_period = 100
    test_period = 200
    factor_num = 800
    indicator = 'ic_d'
    tag = 'NNExtractor_%s_train%d_test%d_factor_num%d' % (indicator, train_period, test_period, factor_num)
    out_file = f'/data/group/800442/800319/Strong_stock/C3PO/{tag}/{tag}.pkl'
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, _, _ = para_list[i][1]
    extract_start,extract_end = get_pre_trade_date(train_start,train_period),get_pre_trade_date(train_start,1)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)
    model = NN_redefine(extract_start, train_end, None, feature_address='/data//group/800442/800319/HFfactor/RealTimeFixRollRobust/data/', factor_eval_indicator=indicator, factor_num=factor_num)

    best_param_clf_nn['feature_path'] = out_file.replace('.pkl', '_feature_path/')
    best_param_clf_nn['train_log_path'] = out_file.replace('.pkl', '_train_log/')
    best_param_clf_nn['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_nn['load local model'] = True
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl','_train_pred/')
    label = model.rolling_train_and_predict(params=best_param_clf_nn, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)
    # os.mkdir('/data//group/800442/800319/Faamonitor/PL/')
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
idx_origin = list(range(133))[24:]
idx_list_list = [idx_origin[len(idx_origin) * i // 6:(i + 1) * len(idx_origin) // 6] for i in range(6)]
# idx_list = eval(AIMR.getParam())
# idx_list_list = list(zip(*idx_origin))[::-1]
# idx_list = idx_origin[33:]
for idx_list in idx_list_list[:3]:
    for idx in idx_list:
        main(idx)
        gc.collect()



