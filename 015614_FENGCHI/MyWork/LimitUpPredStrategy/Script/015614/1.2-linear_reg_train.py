# coding: utf-8
# Author：fengchi863
# Date ：2021/5/14 10:13

import random
random.seed(2021)
from LimitUpPredStrategy.model.ModelImpl.RollingLinearModelReg import RollingLinearModelReg
from LimitUpPredStrategy.conf.model_param_config import best_param_clf_lr
from LimitUpPredStrategy.conf.path_conf import pred_output_path
from LimitUpPredStrategy.Util.DataUtil import DataUtil
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    model_name = 'linear_reg'
    factor_num = 75
    train_period = 60
    predict_period = 10

    lr_model = RollingLinearModelReg(start_date=20150101, end_date=20191231)
    lr_model.set_dataset(train_start_date=20150101, train_end_date=20191231,
                    predict_start_date=20200101, predict_end_date=20201231,
                    stock_pool_type='all_board',
                    label_type='reg_次日开盘溢价_vwap_30') # 修改一处
    out_file_path = pred_output_path + f'{model_name}_20210805/{model_name}_trainPeriod{train_period}_predictPeriod{predict_period}_factorNum{factor_num}.pkl'
    best_param_clf_lr['val_pred_path'] = out_file_path.replace('.pkl', '_val_pred/')
    best_param_clf_lr['train_pred_path'] = out_file_path.replace('.pkl', '_train_pred/')
    label = lr_model.rolling_train_and_predict(params=best_param_clf_lr, period=train_period, predict_period=predict_period, factor_num=factor_num)
    DataUtil.save_pickle(label, out_file_path)