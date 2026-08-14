import os
import sys

sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from dataApi.stockList import trans_int2windcode
import datetime as dt
s = FactorData()
from ProdWork.CommonTools import excel_saver
from ProdWork.Param_config_data import thred_dict_jup001_v3 as thred_dict   # TODO: import 最新的
if __name__ == '__main__':
    print('===========jup001_prod_model_comparision=============')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
        # nowdate = '20241015'
    # datelist = s.tradingday('20240603','20240618')
    datelist = s.tradingday(nowdate, nowdate)
    for nowdate in datelist:
        tradeDatestr = s.tradingday(nowdate,-1)[0]

        from ProdWork.factor_model_compare.tools import gen_black_list
        filter_black_list, _, white_list = gen_black_list(nowdate)

        tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
        print(tradeDate)

        if sys.argv[2:]:
            env_list = sys.argv[2:]
        else:
            env_list = ['prod', 'UAT']
            # env_list = ['test']
            # env_list = ['night']
            # env_list = ['UAT']
        for environment in env_list:
            All_model_factor_diff_out_dict = {}
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
                    this_factor_diff = (local_factor_data[[factor]] - log_factor_data[[factor]]).rename(columns={factor: 'diff'})
                    this_factor_diff = this_factor_diff.join(local_factor_data[[factor]].rename(columns={factor: 'local'})).join(log_factor_data[[factor]].rename(columns={factor: environment}))
                    this_factor_diff['Factor'] = factor
                    factor_diff_samples = this_factor_diff[np.abs(this_factor_diff['diff']) > 1e-8].reset_index().set_index(['Factor', 'Ticker'])
                    total_factor_diff = pd.concat([total_factor_diff, factor_diff_samples])
                return total_factor_diff

            # ------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
            inf_df = pd.read_excel(f'/data/group/800463/日内强势股/cpp_log_parse/因子耗时/因子耗时_{tradeDate}_{environment}.xlsx', sheet_name='因子耗时New')
            inf_df = inf_df.rename(columns={'Unnamed: 0': 'Ticker'}).set_index('Ticker')
            for model_name in thred_dict.keys():
                if model_name + '_probability' not in inf_df.columns:
                    inf_df[model_name + '_probability'] = np.nan

            log_signal = inf_df[['shouldBuySignal', 'sum_signals']].rename(columns={'shouldBuySignal': environment+'_signal',
                                                                                    'sum_signals': environment+'_sum_signals'})
            total_model_list = list(map(lambda x:x[:~11], np.array(inf_df.columns)[np.array(list(map(lambda x:'probability' in x, list(inf_df.columns))))]))
            total_cla_model_predict_result = pd.DataFrame()
            total_reg_model_predict_result = pd.DataFrame()
            total_ZT_model_predict_result = pd.DataFrame()
            for model_name in thred_dict.keys():
                if model_name+'_probability' not in inf_df.columns:
                    inf_df[model_name+'_probability'] = np.nan

            # TODO:本地与实盘的模型命名dict 对应关系
            prod_model = ['totalRegO2ulFSV8XgbXbcModel',
                            'totalRegXgbFSV8WjModel',
                            'hml0RegFSV8LrXbcModel','hml1RegFSV8LrXbcModel','hml2RegFSV8LrXbcModel',
                            'hml0RegFSV8XgbWjModel','hml1RegFSV8XgbWjModel','hml2RegFSV8XgbWjModel',
                            'totalRegFSRSXgbSkkModel',
                            'totalRegFSV10LrXbcModel']
            log_model = list(thred_dict.keys())
            log_model = ['TotalXgbO2ulXbcModel','TotalXgbWjModel','Hml0PMMLXbcModel','Hml1PMMLXbcModel','Hml2PMMLXbcModel',\
                         'Hml0XgbWjModel', 'Hml1XgbWjModel',  'Hml2XgbWjModel',\
                         'totalXgbSkkModel', 'TotalPMMLXbcModel']
            prod_proba1 = [x.split('Model')[0] +'_proba1' for x in prod_model]

            model_rename_dict = dict(zip(prod_model, log_model))
            model_proba_dict = dict(zip(log_model, prod_proba1))

            #TODO: wj提供，本地模型路径
            pred_path = '/data/group/800463/wangj/model_signal/Jupiter001/prod_v3/%s/%s_%s_europa_fac_20230329_daily_pred.csv'%(tradeDatestr, tradeDatestr, tradeDatestr)
            import time
            while not os.path.exists(pred_path):
                print(f'缺失{pred_path}')
                time.sleep(60)
            All_model_predict_data = pd.read_csv(open(pred_path)).set_index(['Ticker'])
            All_model_predict_data.rename(columns = model_rename_dict, inplace = True)
            inf_df = inf_df.loc[list(set(inf_df.index.tolist())&set(All_model_predict_data.index.tolist()))].sort_index()
            All_model_predict_data_diff_out_dict = {}
            for model_name in log_model:
                tmp_model_log_prob = inf_df[[model_name + '_probability']].rename(columns={model_name + '_probability': model_name + '_%s_prob' % environment}).reindex(index=All_model_predict_data.index)
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

            #------------------------------总结df------------------------------------------------
            summary_dict = {}
            print('start summary')
            for model in log_model:
                model_question_list = []
                if (np.abs(All_model_predict_data_diff_out_dict[model][model+'_diff_prob'])>1e-5).sum()>0:
                    model_question_list.append('模型存在概率差异！！！最大绝对差异为%f'%np.abs(All_model_predict_data_diff_out_dict[model][model+'_diff_prob']).max())
                else:
                    model_question_list.append('模型不存在概率差异~~~')
                summary_dict[model] = model_question_list

            # TODO: sss提供
            param = pd.read_pickle(f'/data/group/800463/project/project1_prod/right_v2304_kcb/daily_data/{nowdate}_europa/all_factor_zt_merge_v2304_with_kcb_{nowdate}_europa.pkl')
            param['zcz'] = param.reset_index()['Ticker'].apply(lambda x: x[0] == '3' or x[:2] == '68').values
            param['ul_ban'] = param['after_not_ul_len'] <= 10
            param.loc[param[param['zcz']].index, 'ul_ban'] = (param['list_len'] <= 15).reindex(param[param['zcz']].index)
            param['is_sample_europa'] = ((param['high_price'] < param['trigger_price']) &
                         (param['open_is_zt'] == False) &
                         (param['T_o2pre'] >= -0.05) &
                         (param['ul_ban'] == False) &
                         (param['last_is_zt'] == 0) &
                         (param['pre_close'] >= 2) &
                         (param['ZT_Time'] <= 143000000) &
                         (param['ZT_Time'] > 93000000) &
                         (param['last_buy_rise'] <= 0.025))

            # 生成本地投票结果
            reg_stacking = total_reg_model_predict_result.sum(axis = 1)
            cla_stacking = total_cla_model_predict_result.sum(axis = 1)

            def jupiter_voting(reg_stacking):
                condition1 = reg_stacking >= 4
                return condition1

            local_predict = jupiter_voting(reg_stacking)
            local_predict = pd.DataFrame(local_predict)
            local_predict.columns = ['本地投票结果']
            local_predict['本地回归投票'] = reg_stacking
            local_predict['本地分类投票'] = cla_stacking
            local_predict['是否在黑名单'] = 0
            local_predict['是否在白名单'] = 0
            sub_index = list(set(local_predict.index.tolist()) & set(list(map(lambda x: trans_int2windcode(x), filter_black_list))))
            local_predict.loc[sub_index, '是否在黑名单'] = 1
            sub_index = list(set(local_predict.index.tolist()) & set(list(map(lambda x: trans_int2windcode(x), white_list))))
            local_predict.loc[sub_index, '是否在白名单'] = 1

            excel_save_dict = dict()
            excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
            excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(total_reg_model_predict_result).join(total_cla_model_predict_result).join(total_ZT_model_predict_result).join(param[['is_sample_europa']])
            excel_save_dict['线上投票结果'] = local_predict.join(log_signal)

            for model_name in prod_model:
                excel_save_dict[model_rename_dict[model_name] + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_rename_dict[model_name]]
            os.makedirs(f'/data/group/800463/日内强势股/cpp_log_parse/模型差异/{tradeDatestr}/', exist_ok=True)
            excel_saver(excel_save_dict, f'/data/group/800463/日内强势股/cpp_log_parse/模型差异/{tradeDatestr}/模型差异New_{tradeDatestr}_{environment}.xlsx')
            if environment == 'prod':
                from dataApi.sendInfo import send_message
                send_message(f'{nowdate} europa生成完毕')

