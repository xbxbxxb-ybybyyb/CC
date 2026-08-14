# @Time : 2020/11/4 14:15
# @Author : Zhichen Lu
# @File : pitches_integration.py

import pandas as pd
import os
from sklearn import metrics
from sklearn.externals import joblib



    #'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoading5minFix_union_train200_test10_factor_num100_norm_window_40/'
# os.listdir('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NN_param_optimization/RNN5mintdse_train200_test10_factor_num100_norm_window_40_val_pred/')

def out_signal(base_path,end_date=None):
    # if os.path.exists(base_path[:-1]+'.pkl'):
    #     return
    # base_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40/'
    file_list = sorted(os.listdir(base_path))
    if not end_date is None:
        file_list = sorted(list(filter(lambda x : x<'%d.pkl'%end_date and x.endswith('.pkl'),file_list)))
    # file_list = sorted(list(filter(lambda x : x.endswith('pkl') and x.startswith('RNN5mintdse_train200_test10_factor_num100_norm_window_40'),file_list)))
    # file_list = sorted(list(filter(lambda x : x.endswith('pkl') and x.startswith('RNN5minmyloss_train200_test10_factor_num100_norm_window_40'),file_list)))
    file_list.sort()
    print(len(file_list))
    # check = pd.read_pickle(base_path+file_list[0])
    label = []
    corr_series = pd.Series()
    mae_series = pd.Series()
    for each in file_list:
        temp= pd.read_pickle(base_path+each)
        if (20211021,1400,688556) in temp.index.tolist():
            print(each)
        label.append(temp)
        if temp.shape[0]==0:
            continue
        corr_series[each.replace('.pkl','').split('_')[-1]] = temp.corr().values[0,1]
        mae_series[each.replace('.pkl','').split('_')[-1]] = metrics.mean_absolute_error(temp['actual_label'],temp['prediction'])

        # print(each.replace('.pkl','').split('_')[-1])

    label = pd.concat(label)

    # check = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NN_param_optimization/NNCorrStdAllPeriod_train200_test10_factor_num400_norm_window_40.pkl')
    res = pd.DataFrame({'corr':corr_series,'mae':mae_series})
    print(res.mean())
    print(label.index[-1],base_path)
    pd.to_pickle(label.sort_index(), base_path[:-1] + '.pkl')


def out_signal_zscore(base_path):
    # base_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/%s/'%each
    if os.path.exists(base_path[:-1]+'_zscore.pkl'):
        return
    file_list = os.listdir(base_path)
    # file_list = sorted(list(filter(lambda x : x.endswith('pkl') and x.startswith('RNN5mintdse_train200_test10_factor_num100_norm_window_40'),file_list)))
    # file_list = sorted(list(filter(lambda x : x.endswith('pkl') and x.startswith('RNN5minmyloss_train200_test10_factor_num100_norm_window_40'),file_list)))
    file_list.sort()
    # check = pd.read_pickle(base_path+file_list[0])
    label = []
    corr_series = pd.Series()
    mae_series = pd.Series()
    if not os.path.exists(base_path[:-1]+'_zscore_val_pred/'):
        os.mkdir(base_path[:-1]+'_zscore_val_pred/')
    for each in file_list:
        temp= pd.read_pickle(base_path+each)
        val_set = pd.read_pickle(base_path[:-1]+'_val_pred/'+each)
        val_set_mean = val_set.mean()
        val_set_std = val_set.std()
        val_set['prediction'] = (val_set['prediction'] - val_set_mean['prediction'])/val_set_std['prediction']
        temp['prediction'] = (temp['prediction'] - val_set_mean['prediction'])/val_set_std['prediction']
        pd.to_pickle(val_set,base_path[:-1]+'_zscore_val_pred/'+each)
        label.append(temp)
        corr_series[each.replace('.pkl','').split('_')[-1]] = temp.corr().values[0,1]
        mae_series[each.replace('.pkl','').split('_')[-1]] = metrics.mean_absolute_error(temp['actual_label'],temp['prediction'])
        print(each.replace('.pkl','').split('_')[-1])
    label = pd.concat(label)
    pd.to_pickle(label.sort_index(),base_path[:-1]+'_zscore.pkl')
    # check = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NN_param_optimization/NNCorrStdAllPeriod_train200_test10_factor_num400_norm_window_40.pkl')
    res = pd.DataFrame({'corr':corr_series,'mae':mae_series})
    print(base_path[:-1]+'_zscore.pkl')


# model_list = ['LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40',
#  'XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40',
#  'LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40',
#  'NNFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40',
#  'LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40',
#  'XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40',
#  'XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40',
#  'NNFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40',
#  'NNFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40']

# model_list = [
# '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample/',
#     '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/',
#
#         '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40/',
#         '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40/',
#         '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40/',
# ]
#
# model_list = [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_ic_half_c_ic_c_half_year//round_{i}/' for i in range(4)]+\
# [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_ic_half_d_ic_d_half_year//round_{i}/' for i in range(4)]
#
# for each in model_list:
#     out_signal(each,20201231)