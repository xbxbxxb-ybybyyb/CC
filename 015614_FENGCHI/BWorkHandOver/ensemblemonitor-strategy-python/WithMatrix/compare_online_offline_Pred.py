# @Time : 2021/3/10 14:45
# @Author : Zhichen Lu
# @File : compare_online_offline_Pred.py

import pandas as pd
# from online_conf import daily_out_path,local_config_path
from dataApi.getData import trans_int2windcode
from ExtraTools import get_path_conf
online_path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
local_config_path =online_path_conf['local_config_path']
daily_out_path = '/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/daily_output/'

date = 20220114
update_date = 20220112
summary = pd.read_pickle(daily_out_path+'%d.pkl'%date)
model_list = {
        'lightGBM_T':'/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample/',
         'CatBoost_T': '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/',
'XGB_D_Matrix':f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400/',
'XGB_T_Matrix':f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400/',
'XGB_C_Matrix':f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400/',
'XGB_D':'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400/',
'XGB_T':'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400/',
'XGB_C':'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400/',

}
# import shutil
# for each in model_list:
#     shutil.copy(
#         model_list[each].replace('800442','800442_old')[:-1]+f'_model_conf/{update_date}.json',
#         model_list[each][:-1]+f'_model_conf/{update_date}.json',
#                 )
#     shutil.copy(
#         model_list[each].replace('800442', '800442_old')[:-1] + f'_val_pred/{update_date}.pkl',
#         model_list[each][:-1] + f'_val_pred/{update_date}.pkl',
#     )
#

pred = summary['pred_ret']
offline_pred = {}
for each in model_list:
    offline_pred[each] = pd.read_pickle(model_list[each]+'%d.pkl'%update_date).loc[date,'prediction']
    if len(list(offline_pred[each].index.levels[0]))>242:
        offline_pred[each].index = offline_pred[each].index.swaplevel(0,1)

offline_pred = pd.DataFrame(offline_pred)
offline_1000 = offline_pred.loc[1000]
offline_1000.index = offline_1000.index.map(trans_int2windcode)
offline_1000 = offline_1000.loc[pred[1000].index,pred[1000].columns]
compare = pd.DataFrame({'online':pred[1000].mean(axis=1),'offline':offline_1000.mean(axis=1)})

online_1000 = pred[1000][offline_1000.columns]


# signal = compare>0.005173092262754873

############check factor difference


from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
import numpy as np
import pandas as pd
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date,get_recent_trade_date
import gc,datetime,time


def load_dataset_from_multiple_add(start, end, factor_lists, addresses,tail_no_future=False):
    print(addresses)
    idx_date, idx_time, idx_code, nolimit, y = None, None, None, None, None
    col = []
    X = []
    for idx_add, add, factor_list in zip(list(range(len(addresses))), addresses, factor_lists):
        col += [f'{x}_{idx_add}' for x in factor_list]
        X1, y1, nolimit1, idx_date1, idx_code1, idx_time1 = load_fix_data(start, end, factor_list, address=add)
        if idx_date is None:
            nolimit, idx_date, idx_time, idx_code, y = nolimit1.copy(), idx_date1.copy(), idx_time1.copy(), idx_code1.copy(), y1.copy()
        else:
            if (idx_date != idx_date1).sum() or (idx_time != idx_time1).sum() or (idx_code != idx_code1).sum():
                raise Exception(f'Nonidentical idx of {start} {end} {add}')
            if (nolimit != nolimit1).sum():
                raise Exception(f'Nonidentical nolimit flag of {start} {end} {add}')
            close = np.isclose(y,y1)
            both_nan = np.isnan(y) & np.isnan(y1)
            close[both_nan] = True
            if (~close).sum():
                raise Exception(f'Nonidentical label of {start} {end} {add}')
        X.append(X1)
    X = np.concatenate(tuple(X), axis=0)
    if tail_no_future:
        print('Newest day -------------------------')
        nolimit[np.isnan(y)] = True
        y[np.isnan(y)] = 0
    X, y, idx_date, idx_time, idx_code = feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_code, idx_time)))

    X = pd.DataFrame(X, columns=col, index=index)
    y = pd.DataFrame({'actual_label': y}, index=index)
    return X, y

def get_dataset(train_idx, test_idx, fix_factor_lists,feature_addresses):
    # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
    #                                load_address=self.feature_address)
    gc.collect()
    e = time.time()
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        train_feature, train_label = load_dataset_from_multiple_add(train_idx[0], get_pre_trade_date(train_idx[-1]), fix_factor_lists, feature_addresses)
    else:
        train_feature, train_label = load_dataset_from_multiple_add(train_idx[0], train_idx[-1], fix_factor_lists, feature_addresses)

    # today = int(datetime.date.today().strftime('%Y%m%d'))
    today = get_recent_trade_date()
    if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
        test_feature, test_label = pd.DataFrame(), pd.DataFrame()
    else:
        if test_idx[-1] >= today:
            test_feature, test_label = load_dataset_from_multiple_add(test_idx[0], today, fix_factor_lists, feature_addresses,tail_no_future=True)
        else:
            test_feature, test_label = load_dataset_from_multiple_add(test_idx[0], test_idx[-1], fix_factor_lists, feature_addresses)
    print('tail index',test_feature.index[-1])
    return train_feature, train_label, test_feature, test_label, time.time() - e


# date = 20220221
model_conf = pd.read_pickle(online_path_conf['model_config_path']+f'model_conf{update_date}.pkl')

model_tag = 'XGB_D_Matrix'#'CatBoost_T'
factor_list = model_conf[0][model_tag][2]['fix']
online_saved_factor = pd.read_pickle(daily_out_path+f'{date}/factor/1000.pkl')
online_factor = online_saved_factor[model_tag]
if 'Matrix' in model_tag:
    train_feature, train_label, test_feature, test_label, train_time = get_dataset((get_pre_trade_date(date,5),get_pre_trade_date(date,5)),(get_pre_trade_date(date,4),date),[factor_list,factor_list],
                                                                               ['/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                                    '/data/group/800442/800319/HFfactor/CrossIndutryMeanShift/data/'])
    offline_factor = test_feature.copy()
    offline_factor.columns = [x[:-2] for x in offline_factor.columns[:200]] + [x[:-2]+'_sw1' for x in offline_factor.columns[200:]]
    offline_factor.index = offline_factor.index.swaplevel(1,2)

    offline_factor = offline_factor.loc[date].loc[1000]#.loc[online_factor.index, online_factor.columns]
    offline_factor.index = offline_factor.index.map(trans_int2windcode)
    offline_factor = offline_factor.loc[online_factor.index, online_factor.columns]

else:
    using_factor_list = pd.read_pickle(local_config_path+'using_fix_list.pkl')
    # dp = FixFactorRollPrepare(start_date=date,end_date=date, freq=7, model_time_len=1,factor_list=using_factor_list,load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
    X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=date,end_date=date,return_idx=True,factor_list=factor_list)
    y[np.isnan(y)] = 0
    nolimit[:] = True
    X, y, idx_date, idx_time, idx_code = feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)
    factor_direction = pd.read_pickle(online_path_conf['local_config_path']+'/factor_direction.pkl')
    offline_factor = pd.DataFrame(X,index=pd.MultiIndex.from_tuples(list(zip(idx_time.tolist(),[trans_int2windcode(x) for x in idx_code.tolist()]))),columns=factor_list)
    offline_factor = offline_factor.loc[1000].loc[online_factor.index, online_factor.columns]
    offline_factor = offline_factor*factor_direction[offline_factor.columns]
offline_factor.corrwith(offline_factor).sort_values(ascending=False)
factor_name = 'RetToVolabs_sw1'
compare_factor = pd.DataFrame({
    'online':online_factor[factor_name],
    'offline':offline_factor[factor_name]
})

# offline_factor_train = pd.read_pickle('/data/user/015664_old/validateset.pkl')
# offline_factor_train.index = offline_factor_train.index.map(trans_int2windcode)
import xgboost as xgb
model = xgb.Booster()
# model.load_model(f'{local_config_path}/model/XGB_D/{update_date}.json')
model.load_model(f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400_model_conf/{update_date}.json')
model.set_param('predictor','cpu_predictor')
pred_compare = pd.DataFrame({'online':model.predict(xgb.DMatrix(online_factor)),
                             'offline':model.predict(xgb.DMatrix(offline_factor)),
                             # 'offline_train':model.predict(xgb.DMatrix(offline_factor_train))

                             }, index=online_factor.index)


compare = pd.DataFrame({'online':online_factor.loc['000009.SZ'], 'offline':offline_factor.loc['000009.SZ']})
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
import pandas as pd






abs(origin_compare['offline'] - origin_compare['online']).mean()