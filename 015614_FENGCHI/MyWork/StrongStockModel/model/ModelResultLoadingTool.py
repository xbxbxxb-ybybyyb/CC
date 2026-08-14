# @Time : 2020/12/3 10:16
# @Author : Zhichen Lu
# @File : ModelResultLoadingTool.py

import pandas as pd
import os
import numpy as np
from dataApi.tradeDate import get_date_range

multi_index_order = {'new': ['date', 'time', 'code'], 'old': ['date', 'code', 'time']}
param_list = param_list = [(0, (20150309, 20151225, 20151228, 20160111)),
                           (1, (20150323, 20160111, 20160112, 20160125)),
                           (2, (20150407, 20160125, 20160126, 20160215)),
                           (3, (20150421, 20160215, 20160216, 20160229)),
                           (4, (20150506, 20160229, 20160301, 20160314)),
                           (5, (20150520, 20160314, 20160315, 20160328)),
                           (6, (20150603, 20160328, 20160329, 20160412)),
                           (7, (20150617, 20160412, 20160413, 20160426)),
                           (8, (20150702, 20160426, 20160427, 20160511)),
                           (9, (20150716, 20160511, 20160512, 20160525)),
                           (10, (20150730, 20160525, 20160526, 20160608)),
                           (11, (20150813, 20160608, 20160613, 20160624)),
                           (12, (20150827, 20160624, 20160627, 20160708)),
                           (13, (20150914, 20160708, 20160711, 20160722)),
                           (14, (20150928, 20160722, 20160725, 20160805)),
                           (15, (20151019, 20160805, 20160808, 20160819)),
                           (16, (20151102, 20160819, 20160822, 20160902)),
                           (17, (20151116, 20160902, 20160905, 20160920)),
                           (18, (20151130, 20160920, 20160921, 20161011)),
                           (19, (20151214, 20161011, 20161012, 20161025)),
                           (20, (20151228, 20161025, 20161026, 20161108)),
                           (21, (20160112, 20161108, 20161109, 20161122)),
                           (22, (20160126, 20161122, 20161123, 20161206)),
                           (23, (20160216, 20161206, 20161207, 20161220)),
                           (24, (20160301, 20161220, 20161221, 20170104)),
                           (25, (20160315, 20170104, 20170105, 20170118)),
                           (26, (20160329, 20170118, 20170119, 20170208)),
                           (27, (20160413, 20170208, 20170209, 20170222)),
                           (28, (20160427, 20170222, 20170223, 20170308)),
                           (29, (20160512, 20170308, 20170309, 20170322)),
                           (30, (20160526, 20170322, 20170323, 20170407)),
                           (31, (20160613, 20170407, 20170410, 20170421)),
                           (32, (20160627, 20170421, 20170424, 20170508)),
                           (33, (20160711, 20170508, 20170509, 20170522)),
                           (34, (20160725, 20170522, 20170523, 20170607)),
                           (35, (20160808, 20170607, 20170608, 20170621)),
                           (36, (20160822, 20170621, 20170622, 20170705)),
                           (37, (20160905, 20170705, 20170706, 20170719)),
                           (38, (20160921, 20170719, 20170720, 20170802)),
                           (39, (20161012, 20170802, 20170803, 20170816)),
                           (40, (20161026, 20170816, 20170817, 20170830)),
                           (41, (20161109, 20170830, 20170831, 20170913)),
                           (42, (20161123, 20170913, 20170914, 20170927)),
                           (43, (20161207, 20170927, 20170928, 20171018)),
                           (44, (20161221, 20171018, 20171019, 20171101)),
                           (45, (20170105, 20171101, 20171102, 20171115)),
                           (46, (20170119, 20171115, 20171116, 20171129)),
                           (47, (20170209, 20171129, 20171130, 20171213)),
                           (48, (20170223, 20171213, 20171214, 20171227)),
                           (49, (20170309, 20171227, 20171228, 20180111)),
                           (50, (20170323, 20180111, 20180112, 20180125)),
                           (51, (20170410, 20180125, 20180126, 20180208)),
                           (52, (20170424, 20180208, 20180209, 20180301)),
                           (53, (20170509, 20180301, 20180302, 20180315)),
                           (54, (20170523, 20180315, 20180316, 20180329)),
                           (55, (20170608, 20180329, 20180330, 20180416)),
                           (56, (20170622, 20180416, 20180417, 20180502)),
                           (57, (20170706, 20180502, 20180503, 20180516)),
                           (58, (20170720, 20180516, 20180517, 20180530)),
                           (59, (20170803, 20180530, 20180531, 20180613)),
                           (60, (20170817, 20180613, 20180614, 20180628)),
                           (61, (20170831, 20180628, 20180629, 20180712)),
                           (62, (20170914, 20180712, 20180713, 20180726)),
                           (63, (20170928, 20180726, 20180727, 20180809)),
                           (64, (20171019, 20180809, 20180810, 20180823)),
                           (65, (20171102, 20180823, 20180824, 20180906)),
                           (66, (20171116, 20180906, 20180907, 20180920)),
                           (67, (20171130, 20180920, 20180921, 20181012)),
                           (68, (20171214, 20181012, 20181015, 20181026)),
                           (69, (20171228, 20181026, 20181029, 20181109)),
                           (70, (20180112, 20181109, 20181112, 20181123)),
                           (71, (20180126, 20181123, 20181126, 20181207)),
                           (72, (20180209, 20181207, 20181210, 20181221))]


def get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                               tail=None,
                                                               end=None):
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    point_list = list(point_set_list[0])
    for i in range(len(point_set_list)):
        for j in range(i + 1, len(point_set_list)):
            if point_set_list[i] != point_set_list[j]:
                inter_set = point_set_list[i].intersection(point_set_list[j])
                if inter_set in [point_set_list[i], point_set_list[j]]:
                    point_list = sorted(list(inter_set))
                else:
                    raise Exception('Change point of models are not match!!')

    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)

    # threshold_series,mean_ret,signal_count,point_list = get_ret_distribution(pct, subset_path_list,val_tag=val_tag,loading_type=loading_type)
    subset_dict = {}
    for date in point_list:
        subset = {}
        for subset_path in subset_path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date).rename(columns={'future': val_tag, 0: val_tag})
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        subset_dict[date] = subset
        th = (subset[val_tag] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = subset['prediction'].quantile(th)
    threshold_series = threshold_series.reset_index()

    signal = {}
    for signal_file_name in signal_file_name_list:
        if end is None:
            signal[signal_file_name] = pd.read_pickle(signal_file_name).loc[start:]
        else:
            signal[signal_file_name] = pd.read_pickle(signal_file_name).loc[start:end]
    signal = pd.Panel(signal)
    signal_count = signal.count(axis=0)
    signal_sum = signal.sum(axis=0)
    signal = signal_sum / signal_count
    signal[signal_count.eq(0)] = np.nan

    signal = signal.reset_index()
    signal = signal.rename(columns={signal.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
    signal = signal.pivot_table(index=['date', 'time'], columns='code', values='prediction').fillna(0).sort_index()
    signal = signal.loc[start:]
    pred_ret = signal.copy()
    signal = signal.reset_index()
    signal['index'] = signal['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list)))).tolist()
    check = signal['date'].apply(lambda x: len(list(filter(lambda i: i < x, point_list))))

    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])
    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal > 0
    if get_subset:
        return signal, pred_ret, subset_dict
    return signal, pred_ret


def get_signal_by_val_pct_threshold_integration(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None, tail=None,
                                                end=None):
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    point_list = list(point_set_list[0])
    for i in range(len(point_set_list)):
        for j in range(i + 1, len(point_set_list)):
            if point_set_list[i] != point_set_list[j]:
                inter_set = point_set_list[i].intersection(point_set_list[j])
                if inter_set in [point_set_list[i], point_set_list[j]]:
                    point_list = sorted(list(inter_set))
                else:
                    raise Exception('Change point of models are not match!!')

    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)

    # threshold_series,mean_ret,signal_count,point_list = get_ret_distribution(pct, subset_path_list,val_tag=val_tag,loading_type=loading_type)
    subset_dict = {}
    for date in point_list:
        subset = {}
        for subset_path in subset_path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date).rename(columns={'future': val_tag, 0: val_tag})
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        subset_dict[date] = subset
        th = (subset[val_tag] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = max(subset['prediction'].quantile(th), 0.005)
    threshold_series = threshold_series.reset_index()

    signal = {}
    for signal_file_name in signal_file_name_list:
        if end is None:
            signal[signal_file_name] = pd.read_pickle(signal_file_name).loc[start:]
        else:
            signal[signal_file_name] = pd.read_pickle(signal_file_name).loc[start:end]
    signal = pd.Panel(signal)
    signal_count = signal.count(axis=0)
    signal_sum = signal.sum(axis=0)
    signal = signal_sum / signal_count
    signal[signal_count.eq(0)] = np.nan

    signal = signal.reset_index()
    signal = signal.rename(columns={signal.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
    signal = signal.pivot_table(index=['date', 'time'], columns='code', values='prediction').fillna(0).sort_index()
    signal = signal.loc[start:]
    pred_ret = signal.copy()
    signal = signal.reset_index()
    signal['index'] = signal['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list)))).tolist()
    check = signal['date'].apply(lambda x: len(list(filter(lambda i: i < x, point_list))))

    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])
    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal > 0
    if get_subset:
        return signal, pred_ret, subset_dict
    return signal, pred_ret


def get_signal_by_val_pct_threshold(pct, subset_path, signal_file_name, val_tag=0, loading_type=None, bar_list=None):
    point_list = os.listdir(subset_path)
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    for date in point_list:
        subset = pd.read_pickle(subset_path + '%d.pkl' % date)
        subset = subset.reset_index()
        # subset = subset.rename(columns={subset.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
        if not bar_list is None:
            subset = subset[subset['time'].isin(bar_list)]
        # subset = subset.set_index(['date','time','code'])
        th = (subset[val_tag] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = max(subset['prediction'].quantile(th), 0.005)
    threshold_series = threshold_series.reset_index()
    pred_ret = pd.read_pickle(signal_file_name)
    pred_ret = pred_ret.reset_index()
    pred_ret = pred_ret.rename(columns={pred_ret.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
    if not bar_list is None:
        pred_ret = pred_ret[pred_ret['time'].isin(bar_list)]
    pred_ret = pred_ret.pivot_table(index=['date', 'time'], columns='code', values='prediction').fillna(0).sort_index()
    pred_ret = pred_ret.reset_index()

    pred_ret['index'] = pred_ret['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list)))).tolist()
    signal = pd.merge(pred_ret, threshold_series, 'left', 'index').set_index(['date', 'time'])
    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal > 0
    return signal, pred_ret.drop('index', axis=1).set_index(['date', 'time'])


def get_val_ret_distribution(pct, subset_path_list, val_tag=0, loading_type=None):
    point_set_list = [set(os.listdir(subset_path)) for subset_path in subset_path_list]
    point_list = os.listdir(subset_path_list[0])
    for i in range(len(point_set_list)):
        for j in range(i + 1, len(point_set_list)):
            if point_set_list[i] != point_set_list[j]:
                inter_set = point_set_list[i].intersection(point_set_list[j])
                if inter_set in [point_set_list[i], point_set_list[j]]:
                    point_list = sorted(list(inter_set))
                else:
                    raise Exception('Change point of models are not match!!')
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    mean_ret = {}
    signal_count = {}
    for date in point_list:
        subset = {}
        for subset_path in subset_path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        th = (subset[val_tag] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = max(subset['prediction'].quantile(th), 0.005)
        subset = subset.reset_index()
        subset = subset.rename(columns={subset.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
        subset = subset[subset['prediction'] > threshold_series.loc[date, 'threshold']]
        mean_ret[date] = subset.groupby('time').mean()[val_tag]
        signal_count[date] = subset.groupby('time').size()
    mean_ret = pd.DataFrame(mean_ret)
    signal_count = pd.DataFrame(signal_count)
    return threshold_series, mean_ret, signal_count, point_list


def get_periodly_ret_distribute(file_name, signal, window=100, loading_type=None):
    original = pd.read_pickle(file_name).reset_index()
    original = original.rename(columns={original.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
    ret = original.pivot_table(index=['date', 'time'], columns='code', values='actual_label')
    ret = ret.reindex(signal.index, axis=0).reindex(signal.columns, axis=1)
    ret[~signal] = np.nan
    ret = ret.stack().to_frame().reset_index()
    ret = ret.pivot_table(index=['date', 'level_2'], columns=ret.columns[1], values=0)
    date_list = signal.index.levels[0].tolist()
    distribution_weight = pd.DataFrame(index=date_list, columns=ret.columns)
    for idx, date in enumerate(date_list):
        # print(date)
        if idx < window:
            distribution_weight.loc[date] = 0.01
            continue
        distribution_weight.loc[date] = ret.loc[date_list[idx - 101]:date_list[idx - 1]].mean()
    distribution_weight = (distribution_weight.T / distribution_weight.sum(axis=1)).T
    return distribution_weight


def get_rolling_threshold_with_no_val_set(pct_threshold, file_name, subset_path, val_tag=None, loading_type=None):
    point_list = os.listdir(subset_path)
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    pred_result = pd.read_pickle(file_name)
    pred_result['signal'] = np.nan
    for idx, cell in param_list:
        tain_start, train_end, test_start, test_end = cell
        if idx == 0:
            val_set = pd.read_pickle(subset_path + '%d.pkl' % train_end)
            percentile = (val_set[val_tag] < pct_threshold).sum() / val_set.shape[0]
            threshold = max(val_set['prediction'].quantile(percentile), 0.005)
        else:
            pre_tain_start, pre_train_end, pre_test_start, pre_test_end = param_list[idx - 1][1]
            val_set = pred_result.loc[pre_test_start:pre_test_end]
            percentile = (val_set['actual_label'] < pct_threshold).sum() / val_set.shape[0]
            threshold = max(val_set['prediction'].quantile(percentile), 0.005)
        pred_result.loc[test_start:test_end, 'signal'] = pred_result.at[test_start:test_end, 'prediction'] > threshold
    pred_result = pred_result.reset_index()
    pred_result = pred_result.rename(columns={pred_result.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
    pred_ret = pred_result.pivot_table(index=['date', 'time'], columns='code', values='prediction')
    signal = pred_result.pivot_table(index=['date', 'time'], columns='code', values='signal').fillna(False)
    return signal, pred_ret


def get_rolling_threshold_with_no_val_set_daily(pct_threshold, window, file_name, subset_path, val_tag=None, loading_type=None):
    point_list = os.listdir(subset_path)
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    pred_result = pd.read_pickle(file_name)
    pred_result['signal'] = np.nan
    tain_start, train_end, test_start, test_end = param_list[0][-1]
    val_set = pd.read_pickle(subset_path + '%d.pkl' % train_end)
    percentile = (val_set[val_tag] < pct_threshold).sum() / val_set.shape[0]
    threshold = max(val_set['prediction'].quantile(percentile), 0.005)
    pred_result.loc[test_start:test_end, 'signal'] = pred_result.at[test_start:test_end, 'prediction'] > threshold
    date_list = sorted(list(set([x[0] for x in pred_result.index])))
    start_idx = date_list.index(test_start)
    for idx, date in enumerate(date_list):
        if date <= test_end:
            continue
        val_set = pred_result.loc[date_list[max(0, idx - window)]:date_list[idx]]
        percentile = (val_set['actual_label'] < pct_threshold).sum() / val_set.shape[0]
        threshold = max(val_set['prediction'].quantile(percentile), 0.005)
        pred_result.loc[[date], 'signal'] = pred_result.loc[[date], 'prediction'] > threshold
    pred_result = pred_result.reset_index()
    pred_result = pred_result.rename(columns={pred_result.columns[i]: multi_index_order[loading_type][i] for i in range(3)})
    pred_ret = pred_result.pivot_table(index=['date', 'time'], columns='code', values='prediction')
    signal = pred_result.pivot_table(index=['date', 'time'], columns='code', values='signal').fillna(False)
    return signal, pred_ret


def zscorelize(source, target, end=20210518):
    target = os.path.join(target)
    target_super = os.path.abspath(os.path.join(target, os.path.pardir))
    if not os.path.exists(target_super):
        os.mkdir(target_super)
    source_dict = {
        'res': source.replace('.pkl', '/'),
        'val': source.replace('.pkl', '_val_pred/')
    }
    target_dict = {
        'res': target.replace('.pkl', '/'),
        'val': target.replace('.pkl', '_val_pred/')
    }
    for each in target_dict:
        if not os.path.exists(target_dict[each]):
            os.mkdir(target_dict[each])

    file_list = os.listdir(source_dict['res'])
    for each in sorted(file_list):
        if each > '%d.pkl' % end:
            continue
        res = pd.read_pickle(source_dict['res'] + each)
        if res.shape[0] == 0:
            continue
        val = pd.read_pickle(source_dict['val'] + each)
        mean, std = val['prediction'].mean(), val['prediction'].std()
        val['prediction'] = (val['prediction'] - mean) / std
        res['prediction'] = (res['prediction'] - mean) / std
        pd.to_pickle(val, target_dict['val'] + each)
        pd.to_pickle(res, target_dict['res'] + each)
        print(each)

# zscorelize(source='/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
# target = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/catboostnew2_ic_all_t.pkl')
# zscorelize(source='/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
#            target='/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/lightgbmnew_ic_all_t.pkl')
# for ind in ['ic_half_d','ic_half_t','ic_half_c']:
#     zscorelize(source='/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_%s_train200_test10_factor_num400_norm_window_40.pkl'%ind,
#            target='/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_%s_train200_test10_factor_num400_norm_window_40.pkl'%ind)
#

