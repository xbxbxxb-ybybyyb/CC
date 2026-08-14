# coding: utf-8
# Author：fengchi863
# Date ：2021/4/23 16:09
'''
测试两种方法
1、根据每个预测期的分位数值来确定0-1；
2、根据训练期中的样本分布来确定阈值；
'''
from LimitUpPredStrategy.conf.path_conf import pred_output_path, label_path
from LimitUpPredStrategy.Util.DataUtil import DataUtil
from LimitUpPredStrategy.model.ModelImpl.RollingXGBModelReg import RollingXGBModelReg
import numpy as np, pandas as pd
import os

model_name = 'linear_reg'
factor_num = 280
train_period = 60
predict_period = 10
pred_file_path = pred_output_path + f'{model_name}_20210805/{model_name}_trainPeriod{train_period}_predictPeriod{predict_period}_factorNum{factor_num}.pkl'
pred = DataUtil.read_pickle(pred_file_path)

r2s_kind = 'r2s3'

xgb_model = RollingXGBModelReg(start_date=20150101, end_date=20191231)
rolling_train_test_idx_list = xgb_model.get_rolling_index(train_period, predict_period)

def convert_reg2signal(kind='r2s1', pct_threshold=None):
    if kind == 'r2s1': # 用到了未来信息
        ### 第一种方式 ###
        quantile = 0.4 # 阈值
        final_pred = pd.DataFrame()
        for idx, cell in rolling_train_test_idx_list:
            tmp_start_date, tmp_end_date = cell[2], cell[3]
            tmp_pred = pred.loc[tmp_start_date:tmp_end_date].copy()
            threshold = np.quantile(tmp_pred['prediction'], quantile) # 直接使用pred数据强制用分位数来编制
            tmp_pred.loc[tmp_pred['prediction'] > threshold, 'prediction'] = True
            tmp_pred.loc[tmp_pred['prediction'] <= threshold, 'prediction'] = False
            final_pred = pd.concat([final_pred, tmp_pred])

        DataUtil.save_pickle(final_pred, pred_output_path + f'{model_name}' + pred_file_path[:-4] + '_signal_r2s1.pkl')

    elif kind == 'r2s2': # 用到了未来信息
        ### 第二种方式 ###
        # 这种方式可以调节滚动时间进行设置，等于说是把最近的信息用在市场中
        label_type = 'reg_次日开盘溢价'
        final_pred = pd.DataFrame()
        label = pd.read_pickle(label_path + label_type + '.pkl') # 使用label来读取真实标签，因为第一轮需要使用到没在prediction中的信息
        for idx, cell in rolling_train_test_idx_list:
            tmp_train_start_date, tmp_train_end_date = cell[0], cell[1]
            tmp_predict_start_date, tmp_predict_end_date = cell[2], cell[3]
            tmp_train = label.loc[tmp_train_start_date:tmp_train_end_date].copy()
            tmp_pred = pred.loc[tmp_predict_start_date:tmp_predict_end_date].copy()
            quantile = tmp_train[tmp_train['label'] > pct_threshold].count() / len(tmp_train)
            threshold = np.quantile(tmp_pred['prediction'], quantile)[0]
            tmp_pred.loc[tmp_pred['prediction'] > threshold, 'prediction'] = True
            tmp_pred.loc[tmp_pred['prediction'] <= threshold, 'prediction'] = False
            final_pred = pd.concat([final_pred, tmp_pred])

        DataUtil.save_pickle(final_pred, pred_output_path + f'{model_name}' + os.path.split(pred_file_path)[-1].replace('.pkl', '_signal_r2s2.pkl'))

    elif kind == 'r2s3':
        ### 第三种方式 ###
        final_pred = pd.DataFrame()
        train_pred_path = pred_file_path.replace('.pkl', '_val_pred/')
        test_pred_path = pred_file_path.replace('.pkl', '_train_pred/')
        for idx, cell in rolling_train_test_idx_list:
            tmp_predict_start_date, tmp_predict_end_date = cell[2], cell[3]
            tmp_train_pred = DataUtil.read_pickle(train_pred_path + '%d.pkl' % tmp_predict_start_date, verbose=False)
            tmp_val_pred = DataUtil.read_pickle(test_pred_path + '%d.pkl' % tmp_predict_start_date, verbose=False)
            tmp_test_pred = pred.loc[tmp_predict_start_date:tmp_predict_end_date].copy()
            quantile = tmp_train_pred[tmp_train_pred['prediction'] > pct_threshold].count() / len(tmp_train_pred)
            threshold = np.quantile(tmp_val_pred['prediction'], 1-quantile)[0]
            tmp_test_pred.loc[tmp_test_pred['prediction'] > threshold, 'prediction'] = True
            tmp_test_pred.loc[tmp_test_pred['prediction'] <= threshold, 'prediction'] = False
            final_pred = pd.concat([final_pred, tmp_test_pred])

        DataUtil.save_pickle(final_pred, pred_output_path + f'{model_name}/' + os.path.split(pred_file_path)[-1].replace('.pkl', f'_pctThreshold{pct_threshold}_signal_r2s3.pkl'))

if __name__ == '__main__':
    pct_threshold = 0.03
    convert_reg2signal(kind=r2s_kind, pct_threshold=pct_threshold)