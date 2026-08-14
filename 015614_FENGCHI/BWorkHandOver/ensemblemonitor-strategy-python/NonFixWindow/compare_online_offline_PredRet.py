# @Time : 2022/2/24 10:46
# @Author : Zhichen Lu
# @File : compare_online_offline_PredRet.py

from online_conf import non_fix_path,non_fix_output_path
import pandas as pd
from dataApi.getData import trans_int2windcode
from dataApi.FixFactorRollPrepare import load_fix_data_selfdefined_label,feature_engineering
from dataApi.FixFactorRollPrepare import load_dataset_from_multiple_add_selfdefine_label
import os, time, gc
import numpy as np
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date
import datetime

def get_dataset( train_idx, test_idx, fix_factor_list,feature_address,label_path ):
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time, y_1day_train = \
            load_fix_data_selfdefined_label(train_idx[0],get_pre_trade_date(train_idx[-1]),fix_factor_list,address=feature_address,label_path=label_path,return_1day_label=True)
    else:
        train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time, y_1day_train = \
            load_fix_data_selfdefined_label(train_idx[0], train_idx[-1],fix_factor_list,address=feature_address,label_path=label_path,return_1day_label=True)
    train_feature, train_label, train_idx_date, train_idx_time, train_idx_code, y_1day_train = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                                   train_idx_time, train_idx_code, y_1day_train)
    train_feature = train_feature
    index_train = pd.MultiIndex.from_tuples(list(zip(train_idx_date.tolist(), train_idx_time.tolist(), train_idx_code.tolist())))
    train_feature, train_label = pd.DataFrame(train_feature, index=index_train, columns=fix_factor_list), \
                                 pd.DataFrame({'actual_label': train_label, '1_day_label': y_1day_train}, index=index_train)

    today = int(datetime.date.today().strftime('%Y%m%d'))
    today = get_recent_trade_date(today)
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        test_feature, test_label = pd.DataFrame(columns=fix_factor_list), pd.DataFrame(columns=fix_factor_list)
    else:
        if test_idx[-1] >= today:
            test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time, y_1day = load_fix_data_selfdefined_label(start_date=test_idx[0],
                                                                                                                                          end_date=get_pre_trade_date(today),
                                                                                                                                          factor_list=fix_factor_list,
                                                                                                                                          return_idx=True,
                                                                                                                                          address=feature_address,
                                                                                                                                          label_path=label_path,
                                                                                                                                          return_1day_label=True)
        else:
            test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time, y_1day = load_fix_data_selfdefined_label(start_date=test_idx[0],
                                                                                                                                          end_date=test_idx[-1],
                                                                                                                                          factor_list=fix_factor_list,
                                                                                                                                          return_idx=True,
                                                                                                                                          address=feature_address,
                                                                                                                                          label_path=label_path,
                                                                                                                                          return_1day_label=True)
        # test_label = np.concatenate((test_label, np.zeros((test_feature.shape[1] - test_label.shape[0], 7))))
        test_nolimit[np.isnan(test_label)] = True
        test_label[np.isnan(test_label)] = 0
        # test_nolimit = np.concatenate((test_nolimit, np.ones((test_feature.shape[1] - test_nolimit.shape[0], 7)) > 0))
        test_feature, test_label, test_idx_date, test_idx_time, test_idx_code, y_1day = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
                                                                                                            test_idx_time, test_idx_code, y_1day)

        index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))

        test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=fix_factor_list), \
                                   pd.DataFrame({'actual_label': test_label, '1_day_label': y_1day}, index=index_test)

    return train_feature, train_label, test_feature, test_label

def get_dataset_multi(train_idx, test_idx, fix_factor_lists,feature_addresses,label_path):
    # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
    #                                load_address=self.feature_address)
    gc.collect()
    e = time.time()
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        train_feature, train_label = load_dataset_from_multiple_add_selfdefine_label(train_idx[0],
                                        get_pre_trade_date(train_idx[-1]), fix_factor_lists, feature_addresses,label_path=label_path,return_1day_label=True)
    else:
        train_feature, train_label = load_dataset_from_multiple_add_selfdefine_label(train_idx[0],
                                        train_idx[-1], fix_factor_lists, feature_addresses,label_path=label_path,return_1day_label=True)

    # today = int(datetime.date.today().strftime('%Y%m%d'))
    today = get_recent_trade_date()
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        test_feature, test_label = pd.DataFrame(), pd.DataFrame()
    else:
        if test_idx[-1] >= today:
            test_feature, test_label = load_dataset_from_multiple_add_selfdefine_label(test_idx[0],
                                today, fix_factor_lists, feature_addresses,tail_no_future=True,label_path=label_path,return_1day_label=True)
        else:
            test_feature, test_label = load_dataset_from_multiple_add_selfdefine_label(test_idx[0],
                                test_idx[-1], fix_factor_lists, feature_addresses,label_path=label_path,return_1day_label=True)
    return train_feature, train_label, test_feature, test_label

model_list = {
    'XGB_D': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_%d_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
    'XGB_T': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_%d_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
    'XGB_C': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_%d_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',

    'XGB_D_Matrix': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_%d_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
   'XGB_T_Matrix': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_%d_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
   'XGB_C_Matrix' : f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_%d_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
     'LightGBM_T':f'/data/group/800442/800319/wyl/model_record/nonfix/future_%d_bar/lightgbm_all_sample_ic_all_t/',
     'CatBoost_T':f'/data/group/800442/800319/wyl/model_record/nonfix/future_%d_bar/catboost_all_sample_ic_all_t/',
}
date = 20220516
update_date = 20220429
future_window =1
offline_all = {}
for each in model_list:
    offline_all[each] = pd.read_pickle(f'{model_list[each]%future_window}{update_date}.pkl')['prediction']
offline_all = pd.DataFrame(offline_all)
time_point = 1430
summary = pd.read_pickle(f'{non_fix_output_path}/{date}/final_summary.pkl')

online_1000 = summary['pred_ret'][time_point][future_window]
offline_1000 = offline_all.loc[(date,time_point)]
offline_1000.index = offline_1000.index.map(trans_int2windcode)
offline_1000 = offline_1000.loc[online_1000.index]
model_corr = offline_1000.corrwith(online_1000)

model_tag = 'XGB_T_Matrix'
label_add = f'/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/future_{future_window}_bar.npy'
fix_factor_list = pd.read_pickle(f'{(model_list[model_tag]%future_window)[:-1]}_factor_list/{update_date}.pkl')
# fix_factor_list = np.load(f'{(model_list[model_tag]%future_window)[:-1]}_train_features/{update_date}.npy').tolist()
model_conf = pd.read_pickle(f'{non_fix_path}/model_conf/{update_date}/Future_{future_window}_bar.pkl')

# model_conf['model_conf'][model_tag][-1]['fix']==fix_factor_list

if 'Matrix' in model_tag:
    feature_adds = ['/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                                    '/data/group/800442/800319/HFfactor/CrossIndutryMeanShift/data/']
    fix_factor_lists = [[x[:-2] for x in fix_factor_list if x.endswith('_0')],[x[:-2] for x in fix_factor_list if x.endswith('_1')]]
    train_feature, train_label, test_feature, test_label = get_dataset_multi((update_date,update_date),(date,date),
                                        fix_factor_lists=fix_factor_lists,feature_addresses=feature_adds,label_path=label_add)
    test_feature = test_feature.rename(columns={
      x:x[:-2] for x in fix_factor_list if x.endswith('_0')
    }).rename(columns={
      x:x[:-2]+'_sw1' for x in fix_factor_list if x.endswith('_1')
    })
else:
    feature_add ='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/'

    train_feature, train_label, test_feature, test_label = get_dataset((update_date,update_date),(date,date),
                                                                       fix_factor_list=fix_factor_list,feature_address=feature_add,label_path=label_add)

online_factor = pd.read_pickle(f'{non_fix_output_path}/factor/{date}/{time_point}.pkl')
online_facotr_1000 = online_factor[future_window][model_tag]
offline_factor_1000 = test_feature.loc[(date,time_point)]
offline_factor_1000.index = offline_factor_1000.index.map(trans_int2windcode)
offline_factor_1000 = offline_factor_1000.loc[online_facotr_1000.index]
corr = offline_factor_1000.corrwith(online_facotr_1000).sort_values(ascending=False)

# prob_factor = 'RetToVolabs_sw1'
# compare = pd.DataFrame({
#     'online':online_facotr_1000[prob_factor],
#     'offline':offline_factor_1000[prob_factor]
# })
# compare.corr()

import xgboost as xgb

model = xgb.Booster(model_file=model_list[model_tag][:-1]%future_window+f'_model_conf/{update_date}.json')
model.set_param('predictor','cpu_predictor')
# model = pd.read_pickle(model_list[model_tag][:-1]%future_window+f'_model_conf/{update_date}.pkl')
res_compare = pd.DataFrame({
    'online':model.predict(xgb.DMatrix(online_facotr_1000)),
    'offline':model.predict(xgb.DMatrix(offline_factor_1000)),
})


model_onlie = xgb.Booster(model_file=model_conf['model_conf'][model_tag][1].replace('strategy_local_path3','strategy_local_path_nonfix'))

model_onlie.set_param('predictor','cpu_predictor')

res_compare_online_model = pd.DataFrame({
    'online':model_onlie.predict(xgb.DMatrix(online_facotr_1000)),
    'offline':model_onlie.predict(xgb.DMatrix(offline_factor_1000)),
})

