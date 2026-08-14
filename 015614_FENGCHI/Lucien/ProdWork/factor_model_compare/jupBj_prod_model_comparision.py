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
from ProdWork.Param_config_data import thred_dict_jup_bjs_v1 as thred_dict

if __name__ == '__main__':
    print('===========jupBj_prod_model_comparision============')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
        # nowdate = '20250214'
    datelist = s.tradingday(nowdate, nowdate)

    for nowdate in datelist:
        tradeDatestr = s.tradingday(nowdate,-1)[0]
        yesDatestr = s.tradingday(tradeDatestr, -2)[0]

        from ProdWork.factor_model_compare.tools import gen_black_list
        filter_black_list, _, white_list = gen_black_list(nowdate)

        tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
        #tradeDate = '2023-03-24'
        print(tradeDate)
        if sys.argv[2:]:
            env_list = sys.argv[2:]
        else:
            env_list = ['prod']
            # env_list = ['test']
            # env_list = ['UAT']
        for environment in env_list:
            All_model_factor_diff_out_dict = {}
            All_model_predict_data_diff_out_dict = {}
            def check_dir(path):  # 路径生成函数
                if not os.path.exists(path):
                    os.makedirs(path)

            # ------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
            inf_df = pd.read_excel(
                '/data/group/800463/日内强势股/jupiterBj_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment), sheet_name='因子耗时')
            inf_df = inf_df.rename(columns={'Unnamed: 0': 'Ticker'}).set_index('Ticker')
            if len(inf_df) == 0: # 当天没有触发，不用对比
                check_dir('/data/group/800463/日内强势股/jupiterBj_log_parse/模型差异/%s/' % tradeDatestr)
                import shutil
                shutil.copyfile('/data/group/800463/日内强势股/jupiterBj_log_parse/模型差异/20250120/模型差异_20250120_prod.xlsx',
                                '/data/group/800463/日内强势股/jupiterBj_log_parse/模型差异/%s/模型差异_%s_%s.xlsx' % (tradeDatestr, tradeDatestr, environment))
                if environment == 'prod':
                    from dataApi.sendInfo import send_message
                    send_message(f'{nowdate} jupiterBj生成完毕，当天无触发')
                break

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

            prod_model = ['totalRegFSRSXgbZwhModel',
                          'totalRegFSCIXgbFcModel',
                          'totalRegSkkXgbSkkModel',
                          'totalRegFSV10XgbWjModel',
                          'totalRegFSV11XgbWjModel',
                          'totalRegFSCIXgbSkkModel']
            log_model = list(thred_dict.keys())
            log_model = ['totalRegFSRSXgbZwhModel',
                          'totalRegFSCIXgbFcModel',
                          'totalRegSkkXgbSkkModel',
                          'totalRegFSV10XgbWjModel',
                          'totalRegFSV11XgbWjModel',
                          'totalRegFSCIXgbSkkModel'
                        ]
            prod_proba1 = [x.split('Model')[0] + '_proba1' for x in prod_model]

            model_rename_dict = dict(zip(prod_model, log_model))
            model_proba_dict = dict(zip(log_model, prod_proba1))
            # log_proba1 = [x+'_probability' for x in log_model]
            pred_path = '/data/group/800463/wangj/model_signal/Jupiter/prod_bjs_v1/%s/%s_%s_jupiterN_fac_20241110_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
            import time
            while not os.path.exists(pred_path):
                print(f'缺失{pred_path}')
                time.sleep(60)
            All_model_predict_data = pd.read_csv(open(pred_path)).set_index(['Ticker'])
            All_model_predict_data.rename(columns=model_rename_dict, inplace=True)
            # 只筛选北交所样本
            All_model_predict_data = All_model_predict_data.loc[All_model_predict_data.index.map(lambda x: str(x).endswith('BJ'))]

            #All_model_predict_data_diff_out_dict = {}
            for model_name in log_model:
                print(model_name)
                tmp_model_log_prob = inf_df[[model_name + '_probability']].rename(columns={model_name + '_probability': model_name + '_%s_prob' % environment}).reindex(index=All_model_predict_data.index)
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

            # TODO: sss提供
            all_df = pd.read_pickle(f'/data/group/800463/project/project1_prod/right_v2412_BJ/daily_data/{nowdate}/all_factor_zt_merge_v2412_BJ_{nowdate}.pkl')
            md = IO.read_data([nowdate, nowdate], columns=['open'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND_BJ.h5')
            all_df['open_price'] = md['open']
            all_df['is_sample_jupiterBj'] = ((all_df['ZT_Time'] > 93000000) &
                                           (all_df['ZT_Time'] != 130000000) &
                                           (all_df['ZT_Time'] <= 143000000) &
                                           (all_df['open_is_zt'] == 0) &
                                           (all_df['T_o2pre'] >= -0.05) &
                                           (all_df['after_not_ul_len'] > 10) &
                                           (all_df['pre_close'] >= 2) &
                                           (all_df['last_is_zt'] == 0) &
                                           (all_df['min_is_dt'] == 0) &
                                           ((all_df['ul_price'] - all_df['open_price']).round(2) > 0.01))

            all_df = all_df.reset_index().set_index('Ticker')

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
                condition1 = reg_stacking >= 4  # jupiter_bjs_v1模型投票阈值
                return condition1

            local_predict = jupiter_voting(reg_stacking,cla_stacking)
            local_predict = pd.DataFrame(local_predict)
            local_predict.columns = ['本地投票结果']
            local_predict['本地回归投票'] = reg_stacking
            local_predict['本地分类投票'] = cla_stacking
            local_predict['是否在黑名单'] = 0
            local_predict['是否在白名单'] = 0
            sub_index = list(set(local_predict.index.tolist())&set(filter_black_list))
            local_predict.loc[sub_index,'是否在黑名单'] = 1
            sub_index = list(set(local_predict.index.tolist()) & set(white_list))
            local_predict.loc[sub_index, '是否在白名单'] = 1

            excel_save_dict = dict()
            excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
            excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(total_reg_model_predict_result).join(total_cla_model_predict_result).join(total_ZT_model_predict_result).join(all_df[['is_sample_jupiterBj']])
            excel_save_dict['线上投票结果'] = local_predict.join(log_signal)

            for model_name in list(All_model_predict_data_diff_out_dict.keys()):
                # excel_save_dict[model_name+'_scaled因子差异'] = All_model_factor_diff_out_dict[model_name]
                excel_save_dict[model_name.replace('totalRegp5_', '') + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]
            check_dir('/data/group/800463/日内强势股/jupiterBj_log_parse/模型差异/%s/'%tradeDatestr)

            excel_saver(excel_save_dict, '/data/group/800463/日内强势股/jupiterBj_log_parse/模型差异/%s/模型差异_%s_%s.xlsx' % (tradeDatestr,tradeDatestr,environment))
            if environment == 'prod':
                from dataApi.sendInfo import send_message
                send_message(f'{nowdate} jupiterBj生成完毕')