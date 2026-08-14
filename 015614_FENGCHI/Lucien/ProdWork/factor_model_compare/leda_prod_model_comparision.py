# coding: utf-8
# Author：fengchi863
# Date ：2023/10/27 14:06

import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import datetime as dt
from dataApi.stockList import trans_int2windcode as Int2WC
s = FactorData()
from ProdWork.CommonTools import excel_saver
from ProdWork.Param_config_data import thred_dict_leda_v1 as thred_dict   # TODO: import 最新的

if __name__ == '__main__':
    print('===========metis_prod_model_comparision=============')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
        # nowdate = '20241008'
    datelist = s.tradingday(nowdate, nowdate)
    for nowdate in datelist:
        # nowdate = '20240529'
        tradeDatestr = s.tradingday(nowdate,-1)[0]
        yesDatestr = s.tradingday(tradeDatestr, -2)[0]

        from ProdWork.factor_model_compare.tools import gen_black_list
        filter_black_list, _, white_list = gen_black_list(nowdate)

        tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
        print(tradeDate)

        if sys.argv[2:]:
            env_list = sys.argv[2:]
        else:
            env_list =['prod', 'UAT']
            # env_list =['test']
            # env_list =['UAT']
        for environment in env_list:

            def check_dir(path):  # 路径生成函数
                if not os.path.exists(path):
                    os.makedirs(path)

            All_model_factor_diff_out_dict = {}
            All_model_predict_data_diff_out_dict = {}
            #------------------------------因子对比函数------------------------------
            def factor_comparison(local_factor_data,log_factor_data,environment):
                out_dict = {}
                local_factors = local_factor_data.columns
                log_factors = log_factor_data.columns
                out_dict['本地因子缺失'] = set(log_factors).difference(set(local_factors))
                out_dict['日志因子缺失'] = set(local_factors).difference(set(log_factors))
                common_factors = list(set(local_factors).intersection(set(log_factors)))
                total_factor_diff = pd.DataFrame()
                for factor in common_factors:
                    # factor = common_factors[0]
                    this_factor_diff = (local_factor_data[[factor]]-log_factor_data[[factor]]).rename(columns = {factor:'diff'})
                    this_factor_diff = this_factor_diff.join(local_factor_data[[factor]].rename(columns = {factor:'local'})).join(log_factor_data[[factor]].rename(columns = {factor:environment}))
                    this_factor_diff['Factor'] = factor
                    factor_diff_samples = this_factor_diff[np.abs(this_factor_diff['diff']) > 1e-8].reset_index().set_index(['Factor','Ticker'])
                    total_factor_diff = pd.concat([total_factor_diff,factor_diff_samples])
                return total_factor_diff

            #------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
            inf_df = pd.read_excel( '/data/group/800463/日内强势股/leda_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment), sheet_name='因子耗时')
            inf_df = inf_df.rename(columns = {'Unnamed: 0':'Ticker'}).set_index('Ticker')
            for model_name in thred_dict.keys():
                if model_name+'_probability' not in inf_df.columns:
                    inf_df[model_name+'_probability'] = np.nan

            #UAT中的信号
            log_signal = inf_df[['shouldBuySignal','sum_signals']].rename(columns = {'shouldBuySignal':environment+'_signal','sum_signals':environment+'_sum_signals'})

            total_model_list = list(map(lambda x:x[:~11],np.array(inf_df.columns)[np.array(list(map(lambda x:'probability' in x ,list(inf_df.columns))))]))
            total_cla_model_predict_result = pd.DataFrame()
            total_reg_model_predict_result = pd.DataFrame()
            total_ZT_model_predict_result = pd.DataFrame()
            for model_name in thred_dict.keys():
                if model_name+'_probability' not in inf_df.columns:
                    inf_df[model_name+'_probability'] = np.nan

            # TODO:本地与实盘的模型命名dict 对应关系
            prod_model = ['totalRegFSRSXgbZwhModel', 'totalRegFSRSXgbSkkModel', 'totalRegFSV8XgbFcModel',
                          'totalRegXgbFcModel', 'totalRegFSV8XgbXbcModel', 'totalRegFSRSXgbXbcModel']
            log_model = ['totalRegFSRSXgbZwhModel',
                         'totalRegFSRSXgbSkkModel',
                         'totalRegFSV8XgbFcModel',
                         'totalRegXgbFcModel',
                         'totalRegFSV8XgbXbcModel',
                         'totalRegFSRSXgbXbcModel']
            prod_proba1 = [x.split('Model')[0] +'_proba1' for x in prod_model]

            model_rename_dict = dict(zip(prod_model, log_model))
            model_proba_dict = dict(zip(log_model, prod_proba1))
            # TODO: wj提供，本地模型路径
            pred_path = '/data/group/800463/wangj/model_signal/Leda/prod_v1/%s/%s_%s_jupiterZ_fac_20231219_daily_pred_prodmodel.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
            import time
            while not os.path.exists(pred_path):
                print(f'缺失{pred_path}')
                time.sleep(60)
            All_model_predict_data = pd.read_csv(open(pred_path)).set_index(['Ticker'])
            All_model_predict_data.rename(columns = model_rename_dict, inplace = True)
            inf_df = inf_df.loc[list(set(inf_df.index.tolist())&set(All_model_predict_data.index.tolist()))].sort_index()
            All_model_predict_data_diff_out_dict = {}
            for model_name in log_model:
                print(model_name)
                tmp_model_log_prob =inf_df[[model_name+'_probability']].rename(columns = {model_name+'_probability':model_name+'_%s_prob'%environment}).reindex(index=All_model_predict_data.index)
                tmp_model_log_prob[model_name+'_local_prob'] = All_model_predict_data[model_proba_dict[model_name]]#.reindex(tmp_model_log_prob.index)
                tmp_model_log_prob[model_name+'_diff_prob'] = tmp_model_log_prob[model_name+'_%s_prob'%environment].astype(float)-tmp_model_log_prob[model_name+'_local_prob']
                All_model_predict_data_diff_out_dict[model_name] = tmp_model_log_prob
                tmp_model_signal = (tmp_model_log_prob[model_name+'_local_prob'] >= thred_dict[model_name]).reindex(All_model_predict_data.index)
                if 'Cla' in model_name:
                    total_cla_model_predict_result = pd.concat([total_cla_model_predict_result, tmp_model_signal], axis=1, sort=True)
                elif 'ZT' not in model_name:
                    total_reg_model_predict_result = pd.concat([total_reg_model_predict_result, tmp_model_signal], axis=1, sort=True)
                elif 'ZT' in model_name:
                    total_ZT_model_predict_result = pd.concat([total_ZT_model_predict_result, tmp_model_signal], axis=1, sort=True)
            #------------------------------总结df------------------------------------------------
            summary_dict = {}
            print('start summary')
            for model in log_model:
                model_question_list = []
                #print(model)
                if (np.abs(All_model_predict_data_diff_out_dict[model][model+'_diff_prob']) > 1e-5).sum() > 0:
                    model_question_list.append('模型存在概率差异！！！最大绝对差异为%f'%np.abs(All_model_predict_data_diff_out_dict[model][model+'_diff_prob']).max())
                else:
                    model_question_list.append('模型不存在概率差异~~~')

                summary_dict[model] = model_question_list

            # TODO: sss提供
            tradeDateInt = int(tradeDate.replace('-', ''))
            while not os.path.exists(f'/data/group/800463/project/project1_prod/right_v2310/daily_data/{tradeDateInt}/leda_v2310_{tradeDateInt}.pkl'):
                print(f'缺失{all_df}')
                time.sleep(60)
            all_df = pd.read_pickle(f'/data/group/800463/project/project1_prod/right_v2310/daily_data/{tradeDateInt}/leda_v2310_{tradeDateInt}.pkl')
            all_df['is_sample_leda'] = (all_df['ZT_Time'] >= 93000000) & \
                                       (all_df['ZT_Time'] <= 143000000) & \
                                       (all_df['open_is_zt'] == 0) & \
                                       (all_df['T_o2pre'] >= -0.05) & \
                                       (all_df['after_not_ul_len'] > 10) & \
                                       (all_df['pre_close'] >= 2) & \
                                       (all_df['high_price'] < (all_df['ul_price'])) & \
                                       (all_df['min_is_dt'] == 0) & \
                                       (all_df['last_is_zt'] == 1) & \
                                       (all_df['saturn_lzt_day_pattern'].isin([3,4]))
            all_df = all_df.reset_index().set_index('Ticker')
            # 对样本进行reindex，其他的填充为nan
            total_reg_model_predict_result.index.name = 'Ticker'
            total_cla_model_predict_result.index.name = 'Ticker'
            total_reg_model_predict_result = total_reg_model_predict_result.reindex(all_df.index)
            total_cla_model_predict_result = total_cla_model_predict_result.reindex(all_df.index)

            # 生成本地投票结果
            reg_stacking = total_reg_model_predict_result.sum(axis = 1)
            cla_stacking = total_cla_model_predict_result.sum(axis = 1)
            def jupiter_voting1(reg_stacking,cla_stacking):
                condition1 = (reg_stacking + cla_stacking) >= 5
                condition2 = (cla_stacking==2) & (reg_stacking==2)
                condition3 = (cla_stacking==1) & (reg_stacking==4)
                condition4 = (cla_stacking==0) & (reg_stacking>=5)
                return (condition1 | condition2) & (condition3==False) & (condition4==False)
            def jupiter_voting(reg_stacking, cla_stacking):
                condition1 = reg_stacking  >= 4

                return condition1
            local_predict = jupiter_voting(reg_stacking,cla_stacking)
            local_predict = pd.DataFrame(local_predict)
            local_predict.columns = ['本地投票结果']
            local_predict['本地回归投票'] = reg_stacking
            local_predict['本地分类投票'] = cla_stacking
            if environment == 'prod':
                local_predict['是否在黑名单'] = 0
                sub_index = list(set(local_predict.index.tolist())&set(filter_black_list))
                local_predict.loc[sub_index,'是否在黑名单'] = 1

            excel_save_dict = {}
            excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
            excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(total_reg_model_predict_result).join(total_cla_model_predict_result).join(total_ZT_model_predict_result).join(all_df[['is_sample_leda']])
            excel_save_dict['线上投票结果'] = local_predict.join(log_signal)

            """添加是否有持仓标志 20231103"""
            tradeDateInt = int(tradeDatestr.replace('-', ''))
            o45 = pd.read_excel(f'/data/group/800463/position/O45_组合证券_{tradeDateInt}.xlsx', index_col=0)
            o45 = o45[~o45['业务日期'].isna()]
            holding_list = o45['证券代码'].map(lambda x: Int2WC(x)).tolist()
            tmp = excel_save_dict['本地投票结果']
            tmp['是否有持仓'] = tmp.index.map(lambda x: True if x in holding_list else False)
            excel_save_dict['本地投票结果'] = tmp

            """添加是否在黑名单 20231103"""
            tmp = excel_save_dict['本地投票结果']
            tmp['是否在黑名单'] = tmp.index.map(lambda x: True if x in filter_black_list else False)
            tmp['是否在白名单'] = tmp.index.map(lambda x: True if x in white_list else False)
            excel_save_dict['本地投票结果'] = tmp

            for model_name in prod_model:
                excel_save_dict[model_rename_dict[model_name] + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_rename_dict[model_name]]
            check_dir('/data/group/800463/日内强势股/leda_log_parse/模型差异/%s/'%tradeDatestr)
            excel_saver(excel_save_dict,'/data/group/800463/日内强势股/leda_log_parse/模型差异/%s/模型差异Leda_%s_%s.xlsx'%(tradeDatestr, tradeDatestr, environment))
            if environment == 'prod':
                from dataApi.sendInfo import send_message
                send_message(f'{nowdate} leda生成完毕')