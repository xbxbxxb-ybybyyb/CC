# @Time : 2020/9/29 9:13
# @Author : Zhichen Lu
# @File : NN.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from keras.callbacks import *
from keras.layers import Dropout, Dense
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
import os,time,gc
from xquant.compute.aimr import AIMR

def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1 - K.mean((y_true - K.mean(y_true)) * (y_pred - K.mean(y_pred))) / (K.std(y_true) * K.std(y_pred)))


def res_std(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.std(y_true - y_pred)


def myloss(y_true_, y_pred_):
    return 0.5 * K_corr(y_true_, y_pred_) + res_std(y_true_, y_pred_)
    # y_true, y_pred = K.cast(y_true_,dtype='float32'),K.cast(y_pred_,dtype='float32')
    # return mean_squared_error(y_pred,y_true) + 2*K_corr(y_true_,y_pred_)


best_param_clf_nn = {'activation': 'relu',
 'alpha': 9.756090506594905e-05,
 'batch_size': 131072,
 'dropout': 0.2,
 'hidden_layer_sizes': (64, 32, 16),
 'learning_rate': 'adaptive',
 'learning_rate_init': 0.1,
 'momentum': 0.5,
 'nb_epoch': 200,
 'solver': 'sgd'}


class NN_redefine(ModelNewLoading):

    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address='/data/group/800319/LittleJunkFix/', factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    # def feature_engineering(self, train_feature, train_label, test_feature, test_label):
    #     value_count = pd.Series((~np.isnan(train_feature.values)).sum(axis=1), index=train_feature.index)
    #     train_feature = train_feature[value_count > train_feature.shape[1] * 0.80]
    #     value_count = pd.Series((~np.isnan(test_feature.values)).sum(axis=1), index=test_feature.index)
    #     test_feature = test_feature[value_count > test_feature.shape[1] * 0.8]
    #     train_label, test_label = train_label.loc[train_feature.index].dropna(), test_label.loc[
    #         test_feature.index].dropna()
    #     train_feature, test_feature = train_feature.loc[train_label.index].fillna(0), test_feature.loc[
    #         test_label.index].fillna(0)
    #
    #     train_arr = train_feature.values
    #     train_arr[train_arr > 5] = 5
    #     train_arr[train_arr < -5] = -5
    #     train_feature = pd.DataFrame(train_arr, index=train_feature.index, columns=train_feature.columns)
    #     test_arr = test_feature.values
    #     test_arr[test_arr > 5] = 5
    #     test_arr[test_arr < -5] = -5
    #     test_feature = pd.DataFrame(test_arr, index=test_feature.index, columns=test_feature.columns)
    #     del train_arr, test_arr
    #     return train_feature, train_label, test_feature, test_label

    def NN(self, input_dim, params):
        print('CorrOnly')
        hidden_layer_sizes = params['hidden_layer_sizes']
        model = Sequential()
        model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
        for dim in hidden_layer_sizes[1:]:
            model.add(Dense(dim, activation=params['activation']))
        model.add(Dense(1))
        optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
        self.compile_model(model, optimizer, ['mae', 'mse'])
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
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]

        model = self.NN(input_dim=X_train.shape[1], params=params)
        early_stopping = EarlyStopping(monitor='val_loss', patience=7)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=3, min_lr=0.001)
        train_log = CSVLogger(params['train_log_path'] + '%d.csv' % val_date[0])
        callbacks_list = [early_stopping, reduce_lr, train_log]
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.h5' % val_date[0]):
            model.load_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
            print('load model from local')
        else:
            model.fit(train_features.values, train_label.values, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=0, \
                      shuffle=True, callbacks=callbacks_list, validation_split=0.05)
            model.save_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            val_labels['prediction'] = model.predict(val_features.values)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % val_date[0])
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % val_date[0])
        return model

    def predict(self, model, X_test, end_date_idx=None):
        pre_label = model.predict(X_test.values)
        return pre_label


para_list = [(0, (20150309, 20151225, 20151228, 20160111)),
              (1, (20150323, 20160111, 20160112, 20160125)),
              (2, (20150407, 20160125, 20160126, 20160215)),
              (3, (20150421, 20160215, 20160216, 20160229)),
              (4, (20150506, 20160229, 20160301, 20160314)),
              (5, (20150520, 20160314, 20160315, 20160328)),
              (6, (20150603, 20160328, 20160329, 20160412)),
              (7, (20150617, 20160412, 20160413, 20160426)),
              (8, (20150702, 20160426, 20160427, 20160511)),
              (9, (20150716, 20160511, 20160512, 20160525)),
              (10, (20150730, 20160525, 20160526, 20160608)),
              (11, (20150813, 20160608, 20160613, 20160624)),
              (12, (20150827, 20160624, 20160627, 20160708)),
              (13, (20150914, 20160708, 20160711, 20160722)),
              (14, (20150928, 20160722, 20160725, 20160805)),
              (15, (20151019, 20160805, 20160808, 20160819)),
              (16, (20151102, 20160819, 20160822, 20160902)),
              (17, (20151116, 20160902, 20160905, 20160920)),
              (18, (20151130, 20160920, 20160921, 20161011)),
              (19, (20151214, 20161011, 20161012, 20161025)),
              (20, (20151228, 20161025, 20161026, 20161108)),
              (21, (20160112, 20161108, 20161109, 20161122)),
              (22, (20160126, 20161122, 20161123, 20161206)),
              (23, (20160216, 20161206, 20161207, 20161220)),
              (24, (20160301, 20161220, 20161221, 20170104)),
              (25, (20160315, 20170104, 20170105, 20170118)),
              (26, (20160329, 20170118, 20170119, 20170208)),
              (27, (20160413, 20170208, 20170209, 20170222)),
              (28, (20160427, 20170222, 20170223, 20170308)),
              (29, (20160512, 20170308, 20170309, 20170322)),
              (30, (20160526, 20170322, 20170323, 20170407)),
              (31, (20160613, 20170407, 20170410, 20170421)),
              (32, (20160627, 20170421, 20170424, 20170508)),
              (33, (20160711, 20170508, 20170509, 20170522)),
              (34, (20160725, 20170522, 20170523, 20170607)),
              (35, (20160808, 20170607, 20170608, 20170621)),
              (36, (20160822, 20170621, 20170622, 20170705)),
              (37, (20160905, 20170705, 20170706, 20170719)),
              (38, (20160921, 20170719, 20170720, 20170802)),
              (39, (20161012, 20170802, 20170803, 20170816)),
              (40, (20161026, 20170816, 20170817, 20170830)),
              (41, (20161109, 20170830, 20170831, 20170913)),
              (42, (20161123, 20170913, 20170914, 20170927)),
              (43, (20161207, 20170927, 20170928, 20171018)),
              (44, (20161221, 20171018, 20171019, 20171101)),
              (45, (20170105, 20171101, 20171102, 20171115)),
              (46, (20170119, 20171115, 20171116, 20171129)),
              (47, (20170209, 20171129, 20171130, 20171213)),
              (48, (20170223, 20171213, 20171214, 20171227)),
              (49, (20170309, 20171227, 20171228, 20180111)),
              (50, (20170323, 20180111, 20180112, 20180125)),
              (51, (20170410, 20180125, 20180126, 20180208)),
              (52, (20170424, 20180208, 20180209, 20180301)),
              (53, (20170509, 20180301, 20180302, 20180315)),
              (54, (20170523, 20180315, 20180316, 20180329)),
              (55, (20170608, 20180329, 20180330, 20180416)),
              (56, (20170622, 20180416, 20180417, 20180502)),
              (57, (20170706, 20180502, 20180503, 20180516)),
              (58, (20170720, 20180516, 20180517, 20180530)),
              (59, (20170803, 20180530, 20180531, 20180613)),
              (60, (20170817, 20180613, 20180614, 20180628)),
              (61, (20170831, 20180628, 20180629, 20180712)),
              (62, (20170914, 20180712, 20180713, 20180726)),
              (63, (20170928, 20180726, 20180727, 20180809)),
              (64, (20171019, 20180809, 20180810, 20180823)),
              (65, (20171102, 20180823, 20180824, 20180906)),
              (66, (20171116, 20180906, 20180907, 20180920)),
              (67, (20171130, 20180920, 20180921, 20181012)),
              (68, (20171214, 20181012, 20181015, 20181026)),
              (69, (20171228, 20181026, 20181029, 20181109)),
              (70, (20180112, 20181109, 20181112, 20181123)),
              (71, (20180126, 20181123, 20181126, 20181207)),
              (72, (20180209, 20181207, 20181210, 20181221))]


def main(i):
    N = 40
    train_period = 200
    test_period = 10
    factor_num = 400
    indicator = 'ic_all_d'
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/NNFactorEvalPara52_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
        indicator, train_period, test_period, factor_num, N)
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        # return
    print(out_file)
    model = NN_redefine(train_start, test_end, None, feature_address='/data/group/800319/HFfactor/FixRoll/data/', factor_eval_indicator=indicator, factor_num=factor_num)

    # best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_nn['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_nn['train_log_path'] = out_file.replace('.pkl', '_train_log/')
    best_param_clf_nn['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_nn['load local model'] = True
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl','_train_pred/')
    label = model.rolling_train_and_predict(params=best_param_clf_nn, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)
    # os.mkdir('/data/group/800319/Faamonitor/PL/')


idx = int(AIMR.getParam())
main(idx)