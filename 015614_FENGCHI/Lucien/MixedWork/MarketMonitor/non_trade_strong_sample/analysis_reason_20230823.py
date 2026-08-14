# coding: utf-8
# Author：fengchi863
# Date ：2023/8/3 10:28
"""
使用不同的获取特征重要性的方式进行测试
"""
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import xgboost as xgb
import lime
import lime.lime_tabular

from xquant.factordata import FactorData
from dataApi.sendInfo import send_file

def _trans_train_test_minmaxscaler(_arr, n, median, mad, data_min, data_max):
    arr = _arr.copy()
    arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad), arr.shape[0], 0), arr)
    arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad), arr1.shape[0], 0), arr1)
    arr_scaled = (arr2 - data_min) / (data_max - data_min)
    return arr_scaled

# week_start_date = 20230726
# week_end_date = 20230801
# week_start_date = 20230802
# week_end_date = 20230808
week_start_date = 20230809
week_end_date = 20230815
date_list = get_date_range(week_start_date, week_end_date)
date_str_list = list(map(lambda x: str(x)[:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8], date_list))

trade_file = pd.read_excel(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}.xlsx', index_col=0, sheet_name=None)
europa = trade_file['Europa_first2']
jupiter = trade_file['Jupiter_first2']

europa_factor = pd.read_pickle(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}_europa_factor_value.pkl')
jupiter_factor = pd.read_pickle(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}_jupiter_factor_value.pkl')

model_path1 = '/data/user/015614/shared/for_wj/20230419_Europa_V20230329_rollTo20230331_prod/XgbFSV8RegModel/'
model_path2 = '/data/user/015614/junkData/XgbGainRegModel/'
model_path3 = '/data/user/015614/junkData/rffs_pct_WeightXgbRegModel/'
model_path4 = '/data/user/015614/junkData/rffs_pct_NoEmotionXgbRegModel/'

# factor_list_all = []
# for model_path in [model_path1, model_path2, model_path3, model_path4]:
#     factor_list = pd.read_json(model_path + '_factorName.json').iloc[:, 0].tolist()
#     factor_list_all = factor_list_all + factor_list
# factor_list_all = list(set(factor_list_all).difference(set(europa_factor.columns.tolist())))
# from LucienUtil.FileUtil import FileUtil
# FileUtil.save_list2pkl(factor_list_all, '/data/group/800463/sunss/复盘/周度无信号强势股/', f'factor_list_all.pkl')

res = pd.DataFrame(index=europa_factor.index, columns=[0,1,2,3])
for idx, model_path in enumerate([model_path1, model_path2, model_path3, model_path4]):
    print(model_path)
    model_fpath = model_path + 'XgbRegModel.pkl'
    xgb_model = xgb.Booster(model_file=model_fpath)
    # xbg_model = xgb.XGBRegressor(model_fpath=model_fpath)
    factor_list = pd.read_json(model_path + '_factorName.json').iloc[:, 0].tolist()
    threshold = pd.read_json(model_path + '_score_threshold.json').iloc[0, 0]
    factor_scaler = pd.read_json(model_path + '_factorScaler.json').set_index('factorName')

    _europa_factor = europa_factor[factor_list]
    X_scaled = pd.DataFrame(index=_europa_factor.index, columns=_europa_factor.columns)
    for factor in _europa_factor.columns.tolist():
        factor_n = factor_scaler.loc[factor, 'n']
        factor_median = factor_scaler.loc[factor, 'median']
        factor_mad = factor_scaler.loc[factor, 'mad']
        factor_min = factor_scaler.loc[factor, 'train_min']
        factor_max = factor_scaler.loc[factor, 'train_max']
        X_scaled[factor] = _trans_train_test_minmaxscaler(np.array(_europa_factor[factor]), factor_n, factor_median, factor_mad, factor_min, factor_max)

    pred_res = pd.DataFrame(index=_europa_factor.index)
    # pred_res['predReg'] = xgb_model.predict(xgb.DMatrix(pd.DataFrame(X_scaled.iloc[0]).T)).tolist()[0]
    pred_res['predReg'] = xgb_model.predict(xgb.DMatrix(X_scaled)).tolist()
    xgb_model.predict(xgb.DMatrix(X_scaled))
    pred_res['prediction'] = pred_res['predReg'] > threshold

    res[idx] = pred_res['prediction']

res.columns = ['prod', 'gain', 'weight', 'noEmotion']
res.sum(axis=0)
# predict_fn_xgb = lambda x: xgb_model.predict(xgb.DMatrix(pd.DataFrame(x).T)).tolist()[0]
# def predict_fn_xgb(X_arr):
#     feature_names = X_scaled.columns.tolist()
#     X_tmp = pd.DataFrame(X_arr, columns=feature_names)
#     pred = xgb_model.predict(xgb.DMatrix(X_tmp))
#     return pred
# # predict_fn_xgb(X_scaled.iloc[0].values)
# explainer = lime.lime_tabular.LimeTabularExplainer(X_scaled.values, feature_names=X_scaled.columns.tolist())
# exp = explainer.explain_instance(X_scaled.iloc[0].values, predict_fn_xgb, num_features=10)
# scores = exp.as_list()
# feature_dict = {}

# for idx in range(len(scores)):
#     score_item = scores[idx]
#     target = score_item[0]
#     score = score_item[1]
#     feature_dict[target] = score
#
# feature_dict = sorted(feature_dict.items(), key=lambda x: abs(float(x[1])), reverse=True)
