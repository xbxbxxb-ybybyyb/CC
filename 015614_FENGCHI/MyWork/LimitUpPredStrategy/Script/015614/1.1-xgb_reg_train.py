# coding: utf-8
# Author：fengchi863
# Date ：2021/4/20 16:16

import random
random.seed(2021)
from LimitUpPredStrategy.model.ModelImpl.RollingXGBModelReg import RollingXGBModelReg
from LimitUpPredStrategy.conf.model_param_config import best_param_clf_xgboost
from LimitUpPredStrategy.conf.path_conf import pred_output_path
from LimitUpPredStrategy.Util.DataUtil import DataUtil
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    model_name = 'xgb_reg'
    factor_num = 80
    train_period = 60
    predict_period = 10

    xgb_model = RollingXGBModelReg(start_date=20150101, end_date=20191231)
    xgb_model.set_dataset(train_start_date=20140101, train_end_date=20191231,
                    predict_start_date=20200101, predict_end_date=20201231,
                    stock_pool_type='all_board',
                    label_type='reg_次日开盘溢价')
    out_file_path = pred_output_path + f'{model_name}_20210518/{model_name}_trainPeriod{train_period}_predictPeriod{predict_period}_factorNum{factor_num}.pkl'
    best_param_clf_xgboost['val_pred_path'] = out_file_path.replace('.pkl', '_val_pred/')
    best_param_clf_xgboost['train_pred_path'] = out_file_path.replace('.pkl', '_train_pred/')
    label = xgb_model.rolling_train_and_predict(params=best_param_clf_xgboost, period=train_period, predict_period=predict_period, factor_num=factor_num)
    DataUtil.save_pickle(label, out_file_path)
