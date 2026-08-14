# coding: utf-8
# Author：fengchi863
# Date ：2023/5/16 19:10

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import datetime as dt
s = FactorData()
from ProdWork.CommonTools import excel_saver
from ProdWork.Param_config_data import thred_dict_jupz_v2 as thred_dict

if __name__ == '__main__':
    print('==========jupz_uat_model_comparision===========')
    nowdate = dt.datetime.now().strftime('%Y%m%d')
    nowdate = '20240119'
    datelist = s.tradingday(nowdate, nowdate)
    for nowdate in datelist:
        tradeDatestr = s.tradingday(nowdate,-2)[0]
        yesDatestr = s.tradingday(tradeDatestr, -2)[0]
        white_list_list = ['/data/group/800463/stock_list/white_list/%s.xlsx' % tradeDatestr]
        grey_list_list = ['/data/group/800463/stock_list/grey_list/grey_list_%s.xlsx' % tradeDatestr]
        black_list_list = [
            '/data/group/800463/stock_list/black_other_list/黑名单-20210621.xls',
            '/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx',
            '/data/group/800463/stock_list/abnormal_notice_list/abnormal_notice_list_%s.xlsx' % tradeDatestr,
            '/data/group/800463/stock_list/pre_st_list/pre_st_list_%s.xlsx' % yesDatestr,
            '/data/group/800463/stock_list/after_dt_list/after_dt_list_%s.xlsx' % yesDatestr,
            '/data/group/800463/stock_list/defer_reply_list/defer_reply_list_%s.xlsx' % yesDatestr,
        ]
        all_black_list = []
        for black_list in black_list_list:
            black_df = pd.read_excel(black_list, dtype=str)
            if '出池时间' in black_df.columns.tolist():
                black_df = black_df[black_df['出池时间'].isnull()]
            if '证券代码' in black_df.columns.tolist():
                all_black_list = all_black_list + list(black_df['证券代码'])
            else:
                all_black_list = all_black_list + list(black_df['股票代码'])
        all_black_list = list(all_black_list)
        all_black_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_black_list]
        all_grey_list = []
        for grey_list in grey_list_list:
            grey_df = pd.read_excel(grey_list, dtype=str)
            if '出池时间' in grey_df.columns.tolist():
                grey_df = grey_df[grey_df['出池时间'].isnull()]
            if '证券代码' in grey_df.columns.tolist():
                all_grey_list = all_grey_list + list(grey_df['证券代码'])
            else:
                all_grey_list = all_grey_list + list(grey_df['股票代码'])
        all_grey_list = list(all_grey_list)
        all_grey_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_grey_list]

        filter_black_list = list(set(all_black_list) - set(all_grey_list))
        tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
        print(tradeDate)

        env_list =['prod', 'SZEX', 'SHEX', 'UAT', 'UAT_50_51', 'UAT_49_53']
        env_list = ['UAT']
        for environment in env_list:
            print(f'##################{environment}')
            def check_dir(path):
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
            inf_df = pd.read_excel( '/data/group/800463/日内强势股/sell_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment), sheet_name='JupiterZ样本')
            inf_df = inf_df.loc[inf_df.filter(regex='ZT.*?_probability').dropna(how='all', axis=0).index]
            inf_df = inf_df.rename(columns = {'Unnamed: 0':'Ticker'}).set_index('Ticker')
            for model_name in thred_dict.keys():
                if model_name+'_probability' not in inf_df.columns:
                    inf_df[model_name+'_probability'] = np.nan

            # UAT中的信号
            log_signal = inf_df[['sum_signals']].rename(columns = {'sum_signals':environment+'_sum_signals'})

            total_model_list = list(map(lambda x:x[:~11], np.array(inf_df.columns)[np.array(list(map(lambda x:'probability' in x ,list(inf_df.columns))))]))
            total_cla_model_predict_result = pd.DataFrame()
            total_reg_model_predict_result = pd.DataFrame()
            total_ZT_model_predict_result = pd.DataFrame()
            for model_name in thred_dict.keys():
                if model_name + '_probability' not in inf_df.columns:
                    inf_df[model_name+'_probability'] = np.nan

            # prod_model = ['totalRegLgbWjModel',
            #               'totalRegFSV8XgbSkkModel',
            #               'pat3RegFSV8LrXlyModel',
            #               'pat4RegFSV8LrXlyModel',
            #               'totalRegFSV10LrXbcModel',
            #               'totalRegFSV11XgbSkkModel',
            #               'totalRegXgbXbcModel']
            log_model = list(thred_dict.keys())
            log_model = list(filter(lambda x: x.startswith('ZT'), log_model))
            # log_model = ['totalWjLgbModel', 'totalSkkXgbFSV8Model', 'pat3XlyPMMLModel', 'pat4XlyPMMLModel',
            #              'totalXbcPMMLModel', 'totalSkkXgbFSV11Model', 'totalXbcXgbModel']
            prod_proba1 = [x.split('Model')[0] +'_proba1' for x in log_model]

            # model_rename_dict = dict(zip(prod_model, log_model))
            model_proba_dict = dict(zip(log_model, prod_proba1))

            pred_path = f'/data/group/800463/wangj/model_signal/JupiterZ/prod_v2/{tradeDatestr}/{tradeDatestr}_{tradeDatestr}_jupiterZ_fac_20230415_daily_pred_prodmodel.csv'

            All_model_predict_data = pd.read_csv(open(pred_path)).set_index(['Ticker'])
            # All_model_predict_data.rename(columns = model_rename_dict, inplace = True)    # 20230516 by fengc 和日志中模型名字一样，不需要rename
            inf_df = inf_df.loc[list(set(inf_df.index.tolist()) & set(All_model_predict_data.index.tolist()))].sort_index()
            All_model_predict_data_diff_out_dict = {}
            for model_name in log_model:
                print(model_name)
                tmp_model_log_prob = inf_df[[model_name + '_probability']].rename(columns={model_name + '_probability': model_name + '_%s_prob' % environment})
                tmp_model_log_prob[model_name + '_local_prob'] = All_model_predict_data[model_proba_dict[model_name]]
                tmp_model_log_prob[model_name + '_diff_prob'] = tmp_model_log_prob[model_name + '_%s_prob' % environment].astype(float) - tmp_model_log_prob[model_name + '_local_prob']
                All_model_predict_data_diff_out_dict[model_name] = tmp_model_log_prob
                tmp_model_signal = (tmp_model_log_prob[model_name + '_local_prob'] >= thred_dict[model_name]).reindex(All_model_predict_data.index)
                if 'Cla' in model_name:
                    total_cla_model_predict_result = pd.concat([total_cla_model_predict_result, tmp_model_signal], axis=1, sort=True)
                elif 'ZT' not in model_name:
                    total_reg_model_predict_result = pd.concat([total_reg_model_predict_result, tmp_model_signal], axis=1, sort=True)
                elif 'ZT' in model_name:
                    total_ZT_model_predict_result = pd.concat([total_ZT_model_predict_result, tmp_model_signal], axis=1, sort=True)
            # ------------------------------总结df------------------------------------------------
            summary_dict = {}
            print('start summary')
            for model in log_model:
                model_question_list = []
                if (np.abs(All_model_predict_data_diff_out_dict[model][model + '_diff_prob']) > 1e-5).sum() > 0:
                    model_question_list.append('模型存在概率差异！！！最大绝对差异为%f' % np.abs(All_model_predict_data_diff_out_dict[model][model + '_diff_prob']).max())
                else:
                    model_question_list.append('模型不存在概率差异~~~')

                summary_dict[model] = model_question_list

            local_predict = pd.DataFrame(index=inf_df.index)

            # 20230517 by fenc 新增ZT的分类回归投票
            ZT_predict = (total_ZT_model_predict_result.sum(axis=1) >= 4)
            ZT_predict_num = total_ZT_model_predict_result.sum(axis=1)
            local_predict.loc[ZT_predict[total_ZT_model_predict_result['ZTTotalFcLgbModel_local_prob'].notnull()].index, '本地投票结果'] = ZT_predict
            local_predict.loc[ZT_predict[total_ZT_model_predict_result['ZTTotalFcLgbModel_local_prob'].notnull()].index, '本地回归投票'] = ZT_predict_num - total_ZT_model_predict_result.filter(regex='Cla').sum(axis=1)
            local_predict.loc[ZT_predict[total_ZT_model_predict_result['ZTTotalFcLgbModel_local_prob'].notnull()].index, '本地分类投票'] = total_ZT_model_predict_result.filter(regex='Cla').sum(axis=1)

            if environment == 'prod':
                local_predict['是否在黑名单'] = 0
                sub_index = list(set(local_predict.index.tolist())&set(filter_black_list))
                local_predict.loc[sub_index,'是否在黑名单'] = 1

            excel_save_dict = dict()
            excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
            excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(total_reg_model_predict_result).join(total_cla_model_predict_result).join(total_ZT_model_predict_result)
            excel_save_dict['线上投票结果'] = local_predict.join(log_signal)

            for model_name in log_model:
                excel_save_dict[(model_name + '_预测概率差异')[:30]] = All_model_predict_data_diff_out_dict[model_name]
            check_dir('/data/group/800463/日内强势股/sell_log_parse/模型差异/%s/' % tradeDatestr)
            excel_saver(excel_save_dict, '/data/group/800463/日内强势股/sell_log_parse/模型差异/%s/JupiterZ模型差异_%s_%s.xlsx' % (tradeDatestr, tradeDatestr, environment))