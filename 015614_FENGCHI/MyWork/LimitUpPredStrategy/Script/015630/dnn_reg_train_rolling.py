# coding: utf-8
# Author：fengchi863
# Date ：2021/4/1 14:33

import random
random.seed(2021)
from LimitUpPredStrategy.Util.DataUtil import DataUtil
from LimitUpPredStrategy.model.ModelImpl.RollingDNNModelReg import RollingDNNModelReg
from LimitUpPredStrategy.conf.path_conf import pred_output_path


import warnings
import pandas as pd
import pickle
import gc
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    model_name = 'rolling_dnn_reg'
    factor_num = 60
    train_period = 60
    predict_period = 5
    stock_pool = 'virga2consis_board'
    dnn_model = RollingDNNModelReg(start_date=20150101, end_date=20191231)
    dnn_model.set_dataset(train_start_date=20140101, train_end_date=20191231,
                          predict_start_date=20200101, predict_end_date=20201231,
                          stock_pool_type='virga2consis_board')
    params = {}
    out_file_path = pred_output_path + f'{model_name}/{stock_pool}_{model_name}_trainPeriod{train_period}_predictPeriod{predict_period}_factorNum{factor_num}.pkl'
    params['val_pred_path'] = out_file_path.replace('.pkl', '_val_pred/')
    params['train_pred_path'] = out_file_path.replace('.pkl', '_train_pred/')
    label = dnn_model.rolling_train_and_predict(params=params, period=train_period,
                                                predict_period=predict_period,factor_num=factor_num)
    DataUtil.save_pickle(label, out_file_path)