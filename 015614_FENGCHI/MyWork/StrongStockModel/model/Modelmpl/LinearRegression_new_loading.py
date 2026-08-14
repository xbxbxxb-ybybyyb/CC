# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.externals import joblib
# import xgboost as xgb
import os
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from StrongStockModel.conf.path_config import fix_factor_true_send_ic_sort_path
import datetime, time, gc
from tqdm import tqdm
from dataApi.DataPrepare import DataPrepare


class LinearNewLoading(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.dp = DataPrepare(idx_address='/data/group/800319/LittleJunkFix/')

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        self.dp.set_date_range(train_idx[0], test_idx[1])
        fix_factor = self.dp.load_data(fix_factor_list + ['future'])
        load_time = time.time() - e
        fix_factor = fix_factor.sort_index()
        train_feature = fix_factor.loc[train_idx[0]:train_idx[-1]]
        print('before pop shape', train_feature.shape)
        train_label = pd.DataFrame(train_feature.pop('future'))
        test_feature = fix_factor.loc[test_idx[0]:test_idx[-1]]
        test_label = pd.DataFrame(test_feature.pop('future'))
        print('load %d ' % (load_time))
        print('after pop shape', train_feature.shape)
        e = time.time()
        train_feature, train_label, test_feature, test_label = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label)
        gc.collect()
        return train_feature, train_label, test_feature, test_label, time.time() - e

    def predict(self, model, X_test, end_date=None):
        # dtest = xgb.DMatrix(X_test)
        pre_label = model.predict(X_test)
        return pre_label

    def get_fix_factor_evaluation(self, num):
        factor_list = pd.read_pickle(fix_factor_true_send_ic_sort_path)
        if num > len(factor_list):
            num = len(factor_list)
            print('the max length of fix_factor_list is %d' % (len(factor_list)))

        # binary_factor = ['vr', 'vidya', 'mtm', 'hlma', 'vi', 'ao1', 'aws2', 'asi', 'ko', 'vao', 'dma', 'bias36', 'roc', 'ppo', 'aligator', 'ic', 'er', 'vvr', 'rmi', 'trix', 'pac', 'nvi', 'fisher', 'vramt', 'cr', 'po', 'adx', 'macd1', 'wvad', 'pvo', 'amv', 'atr', 'madisplaced', 'cho', 'tar', 'sroc', 'kdjd', 'typ', 'demakder', 'skdj', 'expma', 'boll', 'adosc', 'ma', 'eom', 'smi', 'rccd', 'clv', 'dbcd', 'cmf', 'hullma', 'dzcci', 'cv', 'qstick', 'macd2', 'wc', 'macdvol', 'osc', 'srocvol', 'ao2', 'mejt', 'rsis', 'imi', 'tsi', 't3', 'dzrsi', 'tdi', 'kc', 'pvt', 'micd', 'rvi', 'tll', 'aws1', 'kdj', 'rsiv', 'uos', 'wr', 'bop', 'zlmacd', 'mfi', 'tema', 'emv']
        # print('ic_score_factor_num:', len(factor_list[:num]),'binary num:',len(binary_factor))
        print('ic_score_factor_num:', len(factor_list[:num]))
        return factor_list.index.tolist()[:num]  # + binary_factor

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

    def train_model(self, X_train, y_train, params, end_Date=None):
        param_self = LinearRegression().get_params()
        args_param = params.copy()
        for akey in params.keys():
            if akey not in param_self:
                args_param.pop(akey)
            # else:
            #     if not isinstance(args_param[akey], type(param_self[akey])):
            #         args_param[akey] = type(param_self[akey])(args_param[akey])
        print(args_param)
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]

        # d_train = xgb.DMatrix(train_features, label=train_label.values)
        train_features64 = train_features.astype('float64')
        train_label64 = train_label[['future']].astype('float64')
        model = LinearRegression()  # xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], verbose_eval=False)
        model.fit(train_features64, train_label64.values)
        train_label64['prediction'] = model.predict(train_features64)
        pd.to_pickle(train_label64, params['train_pred_path'] + '%d_float64.pkl' % val_date[0])
        model.fit(train_features, train_label.values)
        joblib.dump(model, params['model_conf_path'] + '%d.pkl' % val_date[0])
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

    """
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

    """
