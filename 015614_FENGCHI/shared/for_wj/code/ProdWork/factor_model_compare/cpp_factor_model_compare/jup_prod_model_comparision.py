import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
import re
from LucienUtil import IO
# from multifactor.IO.IO_enums import *
import sys
sys.path.append("../../")
sys.path.append("/../..")
from xquant.factordata import FactorData
import datetime as dt
s = FactorData()
from ProdWork.CommonTools import excel_saver
from ProdWork.Param_config_data import thred_dict_jup_v9 as thred_dict

if __name__ == '__main__':
    print('===========jup_prod_model_comparision============')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
    datelist = s.tradingday(nowdate, nowdate)

    for nowdate in datelist:
        tradeDatestr = s.tradingday(nowdate,-2)[0]
        yesDatestr = s.tradingday(tradeDatestr, -2)[0]
        white_list_list = ['/data/group/800463/stock_list/white_list/%s.xlsx' % tradeDatestr]
        grey_list_list = ['/data/group/800463/stock_list/grey_list/grey_list_%s.xlsx'%tradeDatestr]
        black_list_list = [
            '/data/group/800463/stock_list/black_other_list/黑名单-20210621.xls',
            '/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx',
            '/data/group/800463/stock_list/abnormal_notice_list/abnormal_notice_list_%s.xlsx'%tradeDatestr,
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
        all_black_list = [x +'.SH' if x[0] == '6' else x+'.SZ' for x in all_black_list]
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

        filter_black_list = list(set(all_black_list)-set(all_grey_list))
        tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
        #tradeDate = '2023-03-24'
        print(tradeDate)
        if sys.argv[2:]:
            env_list = sys.argv[2:]
        else:
            env_list = ['prod','SZEX','SHEX','UAT','UAT_50_51','UAT_49_53','UAT_lite']
        for environment in env_list:
        # for environment in ['UAT_lite']:#['prod','UAT','SZEX','SHEX','UAT_lite','UAT_other','night','test1'][:6]: # 可选择 UAT 和 night
            All_model_factor_diff_out_dict = {}
            All_model_predict_data_diff_out_dict = {}
            ztmodel_rename_dict = {
                                 'ZTBysModel': 'ZTBys',
                                 'ZTDjRegModel': 'ZTDjReg',
                                 'ZTDjClaModel': 'ZTDjCla'}
            def check_dir(path):  # 路径生成函数
                if not os.path.exists(path):
                    os.makedirs(path)

            # ------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
            inf_df = pd.read_excel(
                '/data/group/800463/日内强势股/cpp_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment),
                sheet_name='因子耗时')
            inf_df = inf_df.rename(columns={'Unnamed: 0': 'Ticker'}).set_index('Ticker')
            for model_name in thred_dict.keys():
                if model_name + '_probability' not in inf_df.columns:
                    inf_df[model_name + '_probability'] = np.nan

            # UAT中的信号
            log_signal = inf_df[['shouldBuySignal', 'sum_signals']].rename(
                columns={'shouldBuySignal': environment + '_signal',
                         'sum_signals': environment + '_sum_signals'})

            total_model_list = list(map(lambda x: x[:~11], np.array(inf_df.columns)[
                np.array(list(map(lambda x: 'probability' in x, list(inf_df.columns))))]))
            total_cla_model_predict_result = pd.DataFrame()
            total_reg_model_predict_result = pd.DataFrame()
            total_ZT_model_predict_result = pd.DataFrame()
            for model_name in thred_dict.keys():
                if model_name + '_probability' not in inf_df.columns:
                    inf_df[model_name + '_probability'] = np.nan
            DJ_model_name_all = ['ZTDjRegModel', 'ZTDjClaModel']
            for DJ_model_name in DJ_model_name_all:
                print(DJ_model_name)
                if DJ_model_name == 'ZTDjRegModel':
                    dj_path = '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_reg_v2_zt/pred_prob.h5' % tradeDatestr
                    if os.path.exists(dj_path):
                        DJ_model_local_prob = pd.read_hdf(dj_path)
                    else:
                        DJ_model_local_prob = pd.DataFrame(columns = ['dt','Ticker','pred_prob'])
                elif DJ_model_name == 'ZTDjClaModel':
                    dj_path = '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_cla_v2_zt/pred_prob.h5' % tradeDatestr
                    if os.path.exists(dj_path):
                        DJ_model_local_prob = pd.read_hdf(dj_path)
                    else:
                        DJ_model_local_prob = pd.DataFrame(columns = ['dt','Ticker','pred_prob'])

                DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(
                    columns={'pred_prob': DJ_model_name + '_local_prob'})
                DJ_model_log_prob = inf_df[[DJ_model_name + '_probability']].rename(
                    columns={DJ_model_name + '_probability': DJ_model_name + '_%s_prob' % environment})
                DJ_model_log_prob[DJ_model_name + '_local_prob'] = DJ_model_local_prob[DJ_model_name + '_local_prob']
                DJ_model_log_prob[DJ_model_name + '_diff_prob'] = DJ_model_log_prob[
                                                                      DJ_model_name + '_%s_prob' % environment] - \
                                                                  DJ_model_local_prob[DJ_model_name + '_local_prob']
                All_model_predict_data_diff_out_dict[DJ_model_name] = DJ_model_log_prob
                DJ_model_signal = (DJ_model_local_prob >= thred_dict[DJ_model_name]).reindex(
                    DJ_model_local_prob[DJ_model_local_prob[DJ_model_name + '_local_prob'].notnull()].index)
                if ('Cla' in DJ_model_name) & ('ZT' not in DJ_model_name):
                    total_cla_model_predict_result = pd.concat(
                        [total_cla_model_predict_result, DJ_model_local_prob >= thred_dict[DJ_model_name]], axis=1)
                elif ('ZT' not in DJ_model_name):
                    total_reg_model_predict_result = pd.concat(
                        [total_reg_model_predict_result, DJ_model_local_prob >= thred_dict[DJ_model_name]], axis=1)
                if 'ZT' in DJ_model_name:
                    total_ZT_model_predict_result = pd.concat([total_ZT_model_predict_result, DJ_model_signal], axis=1)
            XLY_model_name = ['ZTBysModel']
            for model_name in XLY_model_name:
                print(model_name)
                # 核对模型的预测数据
                xly_model_local_prob = pd.read_pickle(
                    '/data/group/800463/xiely/model_signal/%s/model_predict.pkl' % tradeDatestr).reset_index() \
                    .drop(['dt'], axis=1).set_index('Ticker').reindex(DJ_model_local_prob.index.tolist()) \
                    .rename(columns={model_name + '_proba': model_name + '_local_prob'})[[model_name + '_local_prob']]
                xly_model_log_prob = inf_df[[model_name + '_probability']].rename(
                    columns={model_name + '_probability': model_name + '_%s_prob' % environment})
                xly_model_log_prob[model_name + '_local_prob'] = xly_model_local_prob[model_name + '_local_prob']
                xly_model_log_prob[model_name + '_diff_prob'] = xly_model_log_prob[
                                                                    model_name + '_%s_prob' % environment] - \
                                                                xly_model_local_prob[model_name + '_local_prob']
                All_model_predict_data_diff_out_dict[model_name] = xly_model_log_prob
                xly_model_signal = (xly_model_local_prob >= thred_dict[model_name]).reindex(
                    xly_model_local_prob[xly_model_local_prob[model_name + '_local_prob'].notnull()].index)
                if 'Cla' in model_name and 'ZT' not in model_name:
                    total_cla_model_predict_result = pd.concat([total_cla_model_predict_result, xly_model_signal],
                                                               axis=1, sort=True)
                elif 'ZT' not in model_name:
                    total_reg_model_predict_result = pd.concat([total_reg_model_predict_result, xly_model_signal],
                                                               axis=1, sort=True)
                elif 'ZT' in model_name:
                    total_ZT_model_predict_result = pd.concat([total_ZT_model_predict_result, xly_model_signal], axis=1,
                                                              sort=True)


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



            prod_model = ['hml1RegFSV8XgbXlyModel', 'hml1RegFSV8XgbWjModel', 'hml0RegFSV8XgbWjModel',
                          'hml0RegFSV8XgbXlyModel', 'hml2RegFSV8XgbWjModel', 'hml2RegFSV8XgbXlyModel',
                          'totalRegXgbXbcModel', 'totalRegO2ulFSV8XgbXbcModel', \
                          'totalRegFSV8LrXlyModel', 'totalRegFSV8XgbWjModel']
            log_model = list(thred_dict.keys())
            log_model = ['Hml1XgbModel',
                        'Hml1XgbWjModel',
                        # 'ZTDjRegModel',
                        # 'ZTDjClaModel',
                        'Hml0XgbWjModel',
                        # 'ZTBysModel',
                        'Hml0XgbModel',
                        'Hml2XgbWjModel',
                        'Hml2XgbModel',
                        'TotalXgbXbcModel',
                        'TotalXgbXbcO2ulModel',
                        'TotalPMMLModel',
                        'TotalXgbWjModel']
            prod_proba1 = [x.split('Model')[0] + '_proba1' for x in prod_model]

            model_rename_dict = dict(zip(prod_model, log_model))
            model_proba_dict = dict(zip(log_model, prod_proba1))
            # log_proba1 = [x+'_probability' for x in log_model]
            pred_path = '/data/group/800463/wangj/model_signal/Jupiter/prod_v9/%s/%s_%s_jupiter_fac_20221220_daily_pred.csv' % (
            tradeDatestr, tradeDatestr, tradeDatestr)
            All_model_predict_data = pd.read_csv(open(pred_path)).set_index(['Ticker'])
            All_model_predict_data.rename(columns=model_rename_dict, inplace=True)
            #All_model_predict_data_diff_out_dict = {}
            for model_name in log_model:
                print(model_name)
                tmp_model_log_prob = inf_df[[model_name + '_probability']].rename(columns={model_name + '_probability': model_name + '_%s_prob' % environment})
                tmp_model_log_prob[model_name + '_local_prob'] = All_model_predict_data[model_proba_dict[model_name]]  # .reindex(tmp_model_log_prob.index)
                tmp_model_log_prob[model_name + '_diff_prob'] = tmp_model_log_prob[model_name + '_%s_prob' % environment] - tmp_model_log_prob[model_name + '_local_prob']
                All_model_predict_data_diff_out_dict[model_name] = tmp_model_log_prob
                tmp_model_signal = (tmp_model_log_prob[model_name + '_local_prob'] >= thred_dict[model_name]).reindex(All_model_predict_data.index)
                if 'Cla' in model_name:
                    total_cla_model_predict_result = pd.concat([total_cla_model_predict_result, tmp_model_signal], axis=1, sort=True)
                elif 'ZT' not in model_name:
                    total_reg_model_predict_result = pd.concat([total_reg_model_predict_result, tmp_model_signal], axis=1, sort=True)
                elif 'ZT' in model_name:
                    total_ZT_model_predict_result = pd.concat([total_ZT_model_predict_result, tmp_model_signal], axis=1, sort=True)

            #------------------------------总结df------------------------------------------------
            summary_dict = {}
            print('start summary')
            for model in list(All_model_predict_data_diff_out_dict.keys()):
                model_question_list = []
                # print(model)
                if (np.abs(All_model_predict_data_diff_out_dict[model][model + '_diff_prob']) > 1e-5).sum() > 0:
                    model_question_list.append('模型存在概率差异！！！最大绝对差异为%f' % np.abs(
                        All_model_predict_data_diff_out_dict[model][model + '_diff_prob']).max())
                else:
                    model_question_list.append('模型不存在概率差异~~~')

                summary_dict[model] = model_question_list

            # 生成本地投票结果
            reg_stacking = total_reg_model_predict_result.sum(axis=1)
            cla_stacking = total_cla_model_predict_result.sum(axis=1)
            def jupiter_voting1(reg_stacking,cla_stacking):
                condition1 = (reg_stacking + cla_stacking) >= 5
                condition2 = (cla_stacking==2) & (reg_stacking==2)
                condition3 = (cla_stacking==1) & (reg_stacking==4)
                condition4 = (cla_stacking==0) & (reg_stacking>=5)
                return (condition1 | condition2) & (condition3==False) & (condition4==False)
            def jupiter_voting(reg_stacking, cla_stacking):
                condition1 = reg_stacking >= 3

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

            ZT_predict = (total_ZT_model_predict_result.sum(axis = 1)>=2)
            ZT_predict_num = total_ZT_model_predict_result.sum(axis=1)
            local_predict.loc[ZT_predict[total_ZT_model_predict_result['ZTBysModel_local_prob'].notnull()].index,'本地投票结果'] = ZT_predict
            local_predict.loc[ZT_predict[total_ZT_model_predict_result['ZTBysModel_local_prob'].notnull()].index, '本地回归投票'] = ZT_predict_num-total_ZT_model_predict_result.filter(regex='Cla').sum(axis=1)
            local_predict.loc[ZT_predict[total_ZT_model_predict_result['ZTBysModel_local_prob'].notnull()].index,'本地分类投票'] = total_ZT_model_predict_result.filter(regex='Cla').sum(axis=1)

            excel_save_dict = dict()
            excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
            excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(total_reg_model_predict_result).join(total_cla_model_predict_result).join(total_ZT_model_predict_result)
            excel_save_dict['线上投票结果'] = local_predict.join(log_signal)

            for model_name in list(All_model_predict_data_diff_out_dict.keys()):
                # excel_save_dict[model_name+'_scaled因子差异'] = All_model_factor_diff_out_dict[model_name]
                excel_save_dict[model_name + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]
            check_dir('/data/group/800463/日内强势股/cpp_log_parse/模型差异/%s/'%tradeDatestr)
            excel_saver(excel_save_dict,'/data/group/800463/日内强势股/cpp_log_parse/模型差异/%s/模型差异_%s_%s.xlsx'%(tradeDatestr,tradeDatestr,environment))