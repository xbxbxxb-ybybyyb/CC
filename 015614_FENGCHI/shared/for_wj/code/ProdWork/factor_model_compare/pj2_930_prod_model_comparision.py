'''
S0的模型对比：对比实盘和本地的信号差异

'''
import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
import re

from xquant.factordata import FactorData
import datetime as dt
s = FactorData()
import time
from ProdWork.CommonTools import excel_saver, ftp_download,ftp_upload
from ProdWork.Param_config_data import thred_dict_pj2_930 as thred_dict
if __name__ == '__main__':
    print('============pj2_930_prod_model_comparision==========')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
    tradeDatestr = s.tradingday(nowdate,-2)[0]

    tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
    print(tradeDate)
    if sys.argv[2:]:
        env_list = sys.argv[2:]
    else:
        env_list = ['prod','UAT','night']
    # for environment in environment_lst[:1]+environment_lst[2:4]: ## night
    # for environment in ['UAT_lite']: ## night
    for environment in env_list:
        print(environment)
        '''thred_dict = {'openPctHighDjClaModel':0.74,
                      'openPctHighWjClaModel':0.555,
                      'openPctLowDjClaModel':0.7,
                      'openPctLowWjClaModel':0.57,
                      'pat3XgbClaModel':0.5,
                      'pat4XgbClaModel':0.5,
                      'totalDjClaModel':0.64,
                      'totalWjClaModel':0.5609}'''
        #thred_dict = thred_dict_pj2_930

        model_rename_dict = {'openPctHighDjClaModel':'openPctHighDjClaModel',
                             'openPctHighWjClaModel': 'openPctHighWjClaModel',
                             'openPctLowDjClaModel': 'openPctLowDjClaModel',
                             'openPctLowWjClaModel': 'openPctLowWjClaModel',
                             'pat3XgbClaModel':'pat3XgbClaModel',
                             'pat4XgbClaModel':'pat4XgbClaModel',
                             'totalDjClaModel':'totalDjClaModel',
                             'totalWjClaModel':'totalWjClaModel'}


        def check_dir(path):  # 路径生成函数
            if not os.path.exists(path):
                os.makedirs(path)



        All_model_predict_data_diff_out_dict = {}

        #------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
        inf_df = pd.read_excel( '/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_%s.xlsx'%(tradeDate, environment),sheetname = '项目二930样本')
        inf_df = inf_df.rename(columns = {'Unnamed: 0':'Ticker'}).set_index('Ticker')
        inf_df = inf_df.loc[~inf_df.index.duplicated(keep='first')].sort_index()
        #UAT中的信号
        log_signal = inf_df[['p2shouldBuySignal']].rename(columns = {'p2shouldBuySignal':environment+'_signal'})

        total_model_list = list(map(lambda x:x[:~11],np.array(inf_df.columns)[np.array(list(map(lambda x:'probability' in x ,list(inf_df.columns))))]))
        total_cla_model_predict_result = pd.DataFrame()
        total_reg_model_predict_result = pd.DataFrame()
        for model_name in thred_dict.keys():
            if model_name+'_probability' not in inf_df.columns:
                inf_df[model_name+'_probability'] = np.nan
        Log_triggered_samples = inf_df.index
        #------------------------------核对王敬的模型--------------------------------------
        WJ_model_name_all = ['openPctHighWjClaModel', 'openPctLowWjClaModel', 'totalWjClaModel']
        WJ_model_rename_dict = {'openPctHighWjClaModel':'highopenClaModel',
                                'openPctLowWjClaModel':'lowopenClaModel',
                                'totalWjClaModel':'allClaModel'}
        for WJ_model_name in WJ_model_name_all:
            print(WJ_model_name)
            #wj_new_models_path = '/data/user/013550/wjworkspace/Saturn_930_scene/DataPrediction/Daily_result/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Saturn/S0/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            # 核对模型的预测数据
            Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
            csv_name = np.array(Predict_file_csvs)[np.array(list(map(lambda x:'v2' not in x,Predict_file_csvs)))][0]
            try:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
            except:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            if WJ_model_name == 'totalWjClaModel':
                # 在这里计算公共样本偏差
                Local_triggered_samples = WJ_model_local_prob['Ticker']
                Local_sample_missing = list(set(Log_triggered_samples).difference(set(WJ_model_local_prob['Ticker'])))
                Log_sample_missing = list(set(WJ_model_local_prob['Ticker']).difference(set(Log_triggered_samples)))
            # WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).reindex(Log_triggered_samples).rename(columns={'probability': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]/100
            WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).rename(columns={'probability': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]/100
            WJ_model_log_prob = inf_df[[WJ_model_name+'_probability']].rename(columns = {WJ_model_name+'_probability':WJ_model_name+'_%s_prob'%environment})
            WJ_model_log_prob[WJ_model_name+'_local_prob'] = WJ_model_local_prob[WJ_model_name+'_local_prob']
            WJ_model_log_prob[WJ_model_name+'_diff_prob'] = WJ_model_log_prob[WJ_model_name+'_%s_prob'%environment]-WJ_model_local_prob[WJ_model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[WJ_model_name] = WJ_model_log_prob
            if 'Cla' in WJ_model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,WJ_model_local_prob.dropna()>=thred_dict[WJ_model_name]],axis = 1)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,WJ_model_local_prob.dropna()>=thred_dict[WJ_model_name]],axis = 1)
        #------------------------------核对董坚的模型--------------------------------------
        DJ_model_name_all = ['openPctHighDjClaModel','openPctLowDjClaModel','totalDjClaModel']
        DJ_model_rename_dict = {'openPctHighDjClaModel':'930_openpct_high_v2',
                                'openPctLowDjClaModel':'930_openpct_low_v2',
                                'totalDjClaModel':'930_cla_v2'}
        for DJ_model_name in DJ_model_name_all:
            print(DJ_model_name)
            # 核对模型的预测数据
            DJ_model_local_prob = pd.read_hdf('/data/group/800463/dongj/model_signal/saturn/model_output_everyday/%s_%s/pred_prob.h5'%(tradeDatestr,DJ_model_rename_dict[DJ_model_name]))
            # DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(columns = {'pred_prob':DJ_model_name+'_local_prob'})\
            #         .reindex(Log_triggered_samples)
            DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(columns = {'pred_prob':DJ_model_name+'_local_prob'})
            DJ_model_log_prob = inf_df[[DJ_model_name+'_probability']].rename(columns = {DJ_model_name+'_probability':DJ_model_name+'_%s_prob'%environment})
            DJ_model_log_prob[DJ_model_name+'_local_prob'] = DJ_model_local_prob[DJ_model_name+'_local_prob']
            DJ_model_log_prob[DJ_model_name+'_diff_prob'] = DJ_model_log_prob[DJ_model_name+'_%s_prob'%environment]-DJ_model_local_prob[DJ_model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[DJ_model_name] = DJ_model_log_prob
            DJ_model_signal = (DJ_model_local_prob >= thred_dict[DJ_model_name]).reindex(
                DJ_model_local_prob[DJ_model_local_prob[DJ_model_name+'_local_prob'].notnull()].index)
            if 'Cla' in DJ_model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,DJ_model_local_prob>=thred_dict[DJ_model_name]],axis = 1)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,DJ_model_local_prob>=thred_dict[DJ_model_name]],axis = 1)
        #------------------------------核对谢璐遥的模型--------------------------------------
        XLY_model_name = ['pat3XgbClaModel','pat4XgbClaModel']
        for model_name in XLY_model_name:
            print(model_name)
            # 核对模型的预测数据
            # xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal/%s_saturn_930/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1)\
            #         .set_index('Ticker').reindex(Log_triggered_samples).rename(columns = {model_name+'_proba':model_name+'_local_prob'})[[model_name+'_local_prob']]
            xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal/%s_saturn_930/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1)\
                    .set_index('Ticker').rename(columns = {model_name+'_proba':model_name+'_local_prob'})[[model_name+'_local_prob']]
            xly_model_log_prob = inf_df[[model_name+'_probability']].rename(columns = {model_name+'_probability':model_name+'_%s_prob'%environment})
            xly_model_log_prob[model_name+'_local_prob'] = xly_model_local_prob[model_name+'_local_prob']
            xly_model_log_prob[model_name+'_diff_prob'] = xly_model_log_prob[model_name+'_%s_prob'%environment]-xly_model_local_prob[model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[model_name] = xly_model_log_prob
            xly_model_signal = (xly_model_local_prob >= thred_dict[model_name]).reindex(
                xly_model_local_prob[xly_model_local_prob[model_name+'_local_prob'].notnull()].index)
            if 'Cla' in model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,xly_model_signal],axis = 1,sort = True)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,xly_model_signal],axis = 1,sort = True)

        #------------------------------总结df------------------------------------------------
        summary_dict = {}
        for model in total_model_list:
            # model = total_model_list[0]
            model_question_list = []
            if (np.abs(All_model_predict_data_diff_out_dict[model][model+'_diff_prob'])>1e-5).sum()>0:
                model_question_list.append('模型存在概率差异！！！最大绝对差异为%f'%np.abs(All_model_predict_data_diff_out_dict[model][model+'_diff_prob']).max())
            else:
                model_question_list.append('模型不存在概率差异~~~')
            summary_dict[model] = model_question_list

        # 对样本进行判断和对分场景进行切分
        param = pd.read_pickle('/data/group/800463/project/project2_prod/everyday_Param_v2/%s/pj2_v0311_param_rename_%s_after_closed.pkl'%(tradeDatestr,tradeDatestr))
        param['is_sample_930'] = ((param['saturn_T_day_first_ZT_Time'] <= 93000000) == False) & (param['saturn_lzt_day_pattern']>=3) &\
                                 (param['saturn_T_o2pre'] <= 0.08) & (param['saturn_T_o2pre']>= -0.01) &\
                                 (param['saturn_T_open_is_zt'] == 0) & (param['saturn_T_open_is_dt'] == 0)
        param = param.reset_index().set_index('Ticker')
        # 对样本进行reindex，其他的填充为nan
        total_cla_model_predict_result.index.name = 'Ticker'
        total_cla_model_predict_result = total_cla_model_predict_result.reindex(param.index)

        open_pct_high_model = ['openPctHighDjClaModel','openPctHighWjClaModel']
        open_pct_low_model = ['openPctLowDjClaModel','openPctLowWjClaModel']
        pat3_model = ['pat3XgbClaModel']
        pat4_model = ['pat4XgbClaModel']
        scene_thred_dict = {'saturn_T_o2pre':0,
                            'saturn_lzt_day_pattern':4}
        for model_name in open_pct_high_model:
            if 'Cla' in model_name: total_cla_model_predict_result[param['saturn_T_o2pre']<scene_thred_dict['saturn_T_o2pre']][model_name] = np.nan
            else: total_reg_model_predict_result[param['saturn_T_o2pre']<scene_thred_dict['saturn_T_o2pre']][model_name] = np.nan
        for model_name in open_pct_low_model:
            if 'Cla' in model_name: total_cla_model_predict_result[param['saturn_T_o2pre']>=scene_thred_dict['saturn_T_o2pre']][model_name] = np.nan
            else: total_reg_model_predict_result[param['saturn_T_o2pre']>=scene_thred_dict['saturn_T_o2pre']][model_name] = np.nan
        for model_name in pat3_model:
            if 'Cla' in model_name: total_cla_model_predict_result[param['saturn_lzt_day_pattern']==4][model_name] = np.nan
            else: total_reg_model_predict_result[param['saturn_lzt_day_pattern']==4][model_name] = np.nan
        for model_name in pat4_model:
            if 'Cla' in model_name: total_cla_model_predict_result[param['saturn_lzt_day_pattern']==3][model_name] = np.nan
            else: total_reg_model_predict_result[param['saturn_lzt_day_pattern']==3][model_name] = np.nan

        # 生成本地投票结果
        reg_stacking = total_reg_model_predict_result.sum(axis = 1)
        cla_stacking = total_cla_model_predict_result.sum(axis = 1)
        local_predict = cla_stacking >= 3

        local_predict = pd.DataFrame(local_predict)
        local_predict.columns = ['本地投票结果']

        excel_save_dict = {}
        excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
        excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(param[['is_sample_930']]).join(total_cla_model_predict_result)

        for model_name in total_model_list:
            excel_save_dict[model_rename_dict[model_name] + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]

        check_dir('/data/group/800463/日内强势股/log_parse/模型差异/%s'%tradeDatestr)
        excel_saver(excel_save_dict,'/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_%s_pj2_930.xlsx'%(tradeDatestr,tradeDatestr,environment))



