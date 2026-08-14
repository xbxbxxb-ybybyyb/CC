# coding: utf-8
# Author：fengchi863
# Date ：2021/4/1 14:33
from hyperopt import hp, fmin, tpe
import random
random.seed(2021)
from LimitUpPredStrategy.Util.DataUtil import DataUtil
from LimitUpPredStrategy.model.ModelImpl.RollingCatBoostModelReg import RollingCatBoostModelReg
from LimitUpPredStrategy.conf.path_conf import pred_output_path
import warnings
import pandas as pd
import numpy as np
import pickle
import gc
from sklearn import metrics
from LimitUpPredStrategy.Util.hyperopt_util import hyperopt_wrapper

warnings.filterwarnings('ignore')

if __name__ == '__main__':
    model_name = 'rolling_catboost_reg_20210513'
    factor_num = 80
    train_period = 60
    predict_period = 5
    stock_pool = 'all_board'
    dnn_model = RollingCatBoostModelReg(start_date=20150101, end_date=20191231)
    rolling_train_test_idx_list = dnn_model.get_rolling_index(train_period,predict_period)
    dnn_model.set_dataset(train_start_date=20140101, train_end_date=20191231,
                          predict_start_date=20200101, predict_end_date=20201231,
                          stock_pool_type=stock_pool,label_type='reg_次日开盘溢价_vwap_30')
    params = {}
    out_file_path = pred_output_path + f'{model_name}/{stock_pool}_{model_name}_trainPeriod{train_period}_predictPeriod{predict_period}_factorNum{factor_num}.pkl'
    params['val_pred_path'] = out_file_path.replace('.pkl', '_val_pred/')
    params['train_pred_path'] = out_file_path.replace('.pkl', '_train_pred/')
    #pred = dnn_model.rolling_train_and_predict(params=params, period=train_period,predict_period=predict_period,factor_num=factor_num)

    space = {
        'learning_rate': hp.uniform('learning_rate', 0.01, 0.1),
        'depth': hp.randint('depth', 3, 10),
        'l2_leaf_reg': hp.uniform('l2_leaf_reg', 1, 10),
        'boosting_type': hp.choice('boosting_type', ['Ordered', 'Plain']),
    }
    def hyperopt_objective(params):
        pred = dnn_model.rolling_train_and_predict(params=params, period=train_period,
                                                predict_period=predict_period,factor_num=factor_num)
        f1_score = metrics.mean_squared_error(pred['actual_label'], pred['prediction'])
        # print(f1_score)
        return f1_score

    best_param = hyperopt_wrapper(hyperopt_objective, space, verbose=True, max_evals=10)
    print(best_param)

    final_pred = pd.DataFrame()
    pred_file_path = out_file_path
    train_pred_path = pred_file_path.replace('.pkl','_val_pred/')
    test_pred_path = pred_file_path.replace('.pkl','_train_pred/')
    pct_threshold = 0.02
    for idx,cell in rolling_train_test_idx_list:
        tmp_predict_start_date,tmp_predict_end_date = cell[2],cell[3]
        tmp_train_pred = DataUtil.read_pickle(train_pred_path+'%d.pkl'%tmp_predict_start_date,verbose=False)
        tmp_val_pred = DataUtil.read_pickle(test_pred_path+'%d.pkl'%tmp_predict_start_date,verbose=False)
        tmp_test_pred = pred.loc[tmp_predict_start_date:tmp_predict_end_date].copy()
        quantile = tmp_train_pred[tmp_train_pred['prediction']>pct_threshold].count()/len(tmp_train_pred)
        threshold = np.quantile(tmp_val_pred['prediction'],1-quantile)[0]
        tmp_test_pred.loc[tmp_test_pred['prediction'] > threshold,'prediction'] = 1
        tmp_test_pred.loc[tmp_test_pred['prediction'] <= threshold, 'prediction'] = 0
        final_pred = pd.concat([final_pred,tmp_test_pred])
    DataUtil.save_pickle(final_pred, out_file_path)