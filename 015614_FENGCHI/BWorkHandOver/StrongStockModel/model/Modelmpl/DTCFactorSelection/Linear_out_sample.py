# @Time : 2020/11/7 13:13
# @Author : Zhichen Lu
# @File : Linear_out_sample.py

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression
import os
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
import datetime,time, gc
from tqdm import tqdm
from sklearn.externals import joblib
from StrongStockModel.conf.path_config import root_path

class LinearReg(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.eval_indicator = factor_eval_indicator

    def predict(self, model, X_test,end_date=None):
        pre_label = model.predict(X_test)
        return pre_label

    def get_fix_factor_evaluation(self, num):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        factor_list = factor_evaluation.loc[inter_col, self.eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        return factor_list

    def training_methodology(self, params, period=10, predict_period=10):
        compare = self.rolling_train_and_predict(params=params, period=period, predict_period=predict_period)
        if len(compare) == 0:
            return pd.DataFrame(), {'acc': np.nan, 'precision': np.nan, 'recall': np.nan, 'f1': np.nan}
        acc = metrics.accuracy_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        recall = metrics.recall_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        f1 = metrics.f1_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        print({'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1})
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}

    def train_model(self, X_train, y_train, params,end_date=None):
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        param_self = LinearRegression().get_params()
        args_param = params.copy()
        for akey in params.keys():
            if akey not in param_self:
                args_param.pop(akey)
            # else:
            #     if not isinstance(args_param[akey], type(param_self[akey])):
            #         args_param[akey] = type(param_self[akey])(args_param[akey])
        train_end = sorted(list(set([x[0] for x in X_train.index])))[-1]
        if 'load local model' in params and os.path.exists(params['model_conf_path']+'%d.pkl'%train_end):
            model = joblib.load(params['model_conf_path']+'%d.pkl'%train_end)
            print('load model from local',train_end)
            return model

        print(args_param)
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
        model = LinearRegression()
        model.fit(train_features,train_label.values)
        joblib.dump(model,params['model_conf_path']+'%d.pkl'%end_date)
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            # d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(val_features)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % val_date[0])
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % val_date[0])
        return model

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