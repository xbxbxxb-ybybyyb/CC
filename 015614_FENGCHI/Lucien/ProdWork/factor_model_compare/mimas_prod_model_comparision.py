# coding: utf-8
# Author：fengchi863
# Date ：2025/5/26 10:34

'''
Mimas每日模型信号差异
'''

import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import datetime as dt
from dataApi.stockList import trans_int2windcode as Int2WC
s = FactorData()
import time
from ProdWork.CommonTools import excel_saver
from ProdWork.Param_config_data import thred_dict_mimas_v1 as thred_dict

if __name__ == '__main__':
    print('=============mimas_uat_model_comparision=============')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
        # nowdate = '20250801'    # 第二天
    tradeDatestr = s.tradingday(nowdate, -1)[0]
    yesDatestr = s.tradingday(tradeDatestr, -2)[0]

    from ProdWork.factor_model_compare.tools import gen_black_list
    filter_black_list, _, white_list = gen_black_list(nowdate)

    tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
    print(tradeDate)
    if sys.argv[2:]:
        env_list = sys.argv[2:]
    else:
        # env_list = ['night']
        env_list = ['prod', 'UAT']
        # env_list = ['xdev']
        # env_list = ['UAT']
    for environment in env_list:
        print(environment)
        def check_dir(path):  # 路径生成函数
            if not os.path.exists(path):
                os.makedirs(path)

        All_model_predict_data_diff_out_dict = {}
        # ------------------------------因子对比函数------------------------------
        def factor_comparison(local_factor_data, log_factor_data, environment):
            out_dict = {}
            local_factors = local_factor_data.columns
            log_factors = log_factor_data.columns
            out_dict['本地因子缺失'] = set(log_factors).difference(set(local_factors))
            out_dict['日志因子缺失'] = set(local_factors).difference(set(log_factors))
            common_factors = list(set(local_factors).intersection(set(log_factors)))
            total_factor_diff = pd.DataFrame()
            for factor in common_factors:
                # factor = common_factors[0]
                this_factor_diff = (local_factor_data[[factor]] - log_factor_data[[factor]]).rename(columns={factor: 'diff'})
                this_factor_diff = this_factor_diff.join(local_factor_data[[factor]].rename(columns={factor: 'local'})).join(log_factor_data[[factor]].rename(columns={factor: environment}))
                this_factor_diff['Factor'] = factor
                factor_diff_samples = this_factor_diff[np.abs(this_factor_diff['diff']) > 1e-8].reset_index().set_index(['Factor', 'Ticker'])
                total_factor_diff = pd.concat([total_factor_diff, factor_diff_samples])
            return total_factor_diff

        # ------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
        inf_df = pd.read_excel('/data/group/800463/日内强势股/mimas_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment),
                               sheetname='因子耗时Mimas')
        # inf_df = inf_df.rename(columns={'index': 'Ticker'}).set_index('Ticker')
        inf_df = inf_df.rename(columns={'index': 'Ticker'}).set_index('Unnamed: 0')
        inf_df = inf_df.loc[~inf_df.index.duplicated(keep='first')].sort_index()
        # UAT中的信号

        log_signal = inf_df[['shouldBuySignal', 'sum_signals']].rename(
            columns={'shouldBuySignal': environment + '_signal', 'sum_signals': '%s_sum_signals' % environment})

        total_model_list = list(map(lambda x: x[:~11], np.array(inf_df.columns)[
            np.array(list(map(lambda x: 'probability' in x, list(inf_df.columns))))]))
        total_cla_model_predict_result = pd.DataFrame()
        total_reg_model_predict_result = pd.DataFrame()
        for model_name in thred_dict.keys():
            if model_name + '_probability' not in inf_df.columns:
                inf_df[model_name + '_probability'] = np.nan
        Log_triggered_samples = inf_df.index

        # TODO:本地与实盘的模型命名dict 对应关系
        prod_model = ['totalRegpctp5_FSV11XgbWjModel',
                      'totalRegbase_FSV8XgbWjModel',
                      'totalRegbase_FSRSXgbXbcModel',
                      'totalRegbase_SkkXgbSkkModel',
                      'totalRegbase_FSRSXgbZwhModel',
                      'totalRegbase_FSZWHXgbZwhModel']
        log_model = list(thred_dict.keys())
        log_model = ['totalRegpctp5_FSV11XgbWjModel',
                      'totalRegbase_FSV8XgbWjModel',
                      'totalRegbase_FSRSXgbXbcModel',
                      'totalRegbase_SkkXgbSkkModel',
                      'totalRegbase_FSRSXgbZwhModel',
                      'totalRegbase_FSZWHXgbZwhModel']
        prod_proba1 = [x.split('Model')[0] + '_proba1' for x in prod_model]

        model_rename_dict = dict(zip(prod_model, log_model))
        model_proba_dict = dict(zip(log_model, prod_proba1))
        # TODO: wj提供，本地模型路径
        pred_path = '/data/group/800463/wangj/model_signal/Mimas/hs1_v1/%s/%s_%s_mimas_fac_20250416_daily_pred_prodmodel.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        while not os.path.exists(pred_path):
            print(f'缺失文件：{pred_path}')
            time.sleep(60)
        All_model_predict_data = pd.read_csv(open(pred_path)).set_index(['Ticker'])
        All_model_predict_data.rename(columns=model_rename_dict, inplace=True)
        # inf_df = inf_df.loc[list(set(inf_df.index.tolist()) & set(All_model_predict_data.index.tolist()))].sort_index()
        All_model_predict_data_diff_out_dict = {}
        for model_name in log_model:
            print(model_name)
            tmp_model_local_prob = All_model_predict_data[model_proba_dict[model_name]].rename(model_name + '_local_prob')
            tmp_model_log_prob = inf_df[[model_name + '_probability']].rename(columns={model_name + '_probability': model_name + '_%s_prob' % environment})
            tmp_model_log_prob[model_name + '_local_prob'] = All_model_predict_data[model_proba_dict[model_name]]  # .reindex(tmp_model_log_prob.index)
            tmp_model_log_prob[model_name + '_diff_prob'] = tmp_model_log_prob[model_name + '_%s_prob' % environment].astype(float) - tmp_model_log_prob[model_name + '_local_prob']
            All_model_predict_data_diff_out_dict[model_name] = tmp_model_log_prob
            tmp_model_signal = (tmp_model_local_prob >= thred_dict[model_name]).reindex(All_model_predict_data.index)
            if 'Cla' in model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result, tmp_model_signal], axis=1, sort=True)
            elif 'ZT' not in model_name:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result, tmp_model_signal], axis=1, sort=True)
            elif 'ZT' in model_name:
                total_ZT_model_predict_result = pd.concat([total_ZT_model_predict_result, tmp_model_signal], axis=1, sort=True)

        # ------------------------------总结df------------------------------------------------
        saturn_factor_fpath = f'/data/group/800463/project/project2_prod/daily_data/{tradeDatestr}_mimas_v1/mimas_factor_v1_{tradeDatestr}.pkl'
        while not os.path.exists(saturn_factor_fpath):
            print(f'缺失文件：{saturn_factor_fpath}')
            time.sleep(60)

        summary_dict = {}
        for model in total_model_list:
            # model = total_model_list[0]
            model_question_list = []
            common_samples = list(set(All_model_predict_data_diff_out_dict[model].index.tolist()))
            if (np.abs(All_model_predict_data_diff_out_dict[model].loc[common_samples, model + '_diff_prob']) > 1e-5).sum() > 0:
                model_question_list.append('模型存在概率差异！！！最大绝对差异为%f' % np.abs(
                    All_model_predict_data_diff_out_dict[model].loc[common_samples, model + '_diff_prob']).max())
            else:
                model_question_list.append('模型不存在概率差异~~~')
            summary_dict[model] = model_question_list

        # TODO: sss提供
        param = pd.read_pickle(f'/data/group/800463/project/project2_prod/daily_data/{tradeDatestr}_mimas_v1/mimas_factor_v1_{tradeDatestr}.pkl')
        param_filter = pd.read_pickle(f'/data/group/800463/project/project2_prod/daily_data/{tradeDatestr}_mimas_v1/mimas_filter_factor_v1_{tradeDatestr}.pkl')
        param_filter = param_filter.query('Next_pre_close >= 2')
        param['is_sample_mimas'] = param.index.get_level_values(1).map(lambda x: x in param_filter.index.get_level_values(1))

        param = param.reset_index().set_index('Ticker')
        # 对样本进行reindex，其他的填充为nan
        total_reg_model_predict_result.index.name = 'Ticker'
        total_cla_model_predict_result.index.name = 'Ticker'
        total_reg_model_predict_result = total_reg_model_predict_result.reindex(param.index)
        total_cla_model_predict_result = total_cla_model_predict_result.reindex(param.index)

        # 生成本地投票结果
        reg_stacking = total_reg_model_predict_result.sum(axis=1)
        cla_stacking = total_cla_model_predict_result.sum(axis=1)


        def jupiter_voting1(reg_stacking, cla_stacking):
            condition1 = (reg_stacking + cla_stacking) >= 5
            condition2 = (cla_stacking == 2) & (reg_stacking == 2)
            condition3 = (cla_stacking == 1) & (reg_stacking == 4)
            condition4 = (cla_stacking == 0) & (reg_stacking >= 5)
            return (condition1 | condition2) & (condition3 == False) & (condition4 == False)


        def jupiter_voting(reg_stacking, cla_stacking):
            condition1 = reg_stacking >= 2
            return condition1

        local_predict = jupiter_voting(reg_stacking, cla_stacking)
        local_predict = pd.DataFrame(local_predict)
        local_predict.columns = ['本地投票结果']
        local_predict['本地投票数量'] = reg_stacking + cla_stacking
        local_predict['是否在黑名单'] = 0
        local_predict['是否在白名单'] = 0
        sub_index = list(set(local_predict.index.tolist()) & set(filter_black_list))
        local_predict.loc[sub_index, '是否在黑名单'] = 1
        sub_index = list(set(local_predict.index.tolist()) & set(white_list))
        local_predict.loc[sub_index, '是否在白名单'] = 1

        # # 添加当天是否含有策略参数
        # # param_list = list(map(lambda x: x[:9], os.listdir(f'/data/user/013551/forXT/Mimas/param/20250514_type2/{nowdate}/Mimas/{nowdate}_mimas')))
        # param_list = os.listdir(f'/data/user/013551/forXT/Mimas/param/param_new/MimasStrategy/backend_sz_type1_{nowdate}/stock_params/') + \
        #     os.listdir(f'/data/user/013551/forXT/Mimas/param/param_new/MimasStrategy/backend_sh_type1_{nowdate}/stock_params/')
        # param_list = list(map(lambda x: x[:9], param_list))
        # param['has_param'] = param.index.map(lambda x: x in param_list)

        excel_save_dict = {}
        excel_save_dict['差异汇总'] = pd.Series(summary_dict, name='差异汇总')
        # excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(param[['is_sample_mimas', 'has_param']]).join(total_reg_model_predict_result)
        excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(param[['is_sample_mimas']]).join(total_reg_model_predict_result)

        """添加filter列 Mimas上线后有个filter"""
        excel_save_dict['本地投票结果'] = excel_save_dict['本地投票结果']

        """添加是否有持仓标志"""
        tradeDateInt = int(tradeDatestr.replace('-', ''))
        o45 = pd.read_excel(f'/data/group/800463/position/O45_组合证券_{tradeDateInt}.xlsx', index_col=0)
        o45 = o45[~o45['业务日期'].isna()]
        holding_list = o45['证券代码'].map(lambda x: Int2WC(x)).tolist()
        tmp = excel_save_dict['本地投票结果']
        tmp['是否有持仓'] = tmp.index.map(lambda x: True if x in holding_list else False)
        excel_save_dict['本地投票结果'] = tmp

        # """添加是否在黑名单 20230804"""

        for model_name in total_model_list:
            excel_save_dict[model_name] = All_model_predict_data_diff_out_dict[model_name]

        check_dir('/data/group/800463/日内强势股/mimas_log_parse/模型差异/%s' % tradeDatestr)
        excel_saver(excel_save_dict, '/data/group/800463/日内强势股/mimas_log_parse/模型差异/%s/模型差异_%s_%s_mimas.xlsx' % (tradeDatestr, tradeDatestr, environment))
        # 监测是否存在模型差异
        from dataApi.sendInfo import send_message

        diff_num = len(list(filter(lambda x: '模型存在概率差异' in x, list(summary_dict.values()))))
        if diff_num == 0:
            send_message(f'{nowdate} Mimas {environment} 存在模型差异 {diff_num} !!!!!!')
        else:
            send_message(f'{nowdate} Mimas {environment} 不存在模型差异')