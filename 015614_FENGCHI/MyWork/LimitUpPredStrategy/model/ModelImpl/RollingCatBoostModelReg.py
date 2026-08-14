# coding: utf-8
# Author：fengchi863
# Date ：2021/4/20 15:56

from LimitUpPredStrategy.model.ModelBase.RollingModelBaseReg import RollingModelBaseReg
from LimitUpPredStrategy.Util.DataUtil import DataUtil
import catboost as cat
import datetime, time, gc, os
from tqdm import tqdm
import pandas as pd
from scipy import stats
from catboost.utils import eval_metric

from hyperopt import hp, fmin, tpe
import numpy as np



class RollingCatBoostModelReg(RollingModelBaseReg):
    def __init__(self, start_date=20140101, end_date=20191231):
        super().__init__(start_date, end_date)

    def train_model(self, X_train, y_train, params, end_date=None):
        # 设置验证集
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))

        train_features, train_labels = X_train.loc[date_list], y_train.loc[date_list]
        val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
        train_pool =cat.Pool(train_features,train_labels)
        val_pool = cat.Pool(val_features,val_labels)

        #best_params['boosting_type'] = 'Plain' if best['boosting_type'] == 1 else 'Ordered'
        cat_model = cat.CatBoostRegressor(**params, random_seed=42)
        catmodel = cat_model.fit(train_pool, verbose=0,eval_set=val_pool)



        if 'val_pred_path' in params:

            val_labels = pd.DataFrame(val_labels)
            val_labels['prediction'] = self.predict(catmodel, val_features)
            val_labels.columns.name = ['actual_label', 'prediction']
            DataUtil.save_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date, verbose=False)

        if 'train_pred_path' in params:
            train_label = pd.DataFrame(train_labels)
            train_label['prediction'] = self.predict(catmodel, train_features)
            train_label.columns.name = ['actual_label', 'prediction']
            DataUtil.save_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date, verbose=False)

        return catmodel

    def predict(self, model, X_test):
        predict = model.predict(X_test)
        return predict

    def rolling_train_and_predict(self, params={}, period=60, predict_period=10,factor_num=60):
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
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),factor_num)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e
            e = time.time()

            if len(X_train) > 300 and len(set(y_train)) > 1:
                model = self.train_model(X_train, y_train, params, test_start_idx)


            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test)
                y_test = pd.DataFrame(y_test)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                # print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label