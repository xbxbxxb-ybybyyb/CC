# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from xgboost import XGBRegressor
import xgboost as xgb
import os,gc,time,datetime
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from StrongStockModel.conf.model_param_config import best_param_clf_xgb
from tqdm import tqdm
import random

class XGBRegressionFactorEval(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address='/data/group/800319/LittleJunkFix/', factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def predict(self, model, X_test, end_date=None):
        dtest = xgb.DMatrix(X_test)
        pre_label = model.predict(dtest)
        return pre_label

    def train_model(self, X_train, y_train, params, end_date=None,best_model=None):
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
        args_param.update({'sampling_method': 'gradient_based'})
        train_end = sorted(list(set([x[0] for x in X_train.index])))[-1]

        print(args_param)
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9,-11]]
        date_list = list(set(date_list) - set(val_date))

        val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
        d_val = xgb.DMatrix(val_features)
        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
        d_train = xgb.DMatrix(train_features, label=train_label.values)

        if 'load local model' in params and os.path.exists(params['source_model_conf_path'] + '%d.json' % end_date):
            model = xgb.Booster(args_param)
            model.load_model(params['source_model_conf_path'] + '%d.json' % end_date)
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            ########################
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], verbose_eval=False)
        if best_model is None:
            best_model = model
            val_labels['prediction'] = best_model.predict(d_val)
        else:
            feature_index = train_features.index.tolist()
            eval_index = random.sample(feature_index,int(train_features.shape[0]*0.02))
            eval_feature,eval_label = train_features.loc[eval_index],train_label.loc[eval_index]
            train_features,train_label = train_features.drop(eval_index,axis=0),train_label.drop(eval_index,axis=0)
            d_train = xgb.DMatrix(train_features, label=train_label.values)
            d_eval = xgb.DMatrix(eval_feature,label=eval_label.values)
            model_rolling = xgb.train(args_param,d_train,num_boost_round=params['n_estimators'],early_stopping_rounds=15,xgb_model=best_model,verbose_eval=False,
                                      evals=[(d_eval,'d_eval')])

            val_labels['pred_new_model'] = model.predict(d_val)
            val_labels['pred_rolling_model'] = model_rolling.predict(d_val)

            corr = val_labels.corr()
            corr_new_model = corr.loc['actual_label','pred_new_model']
            corr_rolling_model = corr.loc['actual_label','pred_rolling_model']

            if corr_new_model>corr_rolling_model:
                best_model = model
                print(train_end,'new train')
                val_labels = val_labels.rename(columns={'pred_new_model':'prediction'})[['actual_label','prediction']]
            else:
                best_model = model_rolling
                val_labels = val_labels.rename(columns={'pred_rolling_model':'prediction'})[['actual_label','prediction']]
                print(train_end,'rolling_train')
        best_model.save_model(params['selected_model_conf_path'] + '%d.json' % train_end)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % train_end)
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(d_train)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % train_end)
        return best_model

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
                model = self.train_model(X_train, y_train, params, train_end_idx,best_model=model)
            if model is None:
                continue
            training_time = time.time() - e
            pred_label = self.predict(model, X_test, train_end_idx)
            y_test.columns = ['actual_label']
            y_test['prediction'] = pred_label
            print('test_ic', train_end_idx, y_test.corr())
            label = label.append(y_test)
            del X_train, y_train, X_test, y_test, pred_label
            gc.collect()
        return label


from xquant.xqutils.helper import link


def main_window_search():
    train_period = 200
    test_period = 10
    factor_num = 400
    N = 40
    indicator = 'ic_all_t'

    #######in smaple
    # all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d_and_binary/' % N
    # model = XGBRegressionFactorEval(20150309, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path,factor_eval_indicator=indicator)
    # out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
    # indicator, train_period, test_period, factor_num, N)

    #out sample

    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/XGBFactorEvalRollingBest_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
        indicator, train_period, test_period, factor_num, N)

        # return
    print(out_file)
    best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    best_param_clf_xgb['selected_model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['source_model_conf_path'] = out_file.replace('.pkl', '_model_conf/').replace('RollingBest','')
    best_param_clf_xgb['load local model'] = True
    model = XGBRegressionFactorEval(20150309, 20181231, None, feature_address='/data/group/800319/HFfactor/FixRoll/data/', factor_eval_indicator=indicator, factor_num=factor_num)
    if not os.path.exists(best_param_clf_xgb['selected_model_conf_path']):
        os.mkdir(best_param_clf_xgb['selected_model_conf_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, out_file)
    print(out_file)
    lm = link.LinkMessage()
    lm.sendMessage(indicator+" "+out_file)

main_window_search()
# for i in range(73):
#     main_window_search(i)
#     gc.collect()