# @Time : 2021/1/17 17:48
# @Author : Zhichen Lu
# @File : check_factor_difference.py

import pandas as pd
import os
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
import numpy as np

date = 20210105
path = '/data/group/800319/strategy_local_path3_fake_online/validation/'
XOR = pd.read_pickle('/data/user/015664/AFuckingTrigger/online_stat_v20210209Fake_online/XOR.pkl')
online_data = pd.read_pickle(path + 'factor%d.pkl'%date)
target = XOR[date].swaplevel(0,1).index.tolist()

online = pd.DataFrame()

for time_point in online_data:
    bar_factor = online_data[time_point]
    bar_factor.index = [int(x[:-3]) for x in bar_factor.index]
    bar_factor = bar_factor.reset_index()
    bar_factor['time'] = time_point
    bar_factor = bar_factor.set_index(['time','index'])
    online = online.append(bar_factor)


dp = FixFactorRollPrepare(start_date=date, end_date=date, freq=7, model_time_len=1, factor_list=online.columns.tolist(),
                 load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')

X, y,nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=date, end_date=date, return_idx=True)
X, y, idx_date, idx_time, idx_code = dp.feature_engineering(X, y,nolimit, idx_date, idx_time, idx_code)

offline = pd.DataFrame(X,index=pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code))),columns=online.columns.tolist())
# offline = offline.clip(-5,5)
offline = offline.loc[date]

check_offline = offline.loc[target]
check_online = online.loc[target]

diff = pd.DataFrame({'offline':check_offline.loc[target[0]],'online':check_online.loc[target[0]]})
(diff['offline'].fillna(0) - diff['online'].fillna(0)).apply(abs).max()
"""
offline_app_factor = pd.read_pickle('/data/group/800319/strategy_local_path2/validation/factor_offline20201026.pkl')
offline_app = pd.DataFrame()
for time_point in offline_app_factor:
    bar_factor = offline_app_factor[time_point]
    bar_factor.index = [int(x[:-3]) for x in bar_factor.index]
    bar_factor = bar_factor.reset_index()
    bar_factor['time'] = time_point
    bar_factor = bar_factor.set_index(['time','index'])
    offline_app = offline_app.append(bar_factor)

indexes = set(offline.index).intersection(set(online.index)).intersection(set(offline_app.index))


"""
indexes = set(offline.index).intersection(set(online.index))#.intersection(set(offline_app.index))
all_factor = {
    'offlineHX':offline.reindex(indexes),
    # 'offline_app':offline_app.reindex(indexes),
    'online':online.reindex(indexes)
}

corr = {
    # 'offline_app_to_offlineHX':{},
    #     'offline_app_to_online':{},
        'offlineHX_to_online':{}}

mae = {
    # 'offline_app_to_offlineHX':{},
    #     'offline_app_to_online':{},
        'offlineHX_to_online':{}}
# offline = offline.reindex(offline_app.index)
for each in online.columns.tolist():
    # corr['offline_app_to_offlineHX'][each] = all_factor['offline_app'][each].corr(all_factor['offlineHX'][each])
    # corr['offline_app_to_online'][each] = all_factor['offline_app'][each].corr(all_factor['online'][each])
    corr['offlineHX_to_online'][each] = all_factor['offlineHX'][each].corr(all_factor['online'][each])
    # mae['offline_app_to_offlineHX'][each] = abs(all_factor['offline_app'][each]-all_factor['offlineHX'][each]).mean()
    # mae['offline_app_to_online'][each] = abs(all_factor['offline_app'][each]-all_factor['online'][each]).mean()
    mae['offlineHX_to_online'][each] = abs(all_factor['offlineHX'][each]-all_factor['online'][each]).mean()

corr_df = pd.DataFrame(corr)
mae_df = pd.DataFrame(mae)
# corr_direction = pd.Series(corr['offlineHX_to_online'])/pd.Series(corr['offlineHX_to_online']).apply(abs)
# pd.to_pickle(corr_direction,'/data/group/800319/strategy_local_path2/factor_direction.pkl')

factor_map = {'CatBoost_T': '/data/group/800319/strategy_local_path3/factor_list/20201229/ic_all_t_400_factor_list_post_disease_era.pkl',
 'XGB_C': '/data/group/800319/strategy_local_path3/factor_list/20201229/ic_half_c_400_factor_list.pkl',
 'XGB_D': '/data/group/800319/strategy_local_path3/factor_list/20201229/ic_half_d_400_factor_list.pkl',
 'XGB_T': '/data/group/800319/strategy_local_path3/factor_list/20201229/ic_half_t_400_factor_list.pkl',
 'lightGBM_T': '/data/group/800319/strategy_local_path3/factor_list/20201229/ic_all_t_400_factor_list_post_disease_era.pkl'}

import xgboost as xgb
from online_conf import model_path,model_config_path
from catboost import CatBoostRegressor
import lightgbm as lgb
from sklearn.externals import joblib
model_D = xgb.Booster()
model_T = xgb.Booster()
model_C = xgb.Booster()

factor_map = {
    x:pd.read_pickle(factor_map[x]) for x in factor_map
}
last_update_date = 20201229
model_D.load_model(model_path+'XGB_D/%d.json'%last_update_date)
model_D.set_param('predictor','cpu_predictor')
model_T.load_model(model_path+'XGB_T/%d.json'%last_update_date)
model_T.set_param('predictor','cpu_predictor')
model_C.load_model(model_path+'XGB_C/%d.json'%last_update_date)
model_C.set_param('predictor','cpu_predictor')

ligtGBM_T = joblib.load(model_path+'lightGBM_T/%d.pkl'%last_update_date)
CatBoost_T = joblib.load(model_path+'CatBoost_T/%d.pkl'%last_update_date)

d_matrix = {x:{model:xgb.DMatrix(all_factor[x].fillna(0)[factor_map[model]] ) if model.startswith('XGB') else all_factor[x].fillna(0)[factor_map[model]] for model in factor_map } for x in all_factor}

pred = {
    x:pd.DataFrame({'XGB_D':model_D.predict(d_matrix[x]['XGB_D']),
                    'XGB_T':model_T.predict(d_matrix[x]['XGB_T']),
                    'XGB_C':model_C.predict(d_matrix[x]['XGB_C']),
                    'CatBoost_T':CatBoost_T.predict(d_matrix[x]['CatBoost_T']),
                    'lightGBM_T':ligtGBM_T.predict(d_matrix[x]['lightGBM_T'])},index=indexes) for x in all_factor
}
offline_pred = pred['offlineHX'].loc[target]
online_pred = pred['online'].loc[target]

compare = pd.DataFrame({
    'online': online_pred.drop('CatBoost_T', axis=1).mean(axis=1),
    'offline':offline_pred.drop('CatBoost_T',axis=1).mean(axis=1)
                       })


compare_item = pd.DataFrame({
    'online': online_pred.drop('CatBoost_T', axis=1).loc[(300142,1000)],
    'offline':offline_pred.drop('CatBoost_T',axis=1).loc[(300142,1000)]
                       })
validate = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl').loc[date]
validate = validate.loc[pred['online'].index, 'prediction']

############

#############
compare = pd.DataFrame({
    x:pred[x].mean(axis=1) for x in pred
})
tag = 'OutSample_XGB_Cat_Light_OnlineTest'
offline_signal,offline_pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s.pkl'%tag)
offline_day_pred_ret = offline_pred_ret.loc[date].unstack()
compare['load_from_offline'] = offline_day_pred_ret.swaplevel(0,1).loc[compare.index]


_,threshold = pd.read_pickle('/data/group/800319/strategy_local_path3/model_conf/model_conf%d.pkl'%last_update_date)
signal = compare>threshold

signal['load_signal_from_offline'] = offline_signal.loc[date].unstack().swaplevel(0,1).loc[compare.index]

check = signal[(signal['offlineHX'])&(~signal['online'])]

check_compare = compare.loc[check.index]
check_sample = pd.DataFrame({all_factor[x].loc[(1330,2486),factor_list_d] for x in all_factor})

check_sample = pd.DataFrame({x:all_factor[x].loc[(1000,603606),factor_list_d] for x in all_factor})
model_D.predict(xgb.DMatrix(check_sample.T))
# check_sample = check_sample.loc[check_sample.std(axis=1).sort_values(ascending=False).index]
check_nan = check_sample[check_sample.isnull()['online']]

from online_conf import realtime_path,local_config_path


check_factor = pd.read_pickle(realtime_path+'x_day_lib/20201026/1000/Fix1000_AbnormalPriceDiff.pkl')
local_config_path

code_list = pd.read_pickle('/data/group/800319/strategy_local_path/code_list/20201023.pkl')
factor_mean = pd.read_pickle('/data/group/800319/strategy_local_path/factor_hyper_param2/mean20201023.pkl')


check_offline_factor = pd.read_pickle('/data/group/800002/alpha_factor/lib/x_factor_lib//Fix1000_GTJA5.pkl').loc['20201026']
check_onfline_factor = pd.read_pickle('/data/group/800002/realtime/alpha//x_day_lib/20201026/1000//Fix1000_GTJA5.pkl').loc['20201026']

dp_check = FixFactorRollPrepare(start_date=20201026, end_date=20201026, freq=7, model_time_len=1, factor_list=['GTJA5'],
                 load_address='/data/group/800319/HFfactor/RealTimeFixRollMv/data/')

X, y, idx_date, idx_time, idx_code = dp_check.load_data(start_date=20201026, end_date=20201026, return_idx=True)
X, y, idx_date, idx_time, idx_code = dp_check.feature_engineering(X, y, idx_date, idx_time, idx_code)

check_offlineHX = pd.DataFrame(X[:,0,:],index=pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code))),columns=['GTJA5'])
check_offlineHX.loc[(20201026,1000,603606),'GTJA5'],check_offline_factor.loc['603606.SH'],check_onfline_factor.loc['603606.SH']