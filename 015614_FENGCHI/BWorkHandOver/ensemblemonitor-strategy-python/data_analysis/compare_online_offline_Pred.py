# @Time : 2021/3/10 14:45
# @Author : Zhichen Lu
# @File : compare_online_offline_Pred.py

import pandas as pd
# from online_conf import daily_out_path,local_config_path
from dataApi.getData import trans_int2windcode
from ExtraTools import get_path_conf
online_path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
daily_out_path,local_config_path = online_path_conf['daily_out_path'],online_path_conf['local_config_path']

date = 20211215
update_date = 20211130
summary = pd.read_pickle(daily_out_path+'%d.pkl'%date)
model_list = {
    'XGB_D': '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d/',
    'XGB_T': '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t/',
    'XGB_C': '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c/',
    'lightGBM_T': '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample/',
    'CatBoost_T': '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/',

}

pred = summary['pred_ret']
offline_pred = {}
for each in model_list:
    offline_pred[each] = pd.read_pickle(model_list[each]+'%d.pkl'%update_date).loc[date,'prediction']

offline_pred = pd.DataFrame(offline_pred)
offline_1000 = offline_pred.loc[1000]
offline_1000.index = offline_1000.index.map(trans_int2windcode)
offline_1000 = offline_1000.loc[pred[1000].index,pred[1000].columns]
compare = pd.DataFrame({'online':pred[1000].mean(axis=1),'offline':offline_1000.mean(axis=1)})
signal = compare>0.005173092262754873

############check factor difference


from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
import numpy as np
from dataApi.getData import trans_int2windcode
using_factor_list = pd.read_pickle(local_config_path+'using_fix_list.pkl')
# dp = FixFactorRollPrepare(start_date=date,end_date=date, freq=7, model_time_len=1,factor_list=using_factor_list,load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=date,end_date=date,return_idx=True,factor_list=using_factor_list)

X, y, idx_date, idx_time, idx_code = feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)

factor = pd.read_pickle('/data/user/015664/temp_factor.pkl')
factor_direction = pd.read_pickle('/data/group/800319/strategy_local_path/factor_direction.pkl')
offline_factor = pd.DataFrame(X,index=pd.MultiIndex.from_tuples(list(zip(idx_time.tolist(),[trans_int2windcode(x) for x in idx_code.tolist()]))),columns=using_factor_list)
offline_factor = offline_factor.loc[1000].loc[factor.index,factor.columns]
offline_factor = offline_factor*factor_direction[offline_factor.columns]
import xgboost as xgb
model = xgb.Booster()
model.load_model('/data/group/800319/strategy_local_path3/model/XGB_D/20210618.json')
model.predict()
pred_compare = pd.DataFrame({'online':model.predict(xgb.DMatrix(factor)),
                             'offline':model.predict(xgb.DMatrix(offline_factor))},index=factor.index)


compare = pd.DataFrame({'online':factor.loc['000001.SZ'],'offline':offline_factor.loc['000001.SZ']})
compare[(~np.isclose(compare['online'].fillna(0),compare['offline']))&((compare['online'].fillna(0)*compare['offline'])<0).values].shape


model_conf_online = pd.read_pickle('/data/group/800319/strategy_local_path_active_pool/model_conf/model_conf20210601.pkl')
model_conf_online2 = pd.read_pickle('/data/group/800319/strategy_local_path3/model_conf/model_conf20210616.pkl')
available_factor_list =  pd.read_csv('/data/group/800319/junkData/StrongStock/external_data/实盘可支持Fix因子列表.csv').T.reset_index().T[0].tolist()
import os

exist_factor = list(map(lambda x : x[8:-4],os.listdir('/data/group/800002/realtime/alpha//x_day_lib/20210616/1100/')))
pd.to_pickle(exist_factor,local_config_path + 'available_factor_list.pkl')
len(available_factor_list)

online_factor_list = model_conf_online[0]['XGB_D'][2]
online_factor_list2 = model_conf_online2[0]['XGB_D'][2]
offline_factor_list = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40_factor_list/20210601.pkl')
len(set(online_factor_list2).intersection(offline_factor_list))
available_factor_list = pd.read_pickle()

import time,os

recieve_time = {}
for each in factor.columns:
    tm = time.localtime(os.path.getmtime(f'/data/group/800002/realtime/alpha//x_day_lib/20210702/1000//Fix1000_{each}.pkl'))
    recieve_time[each] = tm.tm_hour*100 + tm.tm_min
recieve_time = pd.Series(recieve_time).sort_values()



