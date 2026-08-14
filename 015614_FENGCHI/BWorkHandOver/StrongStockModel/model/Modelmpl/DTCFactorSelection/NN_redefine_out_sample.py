# @Time : 2020/9/29 9:13
# @Author : Zhichen Lu
# @File : NN.py

import pandas as pd
from keras.callbacks import *
from keras.layers import  Dropout, Dense
from keras.losses import mean_squared_error
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from sklearn import metrics
import datetime,time, gc
from tqdm import tqdm
from StrongStockModel.conf.path_config import root_path
from StrongStockModel.model.ModelBase.ModelBase import ModelBase


def K_corr(y_true_,y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1-K.mean((y_true-K.mean(y_true))*(y_pred-K.mean(y_pred)))/(K.std(y_true)*K.std(y_pred)))


def res_std(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.std(y_true - y_pred)


def myloss(y_true_, y_pred_):
    return 0.5 * K_corr(y_true_, y_pred_) + res_std(y_true_, y_pred_)
    # y_true, y_pred = K.cast(y_true_,dtype='float32'),K.cast(y_pred_,dtype='float32')
    # return mean_squared_error(y_pred,y_true) + 2*K_corr(y_true_,y_pred_)

best_param_clf_nn = {
    'activation': 'relu',
    'alpha': 9.756090506594905e-05,
    'hidden_layer_sizes': (16, 32, 8),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.0703114914234283,
    'momentum': 0.1669382592981298, 'solver': 'sgd',
    'nb_epoch':50,
    'batch_size' : 2**17
}

class NN_redefine(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.eval_indicator = factor_eval_indicator

    def get_fix_factor_evaluation(self, num):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        factor_list = factor_evaluation.loc[inter_col, self.eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        return factor_list

    def feature_engineering(self, train_feature, train_label, test_feature, test_label):
        value_count = pd.Series((~np.isnan(train_feature.values)).sum(axis=1), index=train_feature.index)
        train_feature = train_feature[value_count > train_feature.shape[1] * 0.80]
        value_count = pd.Series((~np.isnan(test_feature.values)).sum(axis=1), index=test_feature.index)
        test_feature = test_feature[value_count > test_feature.shape[1] * 0.8]
        train_label, test_label = train_label.loc[train_feature.index].dropna(), test_label.loc[
            test_feature.index].dropna()
        train_feature, test_feature = train_feature.loc[train_label.index].fillna(0), test_feature.loc[
            test_label.index].fillna(0)

        train_arr = train_feature.values
        train_arr[train_arr>5] = 5
        train_arr[train_arr < -5] = -5
        train_feature = pd.DataFrame(train_arr,index=train_feature.index,columns=train_feature.columns)
        test_arr = test_feature.values
        test_arr[test_arr> 5] = 5
        test_arr[test_arr <-5] = -5
        test_feature = pd.DataFrame(test_arr,index=test_feature.index,columns=test_feature.columns)
        del train_arr,test_arr
        return train_feature, train_label, test_feature, test_label

    def NN(self,input_dim, params):
        print('CorrOnly')
        hidden_layer_sizes = params['hidden_layer_sizes']
        model = Sequential()
        model.add(Dense(hidden_layer_sizes[0],input_dim=input_dim,activation=params['activation']))
        for dim in hidden_layer_sizes[1:]:
            model.add(Dense(dim,activation=params['activation']))
        model.add(Dense(1))
        optimizer = SGD(lr=params['learning_rate_init'],momentum=params['momentum'])
        self.compile_model(model,optimizer,['mae','mse'])
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


        model = self.NN(input_dim=X_train.shape[1],params=params)


        train_end = sorted(list(set([x[0] for x in X_train.index])))[-1]
        if 'load local model' in params and os.path.exists(params['model_conf_path']+'%d.h5'%train_end):
            model.load_weights(params['model_conf_path']+'%d.h5'%train_end)
            print('load model from local')
            return model
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]

        early_stopping = EarlyStopping(monitor='val_loss', patience=7)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=3, min_lr=0.001)
        train_log = CSVLogger(params['train_log_path'] + '%d.csv' % end_date)
        callbacks_list = [early_stopping, reduce_lr, train_log]
        model.fit(train_features.values, train_label.values, epochs=params['nb_epoch'], \
                  batch_size=params['batch_size'], verbose=0, \
                  shuffle=True, callbacks=callbacks_list,validation_split=0.05)
        model.save_weights(params['model_conf_path']+'%d.h5'%end_date)
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            val_labels['prediction'] = model.predict(val_features.values)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date)
        return model

    def predict(self, model, X_test,end_date_idx=None):
        pre_label = model.predict(X_test.values)
        return pre_label

    def training_methodology(self, params, period=10, predict_period=10):
        compare = self.rolling_train_and_predict(params=params, period=period, predict_period=predict_period)
        if len(compare) == 0:
            return pd.DataFrame(), {'acc': np.nan, 'precision': np.nan, 'recall': np.nan, 'f1': np.nan}
        acc = metrics.accuracy_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual_label'], y_pred=compare['prediction'],
                                            average='micro')
        recall = metrics.recall_score(y_true=compare['actual_label'], y_pred=compare['prediction'], average='micro')
        f1 = metrics.f1_score(y_true=compare['actual_label'], y_pred=compare['prediction'], average='micro')
        print({'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1})
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None
        fix_factor_list = self.get_fix_factor_evaluation(factor_nums)
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
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()
            if len(X_test) == 0:
                print('zero sample')
                continue
            if len(X_train) > 2000 and len(set(y_train[y_train.columns[0]])) > 1:
                print('re-train in this round')
                model = self.train_model(X_train, y_train, params, test_start_idx)
            if model is None:
                continue
            training_time = time.time() - e
            pred_label = self.predict(model, X_test, test_start_idx)
            y_test.columns = ['actual_label']
            y_test['prediction'] = pred_label
            label = label.append(y_test)
            del X_train, y_train, X_test, y_test, pred_label
            gc.collect()
        return label
