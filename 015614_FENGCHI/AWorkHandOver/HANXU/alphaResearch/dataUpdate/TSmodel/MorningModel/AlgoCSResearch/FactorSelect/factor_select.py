import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import numpy as np
import pandas as pd

from TSmodel.MorningModel.PreprocessFactor import get_morning_factor_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from dataApi.sendInfo import send_file


def load_test_result(name, start_date, end_date, item_ids, item_num=64, dtype='float64', file_offset=0,
                     address='/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/cs_test/'):
    ft_date_list = get_date_range(get_pre_trade_date(20140801, - file_offset), 20991231)
    start_idx = ft_date_list.index(start_date)
    end_idx = ft_date_list.index(end_date) + 1
    fp = np.memmap(f'{address}/{name}.npy', dtype=dtype, mode='r',
                   offset=128 + start_idx * item_num * int(dtype[-2:]) // 8,
                   shape=(end_idx - start_idx, item_num))
    arr = fp[:, item_ids].__array__()
    del fp
    return arr


def corr_filter(limit, sample, metrics, ignore_sign=True):
    metrics = np.array(metrics)
    sample = np.corrcoef(sample)
    sample[~ np.isfinite(sample)] = 1
    if ignore_sign:
        sample = np.abs(sample)
    rank = (- metrics).argsort(axis=-1)
    corr = sample[rank[:, None], rank[None, :]]
    corr_triu = np.tril_indices(corr.shape[0])
    corr[corr_triu] = 0.
    corr_pool = corr.max(axis=0) < limit
    _corr_pool_num1 = 0
    _corr_pool_num2 = corr_pool.sum()
    while _corr_pool_num2 > _corr_pool_num1:
        _corr_pool_num1 = _corr_pool_num2
        corr[corr[corr_pool].max(axis=0) >= limit] = 0
        corr_pool = corr.max(axis=0) < limit
        _corr_pool_num2 = corr_pool.sum()
    return rank[corr_pool]


def factor_method_filter(factor_list, metrics):
    factor_list = [x.split('_', 1) for x in factor_list]
    df = pd.DataFrame({'metrics': metrics})
    df.index = pd.MultiIndex.from_tuples(factor_list)
    df.index.names = ['method', 'name']
    df = df.reset_index().sort_values(['name', 'metrics']).drop_duplicates(['name'], keep='last')
    return df.index.to_list()


def ic_select(factor_list, start_date, end_date):
    IC_mean = np.empty(len(factor_list))
    IC_t = np.empty(len(factor_list))
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    for j, name in enumerate(factor_list):
        arr = load_test_result(name, start_date, end_date, [20, 44, 53])
        ic_mean = np.nanmean(arr[:, 0])
        ic_std = np.nanstd(arr[:, 0], ddof=1)
        ic_num = np.isfinite(arr[:, 0]).sum()
        ic_t = ic_mean / ic_std * ic_num ** 0.5
        se = arr[:, 1] if ic_mean < 0 else arr[:, 2]
        IC_mean[j] = ic_mean
        IC_t[j] = ic_t
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    IC_mean = np.abs(IC_mean)
    IC_t = np.abs(IC_t)
    return IC_t, IC_mean, SE


def rank_ic_select(factor_list, start_date, end_date):
    IC_mean = np.empty(len(factor_list))
    IC_t = np.empty(len(factor_list))
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    for j, name in enumerate(factor_list):
        arr = load_test_result(name, start_date, end_date, [21, 44, 53])
        ic_mean = np.nanmean(arr[:, 0])
        ic_std = np.nanstd(arr[:, 0], ddof=1)
        ic_num = np.isfinite(arr[:, 0]).sum()
        ic_t = ic_mean / ic_std * ic_num ** 0.5
        se = arr[:, 1] if ic_mean < 0 else arr[:, 2]
        IC_mean[j] = ic_mean
        IC_t[j] = ic_t
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    IC_mean = np.abs(IC_mean)
    IC_t = np.abs(IC_t)
    return IC_t, IC_mean, SE


def group_ic_select(factor_list, start_date, end_date):
    IC_mean = np.empty(len(factor_list))
    IC_t = np.empty(len(factor_list))
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    for j, name in enumerate(factor_list):
        arr = load_test_result(name, start_date, end_date, [22, 44, 53])
        ic_mean = np.nanmean(arr[:, 0])
        ic_std = np.nanstd(arr[:, 0], ddof=1)
        ic_num = np.isfinite(arr[:, 0]).sum()
        ic_t = ic_mean / ic_std * ic_num ** 0.5
        se = arr[:, 1] if ic_mean < 0 else arr[:, 2]
        IC_mean[j] = ic_mean
        IC_t[j] = ic_t
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    IC_mean = np.abs(IC_mean)
    IC_t = np.abs(IC_t)
    return IC_t, IC_mean, SE


def group_dist_select(factor_list, start_date, end_date):
    Dist_mean = np.empty(len(factor_list))
    Dist_t = np.empty(len(factor_list))
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    for j, name in enumerate(factor_list):
        arr = load_test_result(name, start_date, end_date, [20, 23, 24, 44, 53])
        ic_mean = np.nanmean(arr[:, 0])
        se = arr[:, 3] if ic_mean < 0 else arr[:, 4]
        dist = arr[:, 1] if ic_mean > 0 else arr[:, 2]
        dist_mean = np.nanmean(dist)
        dist_std = np.nanstd(dist, ddof=1)
        dist_num = np.isfinite(dist).sum()
        dist_t = dist_mean / dist_std * dist_num ** 0.5
        Dist_mean[j] = dist_mean
        Dist_t[j] = dist_t
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    Dist_mean = - Dist_mean
    return Dist_mean, Dist_t, SE


def gross_ret_select(factor_list, start_date, end_date):
    Ret_mean = np.empty(len(factor_list))
    Ret_t = np.empty(len(factor_list))
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    for j, name in enumerate(factor_list):
        arr = load_test_result(name, start_date, end_date, [20, 44, 53])
        ic_mean = np.nanmean(arr[:, 0])
        se = arr[:, 1] if ic_mean < 0 else arr[:, 2]
        ret_mean = np.nanmean(se)
        ret_std = np.nanstd(se, ddof=1)
        ret_t = ret_mean / ret_std * 244 ** 0.5
        SE[j] = se
        Ret_mean[j] = ret_mean
        Ret_t[j] = ret_t
    SE[~ np.isfinite(SE)] = 0
    return Ret_t, Ret_mean, SE


def net_ret_select(factor_list, start_date, end_date, fee=0.002):
    Ret_mean = np.empty(len(factor_list))
    Ret_t = np.empty(len(factor_list))
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    for j, name in enumerate(factor_list):
        arr = load_test_result(name, start_date, end_date, [20, 44, 53, 54, 63])
        ic_mean = np.nanmean(arr[:, 0])
        se = arr[:, 1] if ic_mean < 0 else arr[:, 2]
        turn = arr[:, 3] if ic_mean < 0 else arr[:, 4]
        ret = se - turn * fee
        ret_mean = np.nanmean(ret)
        ret_std = np.nanstd(ret, ddof=1)
        ret_t = ret_mean / ret_std * 244 ** 0.5
        SE[j] = se
        Ret_mean[j] = ret_mean
        Ret_t[j] = ret_t
    SE[~ np.isfinite(SE)] = 0
    return Ret_t, Ret_mean, SE


def ts_ic_mean_select(factor_list, start_date, end_date):
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    IC_mean = np.empty(len(factor_list))
    month_list = [x // 100 for x in get_date_range(20140801, 20991231, 'M')]
    start_month = start_date // 100
    end_month = get_recent_trade_date(end_date, 'M') // 100
    start_month_idx = month_list.index(start_month)
    end_month_idx = month_list.index(end_month) + 1
    for j, name in enumerate(factor_list):
        dic = pd.read_pickle(f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')
        arr = load_test_result(name, start_date, end_date, [44, 53])
        ic_mean = dic['ic_month_d_mean'][start_month_idx: end_month_idx]
        ic_mean = np.nanmean(ic_mean)
        se = arr[:, 0] if ic_mean < 0 else arr[:, 1]
        IC_mean[j] = ic_mean
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    IC_mean = np.abs(IC_mean)
    return IC_mean, SE


def ts_ic_t_select(factor_list, start_date, end_date):
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    IC_mean = np.empty(len(factor_list))
    month_list = [x // 100 for x in get_date_range(20140801, 20991231, 'M')]
    start_month = start_date // 100
    end_month = get_recent_trade_date(end_date, 'M') // 100
    start_month_idx = month_list.index(start_month)
    end_month_idx = month_list.index(end_month) + 1
    for j, name in enumerate(factor_list):
        dic = pd.read_pickle(f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')
        arr = load_test_result(name, start_date, end_date, [44, 53])
        ic_mean = dic['ic_month_d_t'][start_month_idx: end_month_idx]
        ic_mean = np.nanmean(ic_mean)
        se = arr[:, 0] if ic_mean < 0 else arr[:, 1]
        IC_mean[j] = ic_mean
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    IC_mean = np.abs(IC_mean)
    return IC_mean, SE


def ts_ic_pos_select(factor_list, start_date, end_date):
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    IC_mean = np.empty(len(factor_list))
    month_list = [x // 100 for x in get_date_range(20140801, 20991231, 'M')]
    start_month = start_date // 100
    end_month = get_recent_trade_date(end_date, 'M') // 100
    start_month_idx = month_list.index(start_month)
    end_month_idx = month_list.index(end_month) + 1
    for j, name in enumerate(factor_list):
        dic = pd.read_pickle(f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')
        arr = load_test_result(name, start_date, end_date, [44, 53])
        ic_mean = dic['ic_month_d_mean'][start_month_idx: end_month_idx]
        ic_pos = dic['ic_month_d_pos'][start_month_idx: end_month_idx]
        ic_mean = np.nanmean(ic_mean)
        ic_pos = np.nanmean(ic_pos)
        ic_pos = ic_pos if ic_mean > 0 else 1 - ic_pos
        se = arr[:, 0] if ic_mean < 0 else arr[:, 1]
        IC_mean[j] = ic_pos
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    return IC_mean, SE


def ts_ret_mean_select(factor_list, start_date, end_date):
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    IC_mean = np.empty(len(factor_list))
    month_list = [x // 100 for x in get_date_range(20140801, 20991231, 'M')]
    start_month = start_date // 100
    end_month = get_recent_trade_date(end_date, 'M') // 100
    start_month_idx = month_list.index(start_month)
    end_month_idx = month_list.index(end_month) + 1
    for j, name in enumerate(factor_list):
        dic = pd.read_pickle(f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')
        arr = load_test_result(name, start_date, end_date, [44, 53])
        ic_mean = dic['ic_month_d_mean'][start_month_idx: end_month_idx]
        ret_mean = dic['ret_month'][start_month_idx: end_month_idx]
        ic_mean = np.nanmean(ic_mean)
        ret_mean = np.nanmean(ret_mean)
        se = arr[:, 0] if ic_mean < 0 else arr[:, 1]
        IC_mean[j] = ret_mean
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    return IC_mean, SE


def ts_ret_t_select(factor_list, start_date, end_date):
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    IC_mean = np.empty(len(factor_list))
    month_list = [x // 100 for x in get_date_range(20140801, 20991231, 'M')]
    start_month = start_date // 100
    end_month = get_recent_trade_date(end_date, 'M') // 100
    start_month_idx = month_list.index(start_month)
    end_month_idx = month_list.index(end_month) + 1
    for j, name in enumerate(factor_list):
        dic = pd.read_pickle(f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')
        arr = load_test_result(name, start_date, end_date, [44, 53])
        ic_mean = dic['ic_month_d_mean'][start_month_idx: end_month_idx]
        ret_mean = dic['ret_t_month'][start_month_idx: end_month_idx]
        ic_mean = np.nanmean(ic_mean)
        ret_mean = np.nanmean(ret_mean)
        se = arr[:, 0] if ic_mean < 0 else arr[:, 1]
        IC_mean[j] = ret_mean
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    return IC_mean, SE


def ts_ret_pos_select(factor_list, start_date, end_date):
    SE = np.empty((len(factor_list), len(get_date_range(start_date, end_date))))
    IC_mean = np.empty(len(factor_list))
    month_list = [x // 100 for x in get_date_range(20140801, 20991231, 'M')]
    start_month = start_date // 100
    end_month = get_recent_trade_date(end_date, 'M') // 100
    start_month_idx = month_list.index(start_month)
    end_month_idx = month_list.index(end_month) + 1
    for j, name in enumerate(factor_list):
        dic = pd.read_pickle(f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')
        arr = load_test_result(name, start_date, end_date, [44, 53])
        ic_mean = dic['ic_month_d_mean'][start_month_idx: end_month_idx]
        ret_mean = dic['ret_pos_month'][start_month_idx: end_month_idx]
        ic_mean = np.nanmean(ic_mean)
        ret_mean = np.nanmean(ret_mean)
        se = arr[:, 0] if ic_mean < 0 else arr[:, 1]
        IC_mean[j] = ret_mean
        SE[j] = se
    SE[~ np.isfinite(SE)] = 0
    return IC_mean, SE


SELECT_METHODS = {
    'ic_select': ic_select,
    'rank_ic_select': rank_ic_select,
    'group_ic_select': group_ic_select,
    'group_dist_select': group_dist_select,
    'gross_ret_select': gross_ret_select,
    'net_ret_select': net_ret_select,
    'ts_ic_mean_select': ts_ic_mean_select,
    'ts_ic_t_select': ts_ic_t_select,
    'ts_ic_pos_select': ts_ic_pos_select,
    'ts_ret_mean_select': ts_ret_mean_select,
    'ts_ret_t_select': ts_ret_t_select,
    'ts_ret_pos_select': ts_ret_pos_select,
}


def done_select(start_date, end_date, expanding, factor_std_methods,
                select_method, select_num, corr_limit, method_filter):
    factor_std_methods = [factor_std_methods] if isinstance(factor_std_methods, str) else factor_std_methods
    factor_list = [f'{y}_{x}' for x in get_morning_factor_list(False) for y in factor_std_methods if len(x) > 0]
    _ = SELECT_METHODS[select_method](factor_list, 20140801 if expanding else start_date, end_date)
    metrics, series = _[0], _[-1]
    if method_filter:
        choose = factor_method_filter(factor_list, metrics)
        metrics = metrics[choose]
        series = series[choose]
        factor_list = np.asanyarray(factor_list)[choose].tolist()
    if corr_limit < 1:
        choose = corr_filter(corr_limit, series, metrics, ignore_sign=False)
        metrics = metrics[choose]
        factor_list = np.asanyarray(factor_list)[choose].tolist()
    df = pd.Series(metrics, index=factor_list).sort_values(ascending=False).head(select_num)
    return df.index.to_list()


if __name__ == '__main__':
    factor_list = get_morning_factor_list()
    result = np.empty((len(factor_list), 20))
    for j, name in enumerate(factor_list):
        name = 'WCN_' + name
        cs = load_test_result(name, 20140801, 20211029, [20, 21, 22, 23, 24, 44, 53, 54, 63])
        ic_mean = np.nanmean(cs[:, 0])
        ic_std = np.nanstd(cs[:, 0], ddof=1)
        ic_ir = ic_mean / ic_std
        ic_pos = (cs[:, 0] * ic_mean > 0).sum() / np.isfinite(cs[:, 0]).sum()
        rank_ic_mean = np.nanmean(cs[:, 1])
        rank_ic_std = np.nanstd(cs[:, 1], ddof=1)
        rank_ic_ir = rank_ic_mean / rank_ic_std
        group_ic_mean = np.nanmean(cs[:, 2])
        group_dist_mean = np.nanmean(cs[:, 3]) if ic_mean > 0 else np.nanmean(cs[:, 4])
        gross_ret = cs[:, 6] if ic_mean > 0 else cs[:, 5]
        pn_ret = ((ic_mean > 0) * 2 - 1) * (cs[:, 6] - cs[:, 5])
        gross_ret_mean = np.nanmean(gross_ret)
        gross_ret_sp = gross_ret_mean / np.nanstd(gross_ret, ddof=1)
        gross_ret_pos = (gross_ret > 0).sum() / np.isfinite(gross_ret).sum()
        pn_ret_mean = np.nanmean(pn_ret)
        pn_ret_sp = pn_ret_mean / np.nanstd(pn_ret, ddof=1)
        pn_ret_pos = (pn_ret > 0).sum() / np.isfinite(pn_ret).sum()
        turn = np.nanmean(cs[:, -1]) if ic_mean > 0 else np.nanmean(cs[:, -2])
        ts = pd.read_pickle(f'/arch1/user/015836/DailyFactorResearch/ts_test/{name}.pkl')
        ts_ic = ts['ic_month_d_mean']
        ts_ic_mean = np.nanmean(ts_ic)
        ts_ic_ir = np.nanmean(ts_ic) / np.nanstd(ts_ic, ddof=1)
        ts_ic_pos = np.nanmean(ts['ic_month_d_pos'])
        ts_ic_pos = ts_ic_pos if ts_ic_mean > 0 else 1 - ts_ic_pos
        ts_ret = ts['ret_month']
        ts_ret_mean = np.nanmean(ts_ret)
        ts_ret_ir = ts_ret_mean / np.nanstd(ts_ret, ddof=1)
        ts_ret_pos = np.nanmean(ts['ret_pos_month'])
        result[j] = [ic_mean, ic_ir, ic_pos, rank_ic_mean, rank_ic_ir, group_ic_mean, group_dist_mean,
                     gross_ret_mean, gross_ret_sp, gross_ret_pos, pn_ret_mean, pn_ret_sp, pn_ret_pos,
                     turn, ts_ic_mean, ts_ic_ir, ts_ic_pos, ts_ret_mean, ts_ret_ir, ts_ret_pos]
    result = pd.DataFrame(result, index=factor_list, columns=[
        'ic_mean', 'ic_ir', 'ic_pos', 'rank_ic_mean', 'rank_ic_ir', 'group_ic_mean', 'group_dist_mean',
        'gross_ret_mean', 'gross_ret_sp', 'gross_ret_pos', 'pn_ret_mean', 'pn_ret_sp', 'pn_ret_pos',
        'turn', 'ts_ic_mean', 'ts_ic_ir', 'ts_ic_pos', 'ts_ret_mean', 'ts_ret_ir', 'ts_ret_pos'])
    result.to_excel(f'/arch1/user/015836/DailyFactorResearch/WCN_test_202110.xlsx')
    send_file('015836', f'/arch1/user/015836/DailyFactorResearch/WCN_test_202110.xlsx')

    df = pd.read_excel(f'/arch1/user/015836/DailyFactorResearch/WCN_test_202110.xlsx', index_col=0)
    des = df['ic_mean'].abs().describe(percentiles=[0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])

    corr = np.empty((len(factor_list), 1763))
    for j, name in enumerate(factor_list):
        name = 'WCN_' + name
        cs = load_test_result(name, 20140801, 20211029, [20, 44, 53])
        corr[j] = cs[:, 2] if np.nanmean(cs[:, 0]) > 0 else cs[:, 1]
    corr[~ np.isfinite(corr)] = 0
    corr = np.corrcoef(corr)

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=300, random_state=0).fit(corr)
    print(kmeans.labels_)

    kkk = corr[(kmeans.labels_ == 299)][:, (kmeans.labels_ == 299)]
    df.insert(0, 'group', kmeans.labels_)
    df['ic_ir'] = df['ic_ir'].abs()
    df.to_excel(f'/arch1/user/015836/DailyFactorResearch/WCN_test_202110.xlsx')
    send_file('015836', f'/arch1/user/015836/DailyFactorResearch/WCN_test_202110.xlsx')