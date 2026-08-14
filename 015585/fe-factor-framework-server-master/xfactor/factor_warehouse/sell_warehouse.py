# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from h5data.IO import IO
import settings
import warnings
from xfactor.FactorUtil import check_xdb_tick_1s_full
from loguru import logger

warnings.filterwarnings('ignore')


def summary_inf(in_pkl, out_pkl):
    res = {'in_score': in_pkl['check_score_res'].values[-1][-1],
           'out_score': out_pkl['check_score_res'].values[-1][-1],
           'in_IC_tot': in_pkl['corr_sta']['value']['corr_tot'],
           'in_IC_mean_std': in_pkl['corr_sta']['value']['corr_month_mean_std'],
           'out_IC_tot': out_pkl['corr_sta']['value']['corr_tot'],
           'out_IC_mean_std': out_pkl['corr_sta']['value']['corr_month_mean_std'],
           'Mutual_Info': out_pkl['corr_sta']['value']['mic_tot']}
    res['tot_score'] = res['in_score'] + res['out_score']
    linear_test = (res['tot_score'] > 25) & (res['out_score'] / res['in_score'] > 0.6)
    res['bank_type'] = 'linear' if linear_test else 'nonlinear'
    return res


def sell_warehouse():
    key = settings.sell_key
    scene = settings.sell_scene
    s_xx = settings.sell_s_xx
    in_interval = settings.warehouse_settings_dict["sell"]["in_interval"]
    out_interval = settings.warehouse_settings_dict["sell"]["out_interval"]
    max_corr = settings.warehouse_settings_dict["sell"]["max_corr"]
    res_path = settings.warehouse_settings_dict["sell"]["res_path"]
    sft_basic_path = settings.warehouse_settings_dict["sell"]["sft_basic_path"]
    basic_factor_path = settings.warehouse_settings_dict["sell"]["basic_factor_path"]
    factor_data_path = settings.path_dict["sell"]["factor_value_path"]
    pre_check_path = settings.path_dict["sell"]["factor_precheck_path"]
    factor_test_path = settings.path_dict["sell"]["factor_test_path"]

    test_factor_inf = pd.read_excel(settings.warehouse_settings_dict["sell"]["all_factors_list"])
    test_factor_inf = test_factor_inf[test_factor_inf['factor_type'] != 'other']
    test_factor_inf = test_factor_inf[~test_factor_inf['factor_type'].isin(
        ['TTransaction_cs', 'T1mTransaction_cs', 'TOrder', 'TOrder_cs', 'T1mOrder_cs', 'T1mOrder'])]
    check_res_cols = ['factor_name', 'pre_check', 'in_score', 'out_score', 'in_IC_tot', 'in_IC_mean_std', 'out_IC_tot',
                      'out_IC_mean_std', 'Mutual_Info', 'tot_score', 'bank_type', '入库情况', '入库时间', '出库时间']
    test_date_list = list(test_factor_inf['提交时间'].unique())
    test_date_list.sort()

    last_test_date = test_date_list[-2]  ##如果是None，则是从头开始；如果是test_date_list[-2]，则是从上一日期开始
    start_index = 0 if last_test_date is None else test_date_list.index(last_test_date) + 1

    for test_date in test_date_list[start_index:]:
        logger.info("-" * 20 + "sell warehouse: test_date={}".format(test_date) + "-" * 20)

        if last_test_date is None:
            start_index = 0
            all_factor_df = pd.DataFrame(
                index=IO.read_data([in_interval[0], out_interval[1]], alt=sft_basic_path).index)
            check_res_inf = pd.DataFrame(columns=check_res_cols)
        else:
            start_index = test_date_list.index(last_test_date)
            all_factor_df = pd.read_pickle(res_path + 'all_factor_df/all_factor_df_{}.pkl'.format(last_test_date))
            check_res_inf = pd.read_excel(res_path + 'check_res/check_res_tot_sell_{}.xlsx'.format(last_test_date))[
                check_res_cols]

        day_factor_inf = test_factor_inf[test_factor_inf['提交时间'] == test_date].copy()
        # day_check_res = [] #series with index ['pre_check']
        for index, inf in day_factor_inf.iterrows():
            factor_name, factor_type, factor_owner = inf['factor_name'], inf['factor_type'], inf['factor_owner']

            start_date_new = in_interval[0]
            if "[" in factor_type and "]" in factor_type:
                if 'Tickfull' in factor_type or 'Tick1s' in factor_type or "Cancel" in factor_type:
                    start_date_new = 20170101
                if  "xdb_tickfull" in factor_type or "xdb_tick1s" in factor_type \
                        or "xdb_tickfulladdorder" in factor_type or "xdb_cancel" in factor_type:
                    start_date_new = 20170110

            pre_check = pd.read_pickle('{}/{}.pkl'.format(pre_check_path, factor_name))
            if '预检测' in pre_check.index:
                pre_check['check_inf'] = 'pass' if pre_check['预检测'] == 'pass' else pre_check.astype(
                    'str').sum().replace(
                    'not pass', '').replace('pass', '')
            elif 'pass' in pre_check.index:
                pre_check['check_inf'] = 'pass' if pre_check['pass'] is True else pre_check.astype(
                    'str').sum().replace(
                    'not pass', '').replace('pass', '')
            else:
                logger.error("入库失败！预检测结果格式异常！factor_name={}, strategy=sell".format(factor_name))
                continue

            factor_res = {'factor_name': factor_name, 'pre_check': pre_check['check_inf']}
            if factor_res['pre_check'] != 'pass':
                check_res_inf = check_res_inf.append(pd.DataFrame(factor_res.values(), index=factor_res.keys()).T)[
                    check_res_cols]
                logger.warning(factor_res)
                continue
            in_pkl = pd.read_pickle('{}/{}_{}/{}.pkl'.format(factor_test_path, start_date_new, in_interval[1], factor_name))
            out_pkl = pd.read_pickle(
                '{}/{}_{}/{}.pkl'.format(factor_test_path, out_interval[0], out_interval[1], factor_name))

            if factor_owner != 'other_basic':
                test_factor_df = IO.read_data([start_date_new, out_interval[1]],
                                              alt='{}/{}/{}.h5'.format(factor_data_path, factor_name, factor_name))
            else:
                if factor_name == 'lzt_day_pattern':
                    test_factor_df = pd.read_hdf(basic_factor_path)[['lzt_label_pattern']]
                    test_factor_df.columns = ['lzt_day_pattern']
                else:
                    test_factor_df = pd.read_hdf(basic_factor_path)[[factor_name]]
            if factor_type == 'other_basic':
                test_factor_df = IO.read_data([start_date_new, out_interval[1]], alt=sft_basic_path)[factor_name]

            test_factor_df = test_factor_df.reindex(all_factor_df.index)
            # corr_factor_ser = all_factor_df.corrwith(test_factor_df[factor_name], method='spearman').abs()
            corr_factor_ser = all_factor_df.rank().corrwith(test_factor_df[factor_name].rank()).abs()
            high_corr_factor_list = list(corr_factor_ser[corr_factor_ser > max_corr].index) if len(
                all_factor_df.columns) > 0 else []
            factor_res = {**factor_res, **summary_inf(in_pkl, out_pkl)}
            # ---------------------------------------------------------------------------------------------------------------
            if factor_res['bank_type'] != 'linear':
                # 入库门槛
                factor_res['入库情况'] = '入库失败-未达到入库阈值'

            else:
                if len(high_corr_factor_list) == 0:
                    # 因子库内没有高相关
                    factor_res['入库情况'] = '入库成功-没有高相关'
                else:
                    # 因子库内存在高相关因子
                    corr_factor_bank_type = 'linear' if 'linear' in list(
                        check_res_inf[check_res_inf['factor_name'].apply(lambda x: x in high_corr_factor_list)][
                            'bank_type']) else 'nonlinear'
                    if (factor_res['bank_type'] == 'linear') and (corr_factor_bank_type == 'nonlinear'):
                        # 挤出高相关因子
                        factor_res['入库情况'] = '入库成功-挤出高相关非线性因子{}'.format(high_corr_factor_list)
                    elif (factor_res['bank_type'] == 'nonlinear') and (corr_factor_bank_type == 'linear'):
                        # 新因子未非线性，无法入库
                        factor_res['入库情况'] = '入库失败-存在高相关线性因子{}'.format(high_corr_factor_list)
                    elif (factor_res['bank_type'] == 'linear') and (corr_factor_bank_type == 'linear'):
                        # 都为线性，比较得分
                        corr_max_tot_score = \
                            check_res_inf[check_res_inf['factor_name'].apply(lambda x: x in high_corr_factor_list)][
                                'tot_score'].max()
                        if factor_res['tot_score'] - corr_max_tot_score >= 5:
                            factor_res['入库情况'] = '入库成功-挤出线性高相关因子{}'.format(high_corr_factor_list)
                        else:
                            factor_res['入库情况'] = '入库失败-存在得分更高的线性高相关因子{}'.format(high_corr_factor_list)

                    elif (factor_res['bank_type'] == 'nonlinear') and (corr_factor_bank_type == 'nonlinear'):
                        # 都为非线性，比较互信息
                        corr_max_mic = \
                            check_res_inf[check_res_inf['factor_name'].apply(lambda x: x in high_corr_factor_list)][
                                'Mutual_Info'].max()
                        if (factor_res['Mutual_Info'] / corr_max_mic - 1 > 0.05):
                            factor_res['入库情况'] = '入库成功-挤出非线性高相关因子{}'.format(high_corr_factor_list)
                        else:
                            factor_res['入库情况'] = '入库失败-存在互信息更高的非线性高相关因子{}'.format(high_corr_factor_list)

            factor_res['入库时间'] = test_date if factor_res['入库情况'][:4] == '入库成功' else np.nan
            factor_res['出库时间'] = np.nan
            # ---------------------------------------------------------------------------------------------------------------
            check_res_inf = check_res_inf.append(pd.DataFrame(factor_res.values(), index=factor_res.keys()).T)
            if (np.isnan(factor_res['入库时间']) == False):
                all_factor_df[factor_name] = test_factor_df[factor_name]
                if (len(high_corr_factor_list) > 0):
                    check_res_inf.loc[
                        check_res_inf['factor_name'].apply(lambda x: x in high_corr_factor_list), '出库时间'] = test_date
                    all_factor_df = all_factor_df.drop(high_corr_factor_list, axis=1)
            logger.info(factor_res)

        all_factor_df.to_pickle(res_path + 'all_factor_df/all_factor_df_{}.pkl'.format(test_date))
        check_res_inf_ = test_factor_inf.join(check_res_inf.set_index('factor_name'), on='factor_name')
        check_res_inf_ = check_res_inf_[check_res_inf_['提交时间'] <= test_date].drop(columns=['因子逻辑'])
        check_res_inf_.to_excel(res_path + 'check_res/check_res_tot_sell_{}.xlsx'.format(test_date))
        last_test_date = test_date

        basic_df = IO.read_data([in_interval[0], out_interval[1]], alt=sft_basic_path)
        same_col = [col for col in basic_df.columns if col in all_factor_df.columns]
        basic_df = basic_df.drop(columns=same_col)
        update_file = res_path + 'sft_update_normal{}_filter.h5'.formats_xx
        if not os.path.exists(update_file):
            IO.pd_hdf5_writer(basic_df.join(all_factor_df), update_file, dataset='data')
        else:
            IO.pd_hdf5_writer(basic_df.join(all_factor_df), update_file, dataset='data', override=True)

        update_file_public = update_file.replace('/931/', '/931_public/').replace('filter.h5', 'filter_{}_{}.h5'.format(
            in_interval[0], in_interval[1]))
        if not os.path.exists(update_file_public):
            IO.pd_hdf5_writer(basic_df.join(all_factor_df).loc[:pd.to_datetime(str(in_interval[1]))],
                              update_file_public, dataset='data')
        else:
            IO.pd_hdf5_writer(basic_df.join(all_factor_df).loc[:pd.to_datetime(str(in_interval[1]))],
                              update_file_public, dataset='data', override=True)
