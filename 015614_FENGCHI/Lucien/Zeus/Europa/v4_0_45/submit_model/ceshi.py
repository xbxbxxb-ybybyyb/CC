# coding: utf-8
# Author：fengchi863
# Date ：2023/11/5 9:54

import pandas as pd
import numpy as np
import json
import xgboost as xgb
import lightgbm as lgb

def infer(data_df, factor_list_file, model_file, begin_date, end_date, threshold_file, datapro_file=None):
    raw_data = data_df.copy()
    factor_list = pd.read_json(factor_list_file).iloc[:, 0].tolist()
    factor_data = raw_data.query(f'dt >= {begin_date} & dt <= {end_date}')[factor_list]
    if 'Xgb' in model_file:
        model = xgb.Booster(model_file=model_file)
    if 'Lgb' in model_file:
        model = lgb.Booster(model_file=model_file)

    factor_scaler = pd.read_json(datapro_file).set_index('factorName')
    threshold = pd.read_json(threshold_file).iloc[0, 0]
    factor_data = factor_data[factor_list]
    X_scaled = pd.DataFrame(index=factor_data.index, columns=factor_data.columns)
    if 'S1' in model_file:
        for factor in factor_data.columns.tolist():
            factor_n = factor_scaler.loc[factor, 'n']
            factor_median = factor_scaler.loc[factor, 'median']
            factor_mad = factor_scaler.loc[factor, 'mad']
            factor_min = factor_scaler.loc[factor, 'train_min']
            factor_max = factor_scaler.loc[factor, 'train_max']
            X_scaled[factor] = _trans_train_test_minmaxscaler(np.array(factor_data[factor]), factor_n, factor_median, factor_mad, factor_min, factor_max)
    elif 'S2' in model_file:
        for factor in factor_data.columns.tolist():
            factor_std = factor_scaler.loc[factor, 'std']
            factor_mean = factor_scaler.loc[factor, 'mean']
            X_scaled[factor] = _trans_train_test_standardscaler(np.array(factor_data[factor]), factor_mean, factor_std)

    if 'Xgb' in model_file:
        all_result = model.predict(xgb.DMatrix(X_scaled))
    if 'Lgb' in model_file:
        all_result = model.predict(X_scaled)
    factor_data['pred_Reg'] = all_result
    factor_data['prediction'] = (factor_data['pred_Reg'] > threshold).astype(int)
    return factor_data[['pred_Reg', 'prediction']], X_scaled

def _trans_train_test_minmaxscaler(_arr, n, median, mad, data_min, data_max):
    arr = _arr.copy()
    arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad), arr.shape[0], 0), arr)
    arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad), arr1.shape[0], 0), arr1)
    arr_scaled = (arr2 - data_min) / (data_max - data_min)
    return arr_scaled

def _trans_train_test_standardscaler(_arr, mean, std):
    arr = _arr.copy()
    arr_scaled = (arr - mean) / std
    return arr_scaled

if __name__ == '__main__':
    data_fpath = '/data/group/800463/sunss/europa/20240501/factor_df_all_20160101_20220531.pkl'
    # root_dir = '/data/user/015614/shared/for_wj/strategy_model/Europa/fac_20240501/区间4/FcLgb/'
    root_dir = '/data/user/015614/shared/for_wj/strategy_model/Europa/fac_20240501/区间5/base_S2FSV11Lgb/'
    datapro_file = root_dir + 'Model_roll_factorScaler.json'
    factor_list_file = root_dir + 'Model_roll_factorName.json'
    threshold_file = root_dir + 'Model_config.json'
    model_file = root_dir + 'model_seed0.pkl'
    begin_date = '20211201'
    end_date = '20220531'
    data_df = pd.read_pickle(data_fpath)
    result, scaled_df = infer(data_df, factor_list_file, model_file, begin_date, end_date, threshold_file, datapro_file=datapro_file)