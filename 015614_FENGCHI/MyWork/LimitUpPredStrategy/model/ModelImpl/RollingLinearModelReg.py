# coding: utf-8
# Author：fengchi863
# Date ：2021/5/14 10:11

from LimitUpPredStrategy.model.ModelBase.RollingModelBaseReg import RollingModelBaseReg
from LimitUpPredStrategy.Util.DataUtil import DataUtil
from sklearn.linear_model import LinearRegression
import datetime, time, gc, os
from tqdm import tqdm
import pandas as pd, numpy as np

class RollingLinearModelReg(RollingModelBaseReg):
    def __init__(self, start_date=20140101, end_date=20191231):
        super().__init__(start_date, end_date)

    def train_model(self, X_train, y_train, params, end_date=None):
        lr_model = LinearRegression()
        # param_self = lr_model.get_params()
        # args_param = params.copy()
        # for akey in params.keys():
        #     if akey not in param_self:
        #         args_param.pop(akey)
        #     else:
        #         if not isinstance(args_param[akey], type(param_self[akey])):
        #             args_param[akey] = int(args_param[akey])
        # lr_model.set_params(**args_param)

        # 设置验证集
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))

        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
        lr_model = lr_model.fit(train_features, train_label)

        if 'val_pred_path' in params:
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            val_labels = pd.DataFrame(val_labels)
            val_labels['prediction'] = self.predict(lr_model, val_features)
            val_labels.columns.name = ['actual_label', 'prediction']
            DataUtil.save_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date, verbose=False)

        if 'train_pred_path' in params:
            train_label = pd.DataFrame(train_label)
            train_label['prediction'] = self.predict(lr_model, train_features)
            train_label.columns.name = ['actual_label', 'prediction']
            DataUtil.save_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date, verbose=False)

        return lr_model

    def predict(self, model, X_test):
        predict = model.predict(X_test)
        return predict

    def rolling_train_and_predict(self, params={}, period=60, predict_period=10, factor_num=80):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, training_sample = 0, 0, 0
        model = None
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            X_train, y_train, X_test, y_test = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx), factor_num=factor_num)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e
            e = time.time()

            if len(X_train) > 10000 and len(set(y_train)) > 1:
                X_train = X_train.replace([np.inf, -np.inf], np.nan)
                X_train = X_train.fillna(0)
                model = self.train_model(X_train, y_train, params, test_start_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                X_test = X_test.replace([np.inf, -np.inf], np.nan)
                X_test = X_test.fillna(0)
                pred_label = self.predict(model, X_test)
                y_test = pd.DataFrame(y_test)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                # print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label