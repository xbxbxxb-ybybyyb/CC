# @Time : 2021/3/10 14:45
# @Author : Zhichen Lu
# @File : compare_online_offline_Pred.py
import pandas as pd
# from online_conf import daily_out_path,local_config_path
from dataApi.getData import trans_int2windcode
from ExtraTools import get_path_conf
from dataApi.getData import trans_int2windcode, trans_windcode2int
from dataApi.tradeDate import get_pre_trade_date
import numpy as np
import os

# online_path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForMatrix/')
online_path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForMixSim/')
daily_out_path, local_config_path = online_path_conf['daily_out_path'], online_path_conf['local_config_path']


def get_intersec(date, pre_date, file_name, path_conf):
    code_list_path, holding_info_path = path_conf['code_list_path'], path_conf['holding_info_path']
    offline_signal, offline_pred_ret = pd.read_pickle(file_name)
    code_list = pd.read_pickle(code_list_path + '%d.pkl' % pre_date)
    holding_info = pd.read_pickle(holding_info_path + '%d.pkl' % pre_date)
    holding_info.pop('cash')
    code_list = set(code_list).union(set(holding_info.keys()))
    code_list = [int(x[:-3]) for x in code_list]
    # .loc[1000]
    offline_signal = offline_signal.reindex(code_list, axis=1).fillna(False)
    if date == 20210730:
        print(1)

        holding = pd.read_pickle(f'{holding_info_path}{get_pre_trade_date(date)}.pkl')
        holding.pop('cash')
        offline_signal[list(map(trans_windcode2int, holding.keys()))] = False
    signal = pd.DataFrame()
    summary = pd.read_pickle(f'{daily_out_path}/{date}.pkl')
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        if os.path.exists(daily_out_path + '/%d.pkl' % date):
            online_output = pd.read_pickle(daily_out_path + '/%d.pkl' % date)
            online_bar_signal = online_output['signal'][time_point]
        elif os.path.exists(f'{daily_out_path}{date}/{time_point}_summary.pkl'):
            online_output = pd.read_pickle(f'{daily_out_path}/{date}/{time_point}_summary.pkl')
            online_bar_signal = online_output['signal']  # [time_point]
        else:
            online_bar_signal = pd.Series()
        offline_bar_signal = offline_signal.loc[date].loc[time_point]
        offline_bar_signal = offline_bar_signal[offline_bar_signal]

        offline_bar_pred_ret = offline_pred_ret.loc[date].loc[time_point]  # .loc[offline_bar_signal.index]

        online_bar_signal.index = [int(x[:-3]) for x in online_bar_signal.index]
        online_bar_pred_ret = summary['pred_ret'][time_point].mean(axis=1).copy()  #
        online_bar_pred_ret.index = online_bar_pred_ret.index.map(trans_windcode2int)
        online_bar_pred_ret = online_bar_pred_ret  # .loc[online_bar_signal.index]

        online_bar_signal.loc[:] = True
        bar = pd.DataFrame({'online_signal': online_bar_signal, 'offline_signal': offline_bar_signal,
                            'online_pred': online_bar_pred_ret, 'offline_pred': offline_bar_pred_ret})
        bar = bar.reset_index()
        bar['time'] = time_point
        bar = bar.set_index(['time', 'index'])
        signal = signal.append(bar)

    triggered_stk_num = (offline_signal.groupby('date').sum() > 0).sum(axis=1)
    unavailable_pool = pd.read_pickle(path_conf['local_config_path'] + 'restrict_list.pkl')
    offline_unavailabel_stk = set([x[1] for x in signal.index]).intersection(set(unavailable_pool))
    if date == 20210702:
        print(1)
    signal = signal.swaplevel(0, 1)
    signal.loc[list(offline_unavailabel_stk)] = np.nan
    # signal = signal.dropna()#>0.5
    signal[['online_signal', 'offline_signal']] = signal[['online_signal', 'offline_signal']] > 0.5
    inter_sec = signal[(signal['online_signal']) & (signal['offline_signal'])]
    XOR = signal[~((signal['online_signal']) == (signal['offline_signal']))]
    signal_info = signal.sum()
    signal_info['intersection'] = inter_sec.shape[0]
    signal_info['线下触发股票数量'] = triggered_stk_num[date]
    return signal_info, XOR, signal


# signal_info,XOR,signal = get_intersec(20210715,20210714,'/data/user/015664/AFuckingTrigger/for5minFactor/sample_20210702_20210716.pkl',online_path_conf)
signal_info, XOR, signal = get_intersec(20211012, get_pre_trade_date(20211012),
                                        '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测Ray/信号/signal_OutSample_XGB_Cat_Light_OnlineTest_20211104.pkl', online_path_conf)
# signal_info,XOR,signal = get_intersec(20210406,20210402,
#                     '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测Matrix/信号/signal_OutSample_XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val_OnlineTest_20210415.pkl',
#                                       online_path_conf)

signal.corr()
check = signal[signal['online_signal'] != signal['offline_signal']]
# signal_info,XOR,signal = get_intersec(20210715,20210714,
#     '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_XGB_Cat_Light_OnlineTest_20210812.pkl',
#                                       online_path_conf)
signal = signal[signal['offline_signal'] | signal['online_signal']]
check = signal[~signal['online_signal']]
check_nolimit = check[~np.isclose(check['online_pred'], check['offline_pred'])]
# signal_real
signal_info['intersection'] / signal_info

date = 20210813
update_date = 20210730
summary = pd.read_pickle(daily_out_path + '%d.pkl' % date)
model_list = {
    'XGB_D': '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal//XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_d_ic_h_d/',
    'XGB_T': '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_t_ic_h_t/',
    'XGB_C': '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_c_ic_h_c/',
    'lightGBM_T': '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample/',
    'CatBoost_T': '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/',
}

# model_list = {
#     'XGB_D': '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_d/',
#     'XGB_T': '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_t/',
#     'XGB_C': '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_c/',
#     'lightGBM_T': '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample/',
#     'CatBoost_T': '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/',
# }


pred = summary['pred_ret']
offline_pred = {}
for each in model_list:
    offline_pred[each] = pd.read_pickle(model_list[each] + '%d.pkl' % update_date).loc[date, 'prediction']

offline_pred = pd.DataFrame(offline_pred)
offline = {}
for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
    offline[time_point] = offline_pred.loc[time_point]
    offline[time_point].index = offline[time_point].index.map(trans_int2windcode)
    offline[time_point] = offline[time_point].loc[pred[time_point].index]
# offline_1000 = offline_pred.loc[1000]
# offline_1000.index = offline_1000.index.map(trans_int2windcode)
# offline_1000 = offline_1000.loc[pred[1000].index]

from WithNewFactor.XGBRegressionFactorEvalMultiFreqFix5MinDeltaEraForTest import load_dataset, get_fix_factor_evaluation, get_5min_factor_evaluation
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442//800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
train_start, train_end, test_start, test_end = para_list[137][1]

indicator_fix, indicator_daily = 'ic_d', 'ic_h_d'

fix_factor_list = get_fix_factor_evaluation(200, train_end, eval_indicator=indicator_fix)
min5_factor_list = get_5min_factor_evaluation(200, train_end, eval_indicator=indicator_daily)

X, y = load_dataset(test_start, test_end, fix_factor_list, min5_factor_list)
X_offline, y_offline = X.loc[date].loc[1000], y.loc[date].loc[1000]
X_offline.index = X_offline.index.map(trans_int2windcode)
X_online = pd.read_pickle('/data/user/015664/AFuckingTrigger/for5minFactor/sample_online_20210715_1000.pkl')
X_offline = X_offline.loc[X_online.index]


def compare_factor(date, path_conf):
    # path_conf = online_path_conf
    local_config_path = '/data/group/800319/strategy_local_path3_ForMix/'  # path_conf['local_config_path']
    fix_online = pd.read_pickle(f'{local_config_path}validation/factor{date}.pkl')
    min5_online = pd.read_pickle(f'{local_config_path}validation/factor{date}_5min.pkl')

    fix_online_df, min5_online_df = [], []
    for time_point in fix_online:
        fix_online_df.append(fix_online[time_point].rename(index={x: (trans_windcode2int(x), time_point) for x in fix_online[time_point].index}))
        min5_online_df.append(min5_online[time_point].rename(index={x: (trans_windcode2int(x), time_point) for x in min5_online[time_point].index}))
    fix_online_df, min5_online_df = pd.concat(fix_online_df), pd.concat(min5_online_df)
    return fix_online_df, min5_online_df


# from FactorCalculator.RealTime import MinFactorCalculator
# mfc = MinFactorCalculator(20210715)
# mfc.calc_bar_data(1000,0,threads=10)
# factor_online = mfc.factor.T[min5_factor_list].copy()
# factor_online.index = factor_online.index.map(trans_int2windcode)
# factor_offline = X_offline[min5_factor_list]


from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering

X_5min, y_5min, nolimit_5min, idx_date_5min, idx_code_5min, idx_time_5min = load_fix_data(start_date=test_start, end_date=test_end, factor_list=min5_factor_list,
                                                                                          address='/arch1/group/800442/800319/MinFactor/FactorFixData/Factor/')
X, y, idx_date, idx_code, idx_time = feature_engineering(X_5min, y_5min, nolimit_5min, idx_date_5min, idx_code_5min, idx_time_5min)
index = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
X = pd.DataFrame(X, index=index)
X_offline = X.loc[20210715].loc[1000]
X_offline.index = X_offline.index.map(trans_int2windcode)
X_offline = X_offline.loc[X_online.index]
X_online_check = X_online[X_online.columns]
# X_online = factor_online[1000][X_offline.columns]

from dataApi.tradeDate import get_date_range

for date in get_date_range(20210802, 20210813):
    if not os.path.exists(f'/data/group/800442/800319/strategy_HFfactor/{date}/'):
        os.makedirs(f'/data/group/800442/800319/strategy_HFfactor/{date}/TmrMinMaterial/')
        os.makedirs(f'/data/group/800442/800319/strategy_HFfactor/{date}/TmrDesampleMaterial/')
        os.makedirs(f'/data/group/800442/800319/strategy_HFfactor/{date}/TmrLowFreq/')
        os.makedirs(f'/data/group/800442/800319/strategy_HFfactor/{date}/DateCode/')
        os.makedirs(f'/data/group/800442/800319/strategy_HFfactor/{date}/TmrMeanStd/')

