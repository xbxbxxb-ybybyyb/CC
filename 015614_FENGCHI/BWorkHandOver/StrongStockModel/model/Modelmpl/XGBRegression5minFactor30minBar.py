# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression5min.py
import numpy as np
import pandas as pd
from sklearn import metrics
from xgboost import XGBRegressor
import xgboost as xgb
import os
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from multiprocessing import Pool
import time
import gc
from dataApi.DataPrepare import DataPrepare
fix_point = [1000,1030,1100,1300,1330,1400,1430]
class XGBRegression5minFactor30minBar(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.dp = DataPrepare('/data/group/800319/JunkSmallFactor/')



    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        self.dp.set_date_range(train_idx[0],test_idx[1])
        fix_factor = self.dp.load_data(fix_factor_list+['future'])
        load_time = time.time() - e
        fix_factor = fix_factor.sort_index()
        fix_factor = fix_factor.swaplevel(0,1).loc[fix_point].swaplevel(0,1)
        train_feature = fix_factor.loc[train_idx[0]:train_idx[-1]]
        train_label = pd.DataFrame(train_feature.pop('future'))
        test_feature = fix_factor.loc[test_idx[0]:test_idx[-1]]
        test_label = pd.DataFrame(test_feature.pop('future'))
        print('load %d ' % (load_time))
        e = time.time()
        train_feature, train_label, test_feature, test_label = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label)
        gc.collect()
        return train_feature, train_label, test_feature, test_label, time.time() - e

    def predict(self, model, X_test,end_date=None):
        dtest = xgb.DMatrix(X_test)
        pre_label = model.predict(dtest)
        return pre_label

    def get_fix_factor_evaluation(self, num):
        res = pd.read_excel('/data/group/800319/junkData/StrongStock/external_data/5min样本内.xlsx',index_col=0).sort_index()
        factor_list = res.loc[1000:2201].sort_values('ic_all_t',ascending=False).index.tolist()[:200]+\
                        res.loc[8000:8072].index.tolist()+\
                        res.loc[9500:].index.tolist()
        factor_list = [str(x).zfill(4) for x in factor_list]
        print('tnmanual Factor!')
        return factor_list
        # ic_res = pd.read_pickle('/data/group/800319/Strong_stock/ic_sort_yearly_avg_window40.pkl').sort_index()
        # ic_res.index = ic_res.index.astype(int)
        # factor_list = ic_res.loc[1000:2201].sort_values(ascending=False).index.tolist()[:200]+\
        #                 ic_res.loc[8000:8072].index.tolist()+\
        #                 ic_res.loc[9500:].index.tolist()
        # print('factor 312')
        # return factor_list
        # print('factor num 6815 recheck')
        # return [str(x).zfill(4) for x in range(101,169)]+[str(x).zfill(4) for x in range(9101,9115)]

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
        param_self = XGBRegressor().get_params()
        args_param = params.copy()
        for akey in params.keys():
            if akey not in param_self:
                args_param.pop(akey)
            # else:
            #     if not isinstance(args_param[akey], type(param_self[akey])):
            #         args_param[akey] = type(param_self[akey])(args_param[akey])
        args_param.pop('n_estimators')
        args_param.pop('objective')
        args_param['tree_method'] = 'gpu_hist'
        # args_param.update({'subsample': 0.2,'sampling_method': 'gradient_based','tree_method':'gpu_hist'})
        print(args_param)
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))

        if 'load local model' in params and os.path.exists(params['model_conf_path']+'%d.json'%val_date[0]):
            model = xgb.Booster(args_param)
            model.load_model(params['model_conf_path']+'%d.json'%val_date[0])
            print('load from local',val_date[0])
        else:
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            d_train = xgb.DMatrix(train_features, label=train_label.values)
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], verbose_eval=False)
            model.save_model(params['model_conf_path']+'%d.json'%val_date[0])

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(d_val)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % val_date[0])
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(d_train)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % val_date[0])
        return model
