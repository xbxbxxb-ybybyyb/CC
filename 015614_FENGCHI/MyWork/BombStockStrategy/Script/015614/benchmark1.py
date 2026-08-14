# coding: utf-8
# Author：fengchi863
# Date ：2021/11/16 17:47

import warnings
import random
import numpy as np
import pandas as pd
from sklearn import metrics
from ShortTermTrading.Util.tools import save_pickle
from ShortTermTrading.conf.path_conf import junk_path
from BombStockStrategy.conf.model_param_config import best_param_clf_xgb
from BombStockStrategy.model.ModelImpl.XGBModelClf import XGBModelClf
from BombStockStrategy.DataPreprosessing.Sampling import Sampling
from BombStockStrategy.backtest.zhaban_backtest import start_backtest

warnings.filterwarnings('ignore')
random.seed(2021)

sample_dict = {
    'min_zt_time': 10,
    'min_close': 5,
    'max_upper_shadow_pct': 0.3,
    'min_high_down_pct': 0.01
}

if __name__ == '__main__':
    xgb_model = XGBModelClf(start_date=20140101, end_date=20201231)
    xgb_model.set_skf(n_splits=5)
    train_samples, predict_samples = xgb_model.get_dataset(filename='samples_Label2_20211105',
                                                           train_start_date=20140101,
                                                           train_end_date=20191231,
                                                           predict_start_date=20200101,
                                                           predict_end_date=20201231)

    train_samples, predict_samples = Sampling.sample(train_samples, predict_samples, sample_dict)

    # 使用部分因子进行训练
    factor_name_list = ['Close',
                        'HighDownPct',
                        'LenZtMin',
                        'UpperShadowPct',
                        ]

    train_samples = train_samples[factor_name_list + ['label']]
    predict_samples = predict_samples[factor_name_list + ['label']]

    factor_scaler_list = []
    # need_scaler_list = list(set(factor_name_list).difference(set(del_factor_list)))
    # factor_scaler_list.append((need_scaler_list, MinMaxScaler()))
    non_scaler_list = factor_name_list
    X_y_train_test_list = xgb_model.convert_data_4_train_and_test(train_samples, non_scaler_list, *factor_scaler_list)
    best_model = xgb_model.train_and_test_cv(X_y_train_test_list, best_param_clf_xgb)
    _, X_test, _, y_test = xgb_model.convert_data_4_predict(train_samples, predict_samples, non_scaler_list,
                                                           *factor_scaler_list)
    # 在样本外预测
    y_pred = xgb_model.predict(best_model, X_test)
    accuracy = metrics.accuracy_score(y_test, y_pred)
    precision = metrics.precision_score(y_test, y_pred)
    recall = metrics.recall_score(y_test, y_pred)
    f1_score = metrics.f1_score(y_test, y_pred)
    print('准确率：%.4f，精准率：%.4f，召回率：%.4f， F1分数：%.4f' %
          (accuracy, precision, recall, f1_score))
    confuse_metrics = metrics.confusion_matrix(y_test, y_pred)
    print(confuse_metrics)

    # 得到回测结果，转移成DataFrame供回测使用
    signal_df = pd.DataFrame(y_pred.astype('float32'), index=predict_samples.index, columns=['prediction']).\
        unstack().fillna(0).droplevel(0, axis=1)

    junk_path = junk_path + '20211116/'
    filename = 'zhaban_benchmark1.pkl'
    signal_df_path = junk_path + filename
    save_pickle(signal_df, junk_path, filename)

    # 进行回测
    print('开始进行回测')
    output_path = junk_path + 'zhaban_benchmark1_bt_result.xlsx'
    start_backtest(start_date=20200101,
                   end_date=20201231,
                   signal_df_path=junk_path + filename,
                   output_path=output_path)