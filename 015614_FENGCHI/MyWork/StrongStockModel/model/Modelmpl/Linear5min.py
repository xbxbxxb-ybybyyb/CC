# @Time : 2020/9/28 8:38
# @Author : Zhichen Lu
# @File : Linear.py

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression
import os, gc, time
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from sklearn.externals import joblib
from dataApi.DataPrepare import DataPrepare


class LinearReg5min(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.dp = DataPrepare(idx_address=feature_address)
        self.indicator = indicator

    def predict(self, model, X_test, end_date=None):
        pre_label = model.predict(X_test.astype('float64'))
        return pre_label

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        self.dp.set_date_range(train_idx[0], test_idx[1])
        fix_factor = self.dp.load_data(fix_factor_list + ['future'])
        load_time = time.time() - e
        fix_factor = fix_factor.sort_index()  # .astype('float64')
        train_feature = fix_factor.loc[train_idx[0]:train_idx[-1]]
        train_label = pd.DataFrame(train_feature.pop('future'))
        test_feature = fix_factor.loc[test_idx[0]:test_idx[-1]]
        test_label = pd.DataFrame(test_feature.pop('future'))
        print('load %d ' % (load_time))
        e = time.time()
        train_feature, train_label, test_feature, test_label = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label)
        gc.collect()
        return train_feature.clip(-5, 5), train_label, test_feature.clip(-5, 5), test_label, time.time() - e

    def get_fix_factor_evaluation(self, num):
        indicator = self.indicator
        factor_info, _, _, _ = pd.read_pickle('/data/group/800319/FactorSelection/strategy001/%s.pkl' % indicator)
        key_map = pd.read_pickle('/data/group/800319/FactorSelection/strategy001/calc_factor_df.pkl')
        factor_list = key_map.reset_index().set_index('name').loc[factor_info['mix']]['index'].tolist()
        print(indicator, len(factor_list))
        return factor_list
        # factor_list = [1048, 1018, 1034, 1030, 1076, 1000, 1056, 1029, 1177, 1230, 1145, 1002, 1170, 1333, 1047, 1443, 1012, 1391, 1006, 1090, 451, 1028, 1387, 1105, 1024, 1046,
        #                1054, 1093, 2047, 1340, 1908, 1498, 1045, 1072, 1023, 1760, 1201, 1252, 1338, 1715, 1134, 698, 495, 1249, 1020, 1004, 783, 1016, 1254, 1104, 1142, 1140,
        #                1213, 1231, 516, 462, 1189, 1341, 1125, 1778, 745, 1284, 1208, 419, 1112, 8008, 674, 1182, 1148, 800, 1080, 1976, 1513, 1383, 1010, 1237, 1068, 1099, 579,
        #                1110, 1531, 1268, 2044, 2140, 1075, 1214, 1239, 1960, 1734, 2023, 1172, 1287, 1370, 1153, 1166, 1244, 543, 1292, 1337, 1965, 1139, 1362, 1815, 1281, 805,
        #                1386, 1719, 2200, 2062, 1243, 1260, 1567, 1263, 1920, 1035, 1662, 463, 2177, 1131, 661, 754, 1224, 1167, 1718, 1122, 1059, 1506, 1515, 1152, 1409, 1238,
        #                1480, 1852, 1699, 478, 1686, 1233, 1924, 1156, 1339, 1389, 1225, 547, 1001, 1783, 711, 1083, 1692, 1381, 1304, 537, 1178, 726, 738, 1419, 1814, 1588, 1094,
        #                1932, 2078, 1583, 1352, 1691, 1935, 1679, 1563, 747, 797, 1071, 508, 2035, 2080, 750, 1648, 2153, 1865, 1634, 1609, 2091, 1282]
        # factor_list = [str(x).zfill(4) for x in factor_list]
        # print('factor 180')
        # return factor_list

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

    def train_model(self, X_train, y_train, params, end_date=None):
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
        print(args_param)
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.pkl' % train_end):
            model = joblib.load(params['model_conf_path'] + '%d.pkl' % train_end)
            print('load model from local', train_end)
        else:
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            model = LinearRegression()
            model.set_params(**args_param)
            # pd.to_pickle([train_features, train_label], '/data/user/015664/AFuckingTrigger/lr_sample.pkl')
            # train_features, train_label = pd.read_pickle( '/data/user/015664/AFuckingTrigger/lr_sample.pkl')
            model.fit(train_features.values.astype('float64'), train_label.values.astype('float64'))
            joblib.dump(model, params['model_conf_path'] + '%d.pkl' % end_date)
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            # d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(val_features.astype('float64'))
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date)
        return model
