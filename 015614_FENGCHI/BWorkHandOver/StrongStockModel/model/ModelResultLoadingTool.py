# @Time : 2020/12/3 10:16
# @Author : Zhichen Lu
# @File : ModelResultLoadingTool.py

import pandas as pd
import os
import numpy as np
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from tqdm import tqdm
from multiprocessing import Pool

multi_index_order = {'new': ['date', 'time', 'code'], 'old': ['date', 'code', 'time']}


def get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                               tail=None,
                                                               end=None):
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) <= end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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
            temp = pd.read_pickle(subset_path + '%d.pkl' % date)
            if isinstance(temp, list):
                subset[subset_path] = temp[1].rename(columns={'future': val_tag, 0: val_tag})
            else:
                subset[subset_path] = temp.rename(columns={'future': val_tag, 0: val_tag})
            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
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
        if len(list(signal[signal_file_name].index.levels[1])) > 242:
            signal[signal_file_name].index = signal[signal_file_name].index.swaplevel(1, 2)
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
    # check = signal['date'].apply(lambda x: len(list(filter(lambda i: i < x, point_list))))

    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])
    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal > 0
    if get_subset:
        return signal, pred_ret, subset_dict
    return signal, pred_ret


def get_pre_sold_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False,
                                                                        head=None,
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
        th = (subset[val_tag] < -abs(pct)).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = subset['prediction'].quantile(th)
        print(date, th, subset['prediction'].quantile(th))
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

    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])
    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal < 0
    if get_subset:
        return signal, pred_ret, subset_dict
    return signal, pred_ret


def get_signal_by_val_pct_threshold_integration(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                tail=None,
                                                end=None):
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) <= end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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
            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
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
        if len(list(signal[signal_file_name].index.levels[1])) > 242:
            signal[signal_file_name].index = signal[signal_file_name].index.swaplevel(1, 2)
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
        # print(each)
    return True


def get_signal_by_revised_distribution(pct, subset_path_list, signal_file_name_list, start, get_subset=False, head=None, tail=None, end=None):
    # file_list = ['/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t/',
    # '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t/',
    # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400/',
    # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400/',
    # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400/',]
    #
    # subset_path_list = [
    #     '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_val_pred/',
    #     '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_val_pred/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400_val_pred/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400_val_pred/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400_val_pred/',
    # ]

    # head = None
    # tail = None
    # start,end = 20170101,20210531

    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) <= end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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

    from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
    from dataApi.tradeDate import get_pre_trade_date

    hyper_start = get_pre_trade_date(point_list[0], 202)

    train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(hyper_start, end, ['zhy_fix_313'])
    train_feature[np.isnan(train_feature)] = 0
    train_feature, train_label, train_idx_date, train_idx_time, train_idx_code = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                     train_idx_time, train_idx_code)
    # future = pd.Series(train_label,index = pd.MultiIndex.from_tuples(list(zip(train_idx_date,train_idx_time,train_idx_code)))).unstack()
    future_series = pd.Series(train_label, index=pd.MultiIndex.from_tuples(list(zip(train_idx_date, train_idx_time, train_idx_code))))

    down = [x * 0.01 for x in [-100] + list(range(-9, 11))]
    up = [x * 0.01 for x in list(range(-9, 11)) + [100]]
    interval = list(zip(down, up))
    hyper_start = {}
    for down, up in interval:
        hyper_start[f'[{down},{up})'] = ((future_series >= down) & (future_series < up)).groupby(level=0).sum()
    hyper_start = pd.DataFrame(hyper_start)
    hyper_start['total'] = hyper_start.sum(axis=1)
    hyper_start_roll_200 = hyper_start.rolling(200).sum()
    hyper_start_roll_200 = (hyper_start_roll_200.T / hyper_start_roll_200['total']).T

    # threshold_series,mean_ret,signal_count,point_list = get_ret_distribution(pct, subset_path_list,val_tag=val_tag,loading_type=loading_type)
    subset_dict = {}

    for date in tqdm(point_list):
        subset = {}
        for subset_path in subset_path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)
            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count

        subset['weighted_count'] = np.nan
        for down, up in interval:
            period_val = (subset['actual_label'] >= down) & (subset['actual_label'] < up)
            val_hyper = (period_val).sum() / subset['actual_label'].count()
            subset.loc[period_val, 'weighted_count'] = hyper_start_roll_200.loc[:date].iloc[-2][f'[{down},{up})'] / val_hyper
        subset_dict[date] = subset
        th = subset[subset['actual_label'] < pct]['weighted_count'].sum() / subset['weighted_count'].sum()
        threshold_series.loc[date, 'threshold'] = subset['prediction'].quantile(th)
    threshold_series = threshold_series.reset_index()
    signal = {}
    for signal_file_name in signal_file_name_list:
        if end is None:
            signal[signal_file_name] = pd.read_pickle(signal_file_name).loc[start:]
        else:
            signal[signal_file_name] = pd.read_pickle(signal_file_name).loc[start:end]
        if len(list(signal[signal_file_name].index.levels[1])) > 242:
            signal[signal_file_name].index = signal[signal_file_name].index.swaplevel(1, 2)
    signal = pd.Panel(signal)
    signal_count = signal.count(axis=0)
    signal_sum = signal.sum(axis=0)
    signal = signal_sum / signal_count
    signal[signal_count.eq(0)] = np.nan

    # signal = signal.reset_index()
    signal = signal['prediction'].unstack()
    signal = signal.loc[start:]
    pred_ret = signal.copy()
    signal = signal.reset_index()
    signal['index'] = signal['level_0'].apply(lambda x: max(list(filter(lambda i: i < x, point_list)))).tolist()

    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['level_0', 'level_1'])
    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal > 0
    if get_subset:
        return signal, pred_ret, subset_dict
    return signal, pred_ret


def get_signal_by_val_pct_threshold_short_integration(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                      tail=None,
                                                      end=None):
    # head,tail=None,None
    # pct = 0
    # signal_file_name_list = [
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/Future_1_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/Future_1_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/Future_1_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
    # ]
    # subset_path_list = [x[:-1]+'_val_pred/' for x in signal_file_name_list]
    # start = 20170101
    # end = 20170228
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) < end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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

    def get_subset(date, path_list):
        subset = {}
        for subset_path in path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)  # .rename(columns={'future': val_tag, 0: val_tag})
            if subset[subset_path].shape[0] == 0:
                raise Exception
            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        return subset

    res_list = []
    corr = {}
    for dt in tqdm(point_list):
        # break
        val_subset = get_subset(dt, subset_path_list)
        pred_subset = get_subset(dt, signal_file_name_list)
        corr[dt] = pred_subset.corr().loc['actual_label', 'prediction']
        th = (val_subset['actual_label'] < pct).sum() / val_subset['actual_label'].count()
        pred_subset['threshold'] = val_subset['prediction'].quantile(th)
        pred_subset['signal'] = pred_subset['prediction'] < val_subset['prediction'].quantile(th)
        res_list.append(pred_subset)
    print('Corr:', pd.Series(corr).mean())
    res = pd.concat(res_list).sort_index().loc[start:end].unstack()
    # unstack_res = res[~dup_index].unstack()
    return res['signal'], res['prediction'], res['threshold'], res['actual_label']
    # return signal, pred_ret


def get_signal_by_val_pct_threshold_long_integration(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                     tail=None,
                                                     end=None, threshold_tag='actual_label'):
    print('sub', subset_path_list)
    print('sign', signal_file_name_list)
    # head,tail=None,None
    # pct = 0
    # signal_file_name_list = [
    #             '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_d_train200_test10_factor_num400/XGBV4ReversalRes_ic_d_train200_test10_factor_num400/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_t_train200_test10_factor_num400/XGBV4ReversalRes_ic_t_train200_test10_factor_num400/',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_c_train200_test10_factor_num400/XGBV4ReversalRes_ic_c_train200_test10_factor_num400/',
    #                         ]
    # subset_path_list = [x[:-1]+'_val_pred/' for x in signal_file_name_list]
    # start = 20170101
    # end = 20210531
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in signal_file_name_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in signal_file_name_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) < end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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

    def get_subset(date, path_list):
        subset = {}
        for subset_path in path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)  # .rename(columns={'future': val_tag, 0: val_tag})

            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
                subset[subset_path] = subset[subset_path].sort_index()
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        return subset

    res_list = []
    corr = {}
    corr_target = {}
    for dt in tqdm(point_list):
        # break
        val_subset = get_subset(dt, subset_path_list)
        pred_subset = get_subset(dt, signal_file_name_list)
        corr[dt] = pred_subset.corr().loc['actual_label', 'prediction']
        corr_target[dt] = pred_subset.corr().loc[threshold_tag, 'prediction']
        th = (val_subset[threshold_tag] < pct).sum() / val_subset[threshold_tag].count()
        pred_subset['threshold'] = val_subset['prediction'].quantile(th)
        pred_subset['signal'] = pred_subset['prediction'] > val_subset['prediction'].quantile(th)
        res_list.append(pred_subset)
    print('Corr:', pd.Series(corr).mean())
    print(f'Corr_{threshold_tag}:', pd.Series(corr_target).mean())
    res = pd.concat(res_list).sort_index().loc[start:end].unstack()
    return res['signal'], res['prediction'], res['threshold'], res['actual_label']


def get_signal_by_val_pct_threshold_long_integration_multi(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                           tail=None,
                                                           end=None, threshold_tag='actual_label', threads=10):
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) <= end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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

    def get_subset(date, path_list):
        subset = {}
        for subset_path in path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)  # .rename(columns={'future': val_tag, 0: val_tag})

            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        return subset

    res_list = []
    corr = {}
    corr_target = {}

    pool = Pool(threads)
    bar = tqdm(total=len(point_list) * 2)

    def update(*p):
        if bar.last_print_n < bar.total:
            bar.update()
        else:
            bar.close()

    val_subset_res = {}
    pred_ret_res = {}

    for dt in point_list:
        val_subset_res[dt] = pool.apply_async(get_subset, (dt, subset_path_list), callback=update)  # get_subset(dt,subset_path_list)
        pred_ret_res[dt] = pool.apply_async(get_subset, (dt, signal_file_name_list), callback=update)  # get_subset(dt,signal_file_name_list)
    pool.close()
    pool.join()
    for dt in point_list:
        val_subset = val_subset_res[dt].get()
        pred_subset = pred_ret_res[dt].get()
        corr[dt] = pred_subset.corr().loc['actual_label', 'prediction']
        corr_target[dt] = pred_subset.corr().loc[threshold_tag, 'prediction']
        th = (val_subset[threshold_tag] < pct).sum() / val_subset[threshold_tag].count()
        pred_subset['threshold'] = val_subset['prediction'].quantile(th)
        pred_subset['signal'] = pred_subset['prediction'] > val_subset['prediction'].quantile(th)
        res_list.append(pred_subset)
    print('Corr:', pd.Series(corr).mean())
    print(f'Corr_{threshold_tag}:', pd.Series(corr_target).mean())
    res = pd.concat(res_list).sort_index().loc[start:end]
    unstack_res = res.unstack()
    return unstack_res['signal'], unstack_res['prediction'], unstack_res['threshold'], unstack_res['actual_label']


def get_signal_by_val_pct_threshold_long_integration_rolling5_day(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False, head=None,
                                                                  tail=None,
                                                                  end=None):
    signal_file_name_list = list(map(lambda x: x.replace('.pkl', '/'), signal_file_name_list))
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in subset_path_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in subset_path_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in subset_path_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) <= end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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

    def get_subset(date, path_list):
        subset = {}
        for subset_path in path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)  # .rename(columns={'future': val_tag, 0: val_tag})
            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        return subset

    res_list = []

    for dt in tqdm(point_list):
        val_subset = get_subset(dt, subset_path_list)
        pred_subset = get_subset(dt, signal_file_name_list)

        all_pred = pd.concat([val_subset, pred_subset])
        group = (all_pred['actual_label'] < pct).groupby(level=0)

        down_count = group.sum().sort_index().rolling(5).sum()
        total_count = group.count().sort_index().rolling(5).sum()
        th = pd.DataFrame({'percentile': down_count / total_count, 'start_date': total_count.index})
        th['target_date'] = th['start_date'].shift(-1)
        th['start_date'] = th['start_date'].shift(4)
        th = th.dropna()
        pred_subset['threshold'] = np.nan
        for e_date, p_tile, s_date, t_date in th.reset_index().values.tolist():
            thre = all_pred.loc[s_date:e_date, 'prediction'].quantile(p_tile)
            pred_subset.loc[t_date, 'threshold'] = thre
            print(s_date, p_tile, e_date, t_date, thre)
        pred_subset['signal'] = pred_subset['prediction'] > pred_subset['threshold']
        res_list.append(pred_subset)
    res = pd.concat(res_list).sort_index().loc[start:end]
    unstack_res = res.unstack()
    return unstack_res['signal'], unstack_res['prediction'], unstack_res['threshold']


def generate_long_signal(pct, param_map, start, end, out_path,formate=True):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    res = {}
    for future_window in param_map:
        threshold_tag = '1_day_label'
        out_file = f'{out_path}/signal_long_{future_window}_pct_{pct}.pkl'
        if os.path.exists(out_file):
            print(out_file, 'exist')
            res[future_window] = pd.read_pickle(out_file)
        else:
            res[future_window] = get_signal_by_val_pct_threshold_long_integration(pct=pct, signal_file_name_list=param_map[future_window],
                                                                                  subset_path_list=[x[:-1] + '_val_pred/' for x in param_map[future_window]], start=start, end=end,
                                                                                  threshold_tag=threshold_tag)
            pd.to_pickle(res[future_window], out_file)
        signal, pred_ret = res[future_window][:2]
        if formate:
            res[future_window] = pred_ret[signal.fillna(False)]
    return res


def generate_short_signal(pct, param_map, start, end, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    res = {}
    for future_window in param_map:
        if future_window == 2:
            print(1)
        signal_file = f'{out_path}/signal_short_{future_window}_pct_{pct}.pkl'
        if os.path.exists(signal_file):
            print(signal_file)
            res[future_window] = pd.read_pickle(signal_file)
        else:
            res[future_window] = get_signal_by_val_pct_threshold_short_integration(pct=pct, signal_file_name_list=param_map[future_window],
                                                                                   subset_path_list=[x[:-1] + '_val_pred/' for x in param_map[future_window]], start=start, end=end)
            pd.to_pickle(res[future_window], signal_file)
        signal, pred_ret = res[future_window][:2]
        res[future_window] = pred_ret[signal.fillna(False)]
    return res


def get_signal_by_val_pct_threshold_long_integration_threshold_by_history(pct, subset_path_list, signal_file_name_list, start, val_tag=0, loading_type=None, get_subset=False,
                                                                          head=None,
                                                                          tail=None,
                                                                          end=None, threshold_tag='actual_label',val_period=200):


    val_start = get_pre_trade_date(start,val_period)
    print('sign', signal_file_name_list)
    if not head is None:
        point_set_list = [set(sorted(os.listdir(subset_path))[:head]) for subset_path in signal_file_name_list]
    elif not tail is None:
        point_set_list = [set(sorted(list(filter(lambda x: len(x) == 12, os.listdir(subset_path))))[-tail:]) for subset_path in signal_file_name_list]
    else:
        point_set_list = [set(sorted(os.listdir(subset_path))) for subset_path in signal_file_name_list]
    if not end is None:
        point_set_list = [set(filter(lambda x: int(x[:-4]) < end, list(point_set))) for point_set in point_set_list]
    tailored_set_list = []
    for point_set in point_set_list:
        point_set = sorted(list(point_set))
        befor_start = list(filter(lambda x: int(x[:-4]) < val_start, point_set))
        if befor_start:
            point_set = point_set[point_set.index(max(befor_start)):]
        tailored_set_list.append(set(point_set))
    point_set_list = tailored_set_list.copy()
    del tailored_set_list
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
    print(point_list[0],point_list[-1])
    def get_subset(date, path_list):
        subset = {}
        for subset_path in path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)  # .rename(columns={'future': val_tag, 0: val_tag})

            if len(subset[subset_path].index.levels[1]) > 242:
                subset[subset_path].index = subset[subset_path].index.swaplevel(1, 2)
                subset[subset_path] = subset[subset_path].sort_index()
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        return subset

    res_df = pd.DataFrame()
    corr_series = {}
    corr_target = {}
    for dt in tqdm(point_list):

        # val_subset = get_subset(dt, subset_path_list)
        pred_subset = get_subset(dt, signal_file_name_list)
        if pred_subset.shape[0]==0:
            continue
        corr = pred_subset.corr()
        corr[dt] = corr.loc['actual_label', 'prediction']
        corr_target[dt] = corr.loc[threshold_tag, 'prediction']
        # break
        if pred_subset.index[-1][0]<start:
            res_df = res_df.append(pred_subset.reindex(['actual_label', 'prediction','threshold','signal'],axis=1))
            continue
        val_start,val_end = get_pre_trade_date(dt,val_period-1),get_pre_trade_date(dt,1)
        val_subset = res_df.loc[val_start:val_end].copy()
        th = (val_subset[threshold_tag] < pct).sum() / val_subset[threshold_tag].count()
        pred_subset['threshold'] = val_subset['prediction'].quantile(th)
        pred_subset['signal'] = pred_subset['prediction'] > val_subset['prediction'].quantile(th)
        res_df = res_df.append(pred_subset)
    print('Corr:', pd.Series(corr_series).mean())
    print(f'Corr_{threshold_tag}:', pd.Series(corr_target).mean())
    # res = pd.concat(res_list).sort_index().loc[start:end].unstack()
    res_df = res_df.unstack().loc[start:]
    return res_df['signal'], res_df['prediction'], res_df['threshold'], res_df['actual_label']


# if __name__ == '__main__':
#     pct, subset_path_list, signal_file_name_list, start = (0.05, [
#         '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400_val_pred/',
#         '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400_val_pred/',
#         '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400_val_pred/',
#     ],
#      [
#  '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400/',
#  '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400/',
#  '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400/',
#
# ],
#      20170101)
