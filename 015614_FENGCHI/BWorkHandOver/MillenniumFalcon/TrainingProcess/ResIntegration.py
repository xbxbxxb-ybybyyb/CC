# @Time : 2021/10/18 14:47
# @Author : Zhichen Lu
# @File : ResIntegration.py

import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from dataApi.getData import get_daily_1factor


def get_start_index(file_list, start):
    head = list(filter(lambda x: x <= f'{start}.pkl', file_list))
    return file_list[len(head):]


def get_integration(base_path_list, up_threshold, down_threshold, start=None, end=None):
    res_list = [sorted(os.listdir(f'{each}res/')) for each in base_path_list]
    val_list = [sorted(os.listdir(f'{each}val/')) for each in base_path_list]
    if end:
        res_list = [list(filter(lambda x: x < f'{end}.pkl', each)) for each in res_list]
        val_list = [list(filter(lambda x: x < f'{end}.pkl', each)) for each in val_list]
    if start:
        res_list = [get_start_index(each, start) for each in res_list]
        val_list = [get_start_index(each, start) for each in val_list]

    for each in res_list:
        if each != res_list[0] or each != val_list[0]:
            raise Exception('List are not identical')

    val, res = [], []
    for each in val_list[0]:
        temp_val, temp_res = {}, {}
        for base_path in base_path_list:
            temp_res[base_path] = pd.read_pickle(f'{base_path}res/{each}')
            temp_val[base_path] = pd.read_pickle(f'{base_path}val/{each}')
        temp_res = pd.Panel(temp_res)
        temp_val = pd.Panel(temp_val)

        temp_res_count = temp_res.count(axis=0)
        temp_val_count = temp_val.count(axis=0)
        temp_label = temp_res.loc[:, :, 'actual_label'].T
        temp_label.columns = temp_label.columns.map(lambda x: x.split('/')[-2])
        temp_res = temp_res.mean(axis=0)
        temp_val = temp_val.mean(axis=0)
        temp_res[temp_res_count.eq(0)] = np.nan
        temp_val[temp_val_count.eq(0)] = np.nan

        if up_threshold < 1 and down_threshold < 1:
            up_pctile = (temp_val['actual_label'] < up_threshold).sum() / temp_val['actual_label'].count()
            down_pctile = (temp_val['actual_label'] < down_threshold).sum() / temp_val['actual_label'].count()

            temp_res['up_signal'] = temp_res['prediction'] > temp_val['prediction'].quantile(up_pctile)
            temp_res['down_signal'] = temp_res['prediction'] < temp_val['prediction'].quantile(down_pctile)
        elif up_threshold >= 1 and down_threshold >= 1:
            temp_pred_rank_tail = temp_res['prediction'].groupby(level=0).rank()
            temp_pred_rank_head = temp_res['prediction'].groupby(level=0).rank(ascending=False)
            temp_res['up_signal'] = temp_pred_rank_head < up_threshold
            temp_res['down_signal'] = temp_pred_rank_tail < down_threshold
        else:
            raise Exception('Wrong threshold')
        temp_res = pd.concat([temp_res, temp_label], axis=1)
        res.append(temp_res)
    res = pd.concat(res)
    # signal,prediction,actual_label = res['signal'].unstack().fillna(False),res['prediction'].unstack(),res['actual_label'].unstack()
    unstack_res = res.unstack()
    return {x: unstack_res[x] for x in unstack_res.columns.levels[0]}


def trans_ind2stk_signal(signal, ind_info):
    involved_stk = {}
    for date in signal.index:
        involved_ind = signal.loc[date].fillna(False)
        involved_ind = involved_ind[involved_ind]
        involved_stk[date] = ind_info.loc[date].isin(involved_ind.index)
    involved_stk = pd.DataFrame(involved_stk).T
    return involved_stk


def trans_ind2stk_val(val, ind_info):
    stk_val = {}
    for date in tqdm(val.index):
        ind_val = val.loc[date]
        stk_ind_info = ind_info.loc[date]
        temp_stk_val = pd.Series(index=stk_ind_info.index)
        for ind in ind_val.index:
            temp_stk_val.loc[stk_ind_info[stk_ind_info.eq(ind)].index] = ind_val.loc[ind]
        stk_val[date] = temp_stk_val
    return pd.DataFrame(stk_val).T


def get_head_tail_deal_pool(original_pool, up_signal_stk, down_signal_stk):
    up_signal_stk = up_signal_stk.reindex(original_pool.index, axis=0).reindex(original_pool.columns, axis=1).fillna(False)
    down_signal_stk = down_signal_stk.reindex(original_pool.index, axis=0).reindex(original_pool.columns, axis=1).fillna(False)
    pool_droptail = original_pool.copy()
    pool_droptail[down_signal_stk] = np.nan
    pool_head_first = original_pool.copy()
    pool_head_first[up_signal_stk] = pool_head_first[up_signal_stk] + 100

    pool_head_first_and_drop_tail = pool_droptail.copy()
    pool_head_first_and_drop_tail[up_signal_stk] = pool_head_first_and_drop_tail[up_signal_stk] + 100
    return pool_head_first, pool_droptail, pool_head_first_and_drop_tail


# def get

def calc_by_threshold():
    res = get_integration(base_path_list=[
        '/data/group/800442/800319/MillenniumFalcon/ExpRes_New/XGBInd_ic_d/',
        '/data/group/800442/800319/MillenniumFalcon/ExpRes_New/XGBInd_ic_c/',
        '/data/group/800442/800319/MillenniumFalcon/ExpRes_New/XGBInd_ic_dc/',
    ], start=20160101, end=20191231, up_threshold=0.03, down_threshold=-0.03)
    res.keys()
    from dataApi.getData import get_daily_1factor
    sw2_info = get_daily_1factor('SW2')  # .shift(1)
    up_signal, down_signal = [res[x] for x in ['up_signal', 'down_signal']]
    up_signal_stk = trans_ind2stk_signal(up_signal, sw2_info)
    down_signal_stk = trans_ind2stk_signal(down_signal, sw2_info)
    pd.to_pickle(up_signal_stk, f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/up_d_c_dc_3pct.pkl')
    pd.to_pickle(down_signal_stk, f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/down_d_c_dc_3pct.pkl')
    count = pd.DataFrame({'up': up_signal_stk.sum(axis=1), 'down': down_signal_stk.sum(axis=1)})
    stk_preidction = trans_ind2stk_val(res['prediction'], sw2_info)
    pd.to_pickle(stk_preidction, f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/prediction_d_c_dc.pkl')
    ind_prediction_zscore = (res['prediction'].T - res['prediction'].mean(axis=1)) / res['prediction'].std(axis=1)
    stk_prediction_zscore = trans_ind2stk_val(ind_prediction_zscore.T, sw2_info)
    pd.to_pickle(stk_prediction_zscore, f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/prediction_zscore_d_c_dc.pkl')

    original = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl')
    Up_signal_stk = pd.read_pickle(f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/up_d_c_dc_3pct.pkl')
    Down_signal_stk = pd.read_pickle(f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/down_d_c_dc_3pct.pkl')
    Zscore_prediction = pd.read_pickle('/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/prediction_zscore_d_c_dc.pkl')

    Zscore_prediction = Zscore_prediction.reindex(original.index, axis=0).reindex(original.columns, axis=1)

    pool_head_first, pool_droptail, pool_head_first_and_drop_tail = get_head_tail_deal_pool(original, Up_signal_stk, Down_signal_stk)

    pool_zscore = (original.T - original.mean(axis=1)) / original.std(axis=1)
    pool_zscore = pool_zscore.T + Zscore_prediction

    pool_head_first_zscore, pool_droptail_zscore, pool_head_first_and_drop_tail_zscore = \
        get_head_tail_deal_pool(pool_zscore, Up_signal_stk, Down_signal_stk)

    pd.to_pickle(pool_droptail, '/data/group/800442/800319/AlphaPool/pool_droptail_d_c_dc_3pct.pkl')
    pd.to_pickle(pool_head_first, '/data/group/800442/800319/AlphaPool/pool_head_first_d_c_dc_3pct.pkl')
    pd.to_pickle(pool_head_first_and_drop_tail, '/data/group/800442/800319/AlphaPool/pool_head_first_and_drop_tail_d_c_dc_3pct.pkl')
    pd.to_pickle(pool_zscore, '/data/group/800442/800319/AlphaPool/pool_zscore.pkl')

    pd.to_pickle(pool_droptail_zscore, '/data/group/800442/800319/AlphaPool/pool_droptail_zscore_d_c_dc_3pct.pkl')
    pd.to_pickle(pool_head_first_zscore, '/data/group/800442/800319/AlphaPool/pool_head_first_zscore_d_c_dc_3pct.pkl')
    pd.to_pickle(pool_head_first_and_drop_tail_zscore, '/data/group/800442/800319/AlphaPool/pool_head_first_and_drop_tail_zscore_d_c_dc_3pct.pkl')


def replace_top_tail(original_pool, ind_prediction, pool_num, replace_num):
    stock_pool = original_pool.rank(axis=1, ascending=False) < pool_num
    ind_prediction = ind_prediction.reindex(stock_pool.index, axis=0).reindex(stock_pool.columns, axis=1)
    drop = ind_prediction[stock_pool].rank(axis=1, ascending=False) < replace_num
    add = (original_pool[(~stock_pool)].rank(axis=1, ascending=False).T < drop.sum(axis=1)).T
    stock_pool[drop] = False
    stock_pool[add] = True
    # stock_pool.sum(axis=1)
    return stock_pool


def get_head_tail(head, tail, model_list):
    file_name = f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/all_integrate_res_head{head}_tail{tail}.pkl'
    if os.path.exists(file_name):
        res = pd.read_pickle(file_name)
    else:
        res = get_integration(base_path_list=model_list, start=20160101, end=20210531, up_threshold=head, down_threshold=tail)
        # res.keys()
        pd.to_pickle(res, file_name)
    sw2_info = get_daily_1factor('SW2')  # .shift(1)
    up_signal, down_signal = [res[x] for x in ['up_signal', 'down_signal']]
    up_signal_stk = trans_ind2stk_signal(up_signal, sw2_info)
    down_signal_stk = trans_ind2stk_signal(down_signal, sw2_info)
    original = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl')

    """
    pred_z_score = ((res['prediction'].T - res['prediction'].mean(axis=1))/res['prediction'].std(axis=1)).T
    pred = trans_ind2stk_val(pred_z_score,sw2_info)

    zscore_original = (original.T - original.mean(axis=1))/original.std(axis=1)

    pred_to_sum = pred.reindex(zscore_original.index,axis=0).reindex(zscore_original.columns,axis=1).fillna(0)
    sum_stk_ind_pred = zscore_original + pred_to_sum
    pd.to_pickle(sum_stk_ind_pred,'/data/group/800442/800319/AlphaPool/pool_mix_integrate_plus_origin.pkl')

    replace_pool = replace_top_tail(original,pred,600,100)
    replace_pool_200 = replace_top_tail(original,pred,600,200)
    replace_pool.to_pickle('/data/group/800442/800319/AlphaPool/pool_mix_integrate_replace100.pkl')
    replace_pool_200.to_pickle('/data/group/800442/800319/AlphaPool/pool_mix_integrate_replace200.pkl')
    pred.to_pickle('/data/group/800442/800319/AlphaPool/pool_pure_industry_mix_integration.pkl')
    """
    pool_head_first, pool_droptail, pool_head_first_and_drop_tail = get_head_tail_deal_pool(original, up_signal_stk, down_signal_stk)
    pd.to_pickle(pool_droptail, f'/data/group/800442/800319/AlphaPool/pool_droptail_mix_integrate_constant_{head}_{tail}.pkl')
    pd.to_pickle(pool_head_first, f'/data/group/800442/800319/AlphaPool/pool_head_first_mix_integrate_constant_{head}_{tail}.pkl')
    pd.to_pickle(pool_head_first_and_drop_tail, f'/data/group/800442/800319/AlphaPool/pool_head_first_and_drop_tail_mix_integrateconstant_{head}_{tail}.pkl')


if __name__ == '__main__':

    m_list = [
        'XGB_ic_d_mean_lable_group_stk_future_avg_5',
        'XGB_ic_dc_mean_lable_group_stk_future_avg_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_4',
        'XGB_ic_d_zscore_lable_group_stk_future_avg_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_avg_5',
        'XGB_ic_c_zscore_lable_group_stk_future_avg_5',
        'XGB_ic_dc_mean_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_c_mean_lable_group_stk_future_avg_5',
        'XGB_ic_dc_mean_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_c_mean_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_dc_mean_lable_group_stk_future_avg_4',
        'XGB_ic_c_zscore_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_d_mean_lable_group_stk_future_rise_pct_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_c_mean_lable_group_stk_future_avg_4',
        'XGB_ic_dc_zscore_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_avg_4',
        'XGB_ic_d_zscore_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_3',
        'XGB_ic_d_zscore_lable_group_stk_future_rise_pct_5',
        'XGB_ic_d_zscore_lable_group_stk_future_avg_4',
        'XGB_ic_d_zscore_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_c_zscore_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_c_mean_lable_group_stk_future_avg_1_2_3',
        'XGB_ic_c_mean_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_d_mean_lable_group_stk_future_rise_pct_1_3_5',
        'XGB_ic_d_mean_lable_group_stk_future_rise_pct_5',
        'XGB_ic_d_zscore_lable_group_stk_future_rise_pct_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_rise_pct_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_avg_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_rise_pct_1_3_5',
        'XGB_ic_dc_mean_lable_group_stk_future_rise_pct_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_5',
        'XGB_ic_d_zscore_lable_group_stk_future_avg_5',
        'XGB_ic_d_mean_lable_group_stk_future_rise_pct_1_3_5',
        'XGB_ic_c_zscore_lable_group_stk_future_rise_pct_5',
        'XGB_ic_c_mean_lable_group_stk_future_rise_pct_5',
        'XGB_ic_dc_mean_lable_group_stk_future_avg_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_rise_pct_1_2_3_4_5',
        'XGB_ic_dc_zscore_lable_group_stk_future_rise_pct_4',
        'XGB_ic_dc_mean_lable_group_stk_future_avg_1_2_3_4_5',
        'XGB_ic_c_mean_lable_group_stk_future_rise_pct_1',
        'XGB_ic_d_mean_lable_group_stk_future_rise_pct_1_2_3_4_5',
        'XGB_ic_dc_mean_lable_group_stk_future_rise_pct_1',
        'XGB_ic_d_mean_lable_group_stk_future_rise_pct_4',
        'XGB_ic_dc_zscore_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_1_3_5',
        'XGB_ic_c_zscore_lable_group_stk_future_avg_5',
        'XGB_ic_d_mean_lable_group_stk_future_avg_4',

    ]
    m_list = sorted(list(set(m_list)))
    len(m_list)
    m_list = [f'/data/group/800442/800319/MillenniumFalcon/ExpResPreNormalize/{x}/' for x in m_list]
    # head = 10
    # tail = 10
    # for t in [15, 20, 25, 30, 45, 50]:
    #     get_head_tail(t, t, m_list)
    # res['prediction'].corrwith(res['XGB_ic_c_mean_lable_group_stk_future_rise_pct_1'],axis=1).mean()
    pool_list = list(filter(lambda x: x.startswith('pool_'), os.listdir('/data/group/800442/800319/AlphaPool/')))
    pool_list = [x.replace('.pkl','') for x in pool_list]


    res = pd.read_pickle(f'/data/group/800442/800319/MillenniumFalcon/IndstryStockPool/all_integrate_res_head15_tail15.pkl')

    sw2_info = get_daily_1factor('SW2')  # .shift(1)
    up_signal, down_signal = [res[x] for x in ['up_signal', 'down_signal']]
    up_signal_stk = trans_ind2stk_signal(up_signal, sw2_info)
    down_signal_stk = trans_ind2stk_signal(down_signal, sw2_info)
    original = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl')


    # pred_z_score = ((res['prediction'].T - res['prediction'].mean(axis=1))/res['prediction'].std(axis=1)).T
    pred = trans_ind2stk_val(res['prediction'],sw2_info)
    pred = ((pred.T - pred.mean(axis=1))/pred.std(axis=1)).T

    zscore_original = (original.T - original.mean(axis=1))/original.std(axis=1)

    pred_to_sum = pred.reindex(zscore_original.index,axis=0).reindex(zscore_original.columns,axis=1).fillna(0)
    sum_stk_ind_pred = zscore_original + pred_to_sum
    pd.to_pickle(sum_stk_ind_pred,'/data/group/800442/800319/AlphaPool/pool_mix_integrate_plus_origin_ZSCOREAFTERFLATTEN.pkl')
    pred.to_pickle('/data/group/800442/800319/AlphaPool/pool_pure_industry_mix_integration_ZSCOREAFTERFLATTEN.pkl')
