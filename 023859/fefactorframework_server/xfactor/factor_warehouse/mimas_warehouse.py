# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import settings
from h5data.IO import IO
from loguru import logger
from xfactor.FactorUtil import check_xdb_tick_1s_full
import warnings

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


def mimas_warehouse():
    s_xx = settings.mimas_s_xx
    in_interval = settings.warehouse_settings_dict["mimas"]["in_interval"]
    out_interval = settings.warehouse_settings_dict["mimas"]["out_interval"]
    max_corr = settings.warehouse_settings_dict["mimas"]["max_corr"]
    factor_data_path = settings.path_dict["mimas"]["factor_value_path"]
    pre_check_path = settings.path_dict["mimas"]["factor_precheck_path"]
    factor_test_path = settings.path_dict["mimas"]["factor_test_path"]
    res_path = settings.warehouse_settings_dict["mimas"]["res_path"]
    res_public_path = settings.warehouse_settings_dict["mimas"]["res_public_path"]
    sft_basic_path = settings.warehouse_settings_dict["mimas"]["sft_basic_path"]  # 初始地址
    all_factor_saturn = pd.read_pickle(settings.warehouse_settings_dict["mimas"]["all_factor_for_left"]).loc[
                        pd.Timestamp(str(in_interval[0])):pd.Timestamp(str(out_interval[1]))]

    # 读取因子列表
    test_factor_inf = pd.read_excel(settings.warehouse_settings_dict["mimas"]["all_factors_list"])
    other_basic_list = list(
        test_factor_inf[test_factor_inf['factor_owner'].isin(['other_basic'])]['factor_name'].values)
    test_factor_inf = test_factor_inf[~(test_factor_inf['factor_owner'].isin(['other_basic']))]
    # test_factor_inf= test_factor_inf[~test_factor_inf['factor_type'].isin(['TTransaction_cs', 'T1mTransaction_cs', 'TOrder', 'TOrder_cs', 'T1mOrder_cs', 'T1mOrder'])]

    check_res_cols = ['factor_name', 'pre_check', 'in_score', 'out_score', 'in_IC_tot', 'in_IC_mean_std', 'out_IC_tot',
                      'out_IC_mean_std', 'Mutual_Info', 'tot_score', 'bank_type', '入库情况', '入库时间', '出库时间']
    test_date_list = list(test_factor_inf['提交时间'].unique())
    test_date_list.sort()

    last_test_date = test_date_list[-2]  # 如果是None，则是从头开始；如果是test_date_list[-2]，则是从上一日期开始
    start_index = 0 if last_test_date is None else test_date_list.index(last_test_date) + 1

    for test_date in test_date_list[start_index:]:
        logger.info("-" * 20 + "mimas warehouse: test_date={}".format(test_date) + "-" * 20)
        if last_test_date is None:
            start_index = 0
            all_factor_df = IO.read_data([in_interval[0], out_interval[1]], alt=sft_basic_path)
            check_res_inf = pd.DataFrame(columns=check_res_cols)
        else:
            start_index = test_date_list.index(last_test_date)
            all_factor_df = pd.read_pickle(res_path + 'all_factor_df/all_factor_df_{}.pkl'.format(last_test_date))
            check_res_inf = \
            pd.read_excel(res_path + 'check_res/check_res_tot_saturnnext_{}.xlsx'.format(last_test_date))[
                check_res_cols]

        day_factor_inf = test_factor_inf[test_factor_inf['提交时间'] == test_date].copy()
        for index, inf in day_factor_inf.iterrows():
            factor_name, factor_type, factor_owner = inf['factor_name'], inf['factor_type'], inf['factor_owner']

            start_date_new = in_interval[0]
            if "[" in factor_type and "]" in factor_type:
                if 'Tickfull' in factor_type or 'Tick1s' in factor_type or "Cancel" in factor_type:
                    start_date_new = 20170101
                if  "xdb_tickfull" in factor_type or "xdb_tick1s" in factor_type \
                        or "xdb_tickfulladdorder" in factor_type or "xdb_cancel" in factor_type:
                    start_date_new = 20170110

            # 预检测
            if int(test_date) < 20230630:
                if factor_name in all_factor_saturn.columns:
                    factor_res = {'factor_name': factor_name, 'pre_check': 'pass'}
                else:
                    factor_res = {'factor_name': factor_name, 'pre_check': '未通过pre_check'}
                    check_res_inf = check_res_inf.append(pd.DataFrame(factor_res.values(), index=factor_res.keys()).T)[
                        check_res_cols]
                    logger.warning(factor_res)
                    continue

            else:
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
                    logger.error("入库失败！预检测结果格式异常！factor_name={}, strategy=mimas".format(factor_name))
                    continue

                factor_res = {'factor_name': factor_name, 'pre_check': pre_check['check_inf']}
                if factor_res['pre_check'] != 'pass':
                    check_res_inf = check_res_inf.append(pd.DataFrame(factor_res.values(), index=factor_res.keys()).T)[
                        check_res_cols]
                    logger.warning(factor_res)
                    continue

            # 因子报告
            in_pkl = pd.read_pickle(
                '{}/{}_{}/{}.pkl'.format(factor_test_path, start_date_new, in_interval[1], factor_name))
            out_pkl = pd.read_pickle(
                '{}/{}_{}/{}.pkl'.format(factor_test_path, out_interval[0], out_interval[1], factor_name))

            # 因子值
            if int(test_date) < 20230630:
                if factor_name == 'lzt_day_pattern':
                    test_factor_df = all_factor_saturn[['lzt_label_pattern']]
                    test_factor_df.columns = ['lzt_day_pattern']
                else:
                    test_factor_df = all_factor_saturn[[factor_name]]
            else:
                test_factor_df = IO.read_data([start_date_new, out_interval[1]],
                                              alt='{}/{}/{}.h5'.format(factor_data_path, factor_name, factor_name))

            # 样本筛选，qyh:此处略去
            all_factor_df1 = all_factor_df.copy()

            test_factor_df = test_factor_df.reindex(all_factor_df.index)
            test_factor_df1 = test_factor_df.reindex(all_factor_df1.index)
            # corr_factor_ser = all_factor_df.corrwith(test_factor_df[factor_name], method='spearman').abs()
            corr_factor_ser = all_factor_df1.rank().corrwith(
                test_factor_df1[factor_name].rank()).abs()  # 比直接使用spearman更快
            high_corr_factor_list = list(corr_factor_ser[corr_factor_ser > max_corr].index) if len(
                all_factor_df.columns) > 0 else []
            high_corr_factor_list = [f for f in high_corr_factor_list if
                                     f in list(test_factor_inf['factor_name'].values) + other_basic_list]
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
                    high_corr_other_basic = [f for f in high_corr_factor_list if f in other_basic_list]
                    if len(high_corr_other_basic) > 0:
                        # 与other_basic类因子高相关，无法入库
                        factor_res['入库情况'] = '入库失败-与other_basic类因子高相关{}'.format(high_corr_other_basic)
                    else:
                        corr_factor_bank_type = 'linear' if 'linear' in list(
                            check_res_inf[check_res_inf['factor_name'].isin(high_corr_factor_list)][
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
        check_res_inf_ = check_res_inf_[check_res_inf_['提交时间'] <= test_date].drop(
            columns=['因子逻辑', 'emotion', '填充值', '是否针对注册制做调整', 'T-1日类别', '逻辑类别'])
        check_res_inf_.to_excel(res_path + 'check_res/check_res_tot_saturnnext_{}.xlsx'.format(test_date), index=False)
        check_res_inf_.to_excel(res_path + 'check_res/check_res_tot_mimas_{}.xlsx'.format(test_date), index=False)
        last_test_date = test_date

        # 因子入库
        check_res_inf_test = check_res_inf_[(check_res_inf_['提交时间'] == test_date)]
        check_res_inf_sta = pd.DataFrame()
        check_res_inf_sta['提交因子'] = check_res_inf_test.groupby('factor_owner').size()
        check_res_inf_in = check_res_inf_test[
            (check_res_inf_test['入库时间'] == test_date) & (check_res_inf_test['出库时间'].isna())]
        check_res_inf_sta['入库因子'] = check_res_inf_in.groupby('factor_owner').size()
        check_res_inf_sta.loc['全部'] = check_res_inf_sta.sum()
        check_res_inf_sta['入库率'] = check_res_inf_sta['入库因子'] / check_res_inf_sta['提交因子']
        check_res_inf_sta = check_res_inf_sta.reset_index()
        check_res_inf_sta['factor_owner'] = check_res_inf_sta['factor_owner'].replace(
            {'fc': '冯炽', 'qyh': '秦雨豪', 'skk': '孙康康', 'sss': '孙少森', 'wj': '王敬', 'xbc': '徐碧村', 'xly': '谢璐遥',
             'zwh': '张文虎'})
        check_res_inf_sta.to_excel(res_path + 'check_res/check_res_tot_saturnnext_sta.xlsx'.format(test_date),
                                   index=False)

        # 输出结果
        all_factor_df.to_pickle(res_path + 'sft_update_next.pkl')
        # 公共地址输出结果
        check_res_inf_.to_excel(res_public_path + 'check_res_tot_saturnnext.xlsx', index=False)
        all_factor_df.loc[pd.to_datetime(str(in_interval[0])):pd.to_datetime(str(in_interval[1]))].to_pickle(
            res_public_path + 'sft_update_next.pkl')
        #
        # #输出结果
        # update_file=res_path+'sft_update_next.h5'
        # if not os.path.exists(update_file):
        #     IO.pd_hdf5_writer(all_factor_df, update_file, dataset='data')
        # else:
        #     IO.pd_hdf5_writer(all_factor_df, update_file, dataset='data', override=True)
        #
        # #公共地址输出结果
        # check_res_inf_.to_excel(res_public_path + 'check_res_tot_saturnnext.xlsx', index=False)
        # update_public_file=res_public_path+'sft_update_next.h5'
        # if not os.path.exists(update_public_file):
        #     IO.pd_hdf5_writer(all_factor_df.loc[pd.to_datetime(str(in_interval[0])):pd.to_datetime(str(in_interval[1]))], update_public_file, dataset='data')
        # else:
        #     IO.pd_hdf5_writer(all_factor_df.loc[pd.to_datetime(str(in_interval[0])):pd.to_datetime(str(in_interval[1]))], update_public_file, dataset='data', override=True)
