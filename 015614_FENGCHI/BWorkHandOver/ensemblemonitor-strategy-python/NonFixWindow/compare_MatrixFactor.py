# @Time : 2022/2/24 10:46
# @Author : Zhichen Lu
# @File : compare_online_offline_PredRet.py

# from online_conf import non_fix_path,non_fix_output_path
import pandas as pd
from dataApi.getData import trans_int2windcode
from dataApi.FixFactorRollPrepare import load_fix_data_selfdefined_label,feature_engineering
from dataApi.FixFactorRollPrepare import load_dataset_from_multiple_add_selfdefine_label,load_fix_data
import os, time, gc
import pandas as pd
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
        test_nolimit[:] = True
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

    today = get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))
    # today = get_recent_trade_date()
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



# available_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3/available_factor_list.pkl')
fix_factor_list = ['TurnHighSkewRollingReg', 'VolCorr', 'HighLowStdRatio_meandivstd5']
label_add = f'/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/future_2_bar.npy'
# X, y_1day, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=20150105, end_date=20220323, factor_list=fix_factor_list,
#                         return_idx=True,address='/data/group/800442/800319/HFfactor/CrossIndutryMeanShiftV20220420/data/')
feature_adds = [
                # '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                '/data/group/800442/800319/HFfactor/CrossIndutryMeanShift/data/',
                '/data/group/800442/800319/HFfactor/CrossIndutryMeanShiftV20220420/data/']
fix_factor_list = list(filter(lambda x : os.path.exists(f'{feature_adds[1]}/{x}.npy'),fix_factor_list))
# fix_factor_lists = [[x[:-2] for x in fix_factor_list if x.endswith('_0')],[x[:-2] for x in fix_factor_list if x.endswith('_1')]]
fix_factor_lists = [fix_factor_list,fix_factor_list]
train_feature, train_label, test_feature, test_label = get_dataset_multi((20150106,20220120),(20220120,20220408),
                                    fix_factor_lists=fix_factor_lists,feature_addresses=feature_adds,label_path=label_add)

all_factor_list = [x+'_0' for x in fix_factor_list]+[x+'_1' for x in fix_factor_list]
train_feature.columns = all_factor_list
train_feature.columns = all_factor_list
train_feature = train_feature.sort_index(axis=1)

diff_train = abs(train_feature['TurnHighSkewRollingReg_0'] - train_feature['TurnHighSkewRollingReg_1'])
diff_test = abs(test_feature['TurnHighSkewRollingReg_0'] - test_feature['TurnHighSkewRollingReg_1'])

# test_feature = test_feature.rename(columns={
#   x:x[:-2] for x in fix_factor_list if x.endswith('_0')
# }).rename(columns={
#   x:x[:-2]+'_sw1' for x in fix_factor_list if x.endswith('_1')
# })

