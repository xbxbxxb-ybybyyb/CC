
'''
S1每日模型信号差异
'''
import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
import os
import re
from xquant.factordata import FactorData
import datetime as dt
s = FactorData()
import time
from ProdWork.CommonTools import excel_saver, ftp_download,ftp_upload
from ProdWork.Param_config_data import thred_dict_pj3_931_v3 as thred_dict
from ProdWork.Param_config_data import thred_pj3_vote_num_v3 as thred_vote
if __name__ == '__main__':
    print('===========pj3_s1_prod_model_comparision============')
    #Year = '2021'
    #Month = '12'
    #Day = '20'
    # date = Year + Month + Day
    # date_hyphen = '%s-%s-%s' % (Year, Month, Day)
    # environment = 'night'
    # nowdate = dt.datetime.now().strftime('%Y%m%d')
    # nowdate='20210827'
    # tradeDatestr = s.tradingday(nowdate,-2)[0]
    #tradeDatestr = Year + Month + Day
    if sys.argv[1]:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
    tradeDatestr = s.tradingday(nowdate, -2)[0]
    tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
    #tradeDate = '2022-05-25'
    print(tradeDate)
    '''nowdate = dt.datetime.now().strftime('%Y%m%d')
    nowdate = '20211116'
    tradeDatestr = s.tradingday(nowdate,-2)[0]
    tradeDate = pd.Timestamp(tradeDatestr).strftime('%Y-%m-%d')
    print(tradeDate)'''
    if sys.argv[2:]:
        env_list = sys.argv[2:]
    else:
        env_list = ['prod','UAT','SZEX','SHEX','UAT_lite','UAT_other']
    for environment in env_list:#['UAT']:#sel_environment[:2]+sel_environment[4:]: # ['night']:#
        print(environment)


        model_rename_dict = {
            'ceres931O2ulHighClaDjModel':'highOuClaDjModel',
            'ceres931Pct5HighClaDjModel': 'highPct5ClaDjModel',
             'ceres931Pct5HighClaWjModel':'highPct5ClaPMMLModel',
             'ceres931Pct5HighDjModel':'highPct5DjModel',
            'ceres931O2ulLowClaDjModel': 'lowOuClaDjModel',
             'ceres931Pct5LowClaDjModel':'lowPct5ClaDjModel',
             'ceres931Pct5LowClaWjModel':'lowPct5ClaPMMLModel',
            'ceres931Pct5LowDjModel': 'lowPct5DjModel',
            'ceres931t1PctHighXlyModel': 't1PctHighXgbModel',
            'ceres931t1PctLowXlyModel': 't1PctLowXgbModel',
             'ceres931TotalDjModel' :'totalDjModel'
        }

        def check_dir(path):  # 路径生成函数
            if not os.path.exists(path):
                os.makedirs(path)

        All_model_predict_data_diff_out_dict = {}

        #------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
        inf_df = pd.read_excel( '/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_%s.xlsx'%(tradeDate, environment),sheetname = 'Ceres931样本')
        inf_df = inf_df.rename(columns = {'Unnamed: 0':'Ticker'}).set_index('Ticker')
        ind_modelcols = ['%s_probability'%x for x in list(model_rename_dict.values())]#inf_df.filter(regex='_probability').columns.tolist()
        ind_modelcols_change = ['%s_probability'%x for x in list(model_rename_dict.keys())]#['ceres931%s'%x for x in ind_modelcols]
        rename_dict = dict(zip(ind_modelcols,ind_modelcols_change))
        inf_df.rename(columns = rename_dict,inplace=True)
        inf_df = inf_df.loc[~inf_df.index.duplicated(keep='first')].sort_index()
        #UAT中的信号
        log_signal = inf_df[['p3shouldBuySignal','sum_signals']].rename(columns = {'p3shouldBuySignal':environment+'_signal','sum_signals':'%s_sum_signals'%environment})

        total_model_list = list(map(lambda x:x[:~11],np.array(inf_df.columns)[np.array(list(map(lambda x:'probability' in x ,list(inf_df.columns))))]))
        total_cla_model_predict_result = pd.DataFrame()
        total_reg_model_predict_result = pd.DataFrame()
        '''for model_name in thred_dict.keys():
            if model_name+'_probability' not in inf_df.columns:
                print('因子耗时中缺少模型信号%s！！！！！'%model_name)
                inf_df[model_name+'_probability'] = np.nan'''
        Log_triggered_samples = inf_df.index
        #------------------------------核对董坚的模型--------------------------------------

        DJ_model_rename_dict = {'ceres931cbMoreDjModel':'SP2_931_cbmore_reg_v1',
                                'ceres931cbOneDjModel':'SP2_931_cbone_reg_v1',
                                'ceres931Pct5HighDjModel':'SP2_931_open5high_reg_v1',
                                'ceres931Pct5LowDjModel':'SP2_931_open5low_reg_v1',
                                'ceres931TotalDjModel':'SP2_931_reg_v1',
                                'ceres931totalOpenDjModel':'SP2_931_reg_o_v1',
                                }
        DJ_model_rename_dict = {
                                'ceres931Pct5HighDjModel': 'SP2_931_open5high_reg_v1',
                                'ceres931Pct5LowDjModel': 'SP2_931_open5low_reg_v1',
                                'ceres931Pct5HighClaDjModel': 'SP2_931_open5high_cla',
                                'ceres931Pct5LowClaDjModel': 'SP2_931_open5low_cla',
                                'ceres931TotalDjModel': 'SP2_931_reg_v1',
                                'ceres931O2ulHighClaDjModel': 'SP2_931_o2ulhigh_cla',
                                'ceres931O2ulLowClaDjModel': 'SP2_931_o2ullow_cla',
                                }

        for DJ_model_name in list(DJ_model_rename_dict.keys()):
            print(DJ_model_name)
            # 核对模型的预测数据
            #DJ_model_local_prob = pd.read_hdf('/data/group/800463/dongj/model_signal/ceres/temp/%s_%s/pred_prob.h5'%(tradeDatestr,DJ_model_rename_dict[DJ_model_name]))
            if os.path.exists('/data/group/800463/dongj/model_signal/ceres/v3/model_output_everyday/%s_%s/pred_prob.h5' % (
                tradeDatestr, DJ_model_rename_dict[DJ_model_name])):
                DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/ceres/v3/model_output_everyday/%s_%s/pred_prob.h5' % (
                tradeDatestr, DJ_model_rename_dict[DJ_model_name]))

            # DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(columns = {'pred_prob':DJ_model_name+'_local_prob'})\
            #         .reindex(Log_triggered_samples)
                DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(columns = {'pred_prob':DJ_model_name+'_local_prob'})
            else:
                DJ_model_local_prob = pd.DataFrame(columns = [DJ_model_name+'_local_prob'])
            if DJ_model_name+'_probability' not in inf_df.columns.tolist():
                inf_df[DJ_model_name+'_probability'] = np.nan
            DJ_model_log_prob = inf_df[[DJ_model_name + '_probability']].rename(columns={DJ_model_name + '_probability': DJ_model_name + '_%s_prob' % environment})
            DJ_model_log_prob[DJ_model_name+'_local_prob'] = DJ_model_local_prob.loc[DJ_model_log_prob[~DJ_model_log_prob[DJ_model_name+'_%s_prob'%environment].isna()].index].reindex(DJ_model_log_prob.index)[DJ_model_name+'_local_prob']#
            DJ_model_log_prob[DJ_model_name+'_diff_prob'] = DJ_model_log_prob[DJ_model_name+'_%s_prob'%environment]-DJ_model_local_prob[DJ_model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[DJ_model_name] = DJ_model_log_prob
            # DJ_model_signal = (DJ_model_local_prob >= thred_dict[DJ_model_name]).reindex(
            #     DJ_model_local_prob[DJ_model_local_prob[DJ_model_name+'_local_prob'].notnull()].index)
            if 'Cla' in DJ_model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,DJ_model_local_prob>=thred_dict[model_rename_dict[DJ_model_name]]],axis = 1)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,DJ_model_local_prob>=thred_dict[model_rename_dict[DJ_model_name]]],axis = 1)
        #------------------------------核对王敬的模型--------------------------------------

        WJ_model_rename_dict = {'ceres931Pct5HighWjModel':'Highpct5wjModel',
                                'ceres931Pct5LowWjModel':'Lowpct5wjModel',
                                #'ceres931TotalWjModel':'allregwjModel',
                                'ceres931OpenOthWjModel': 'OthopenwjModel',
                                'ceres931OpenMedWjModel': 'MedopenwjModel',
                                }
        WJ_model_rename_dict = {'ceres931Pct5HighClaWjModel': 'Highpct5ClawjModel',
                                'ceres931Pct5LowClaWjModel': 'Lowpct5ClawjModel',
                                # 'ceres931TotalWjModel':'allregwjModel',
                               # 'ceres931OpenOthWjModel': 'OthopenwjModel',
                                #'ceres931OpenMedWjModel': 'MedopenwjModel',
                                }
        for WJ_model_name in list(WJ_model_rename_dict.keys()):
            # WJ_model_name = 'RollLgbClaModel'
            print(WJ_model_name)

            wj_new_models_path = '/data/group/800463/wangj/model_signal/Ceres/S1/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            #wj_new_models_path ='/data/user/013550/wjworkspace/Ceres_S1_v3new/rrrout/DataPrediction/Daily_result/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            # 核对模型的预测数据
            Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
            csv_name = np.array(Predict_file_csvs)[np.array(list(map(lambda x: '%s~%s'%(tradeDatestr,tradeDatestr) in x, Predict_file_csvs)))][0]
            try:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
            except:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            if WJ_model_name == 'ceres931TotalWjModel':
                # 在这里计算公共样本偏差
                Local_triggered_samples = WJ_model_local_prob['Ticker']
                Local_sample_missing = list(set(Log_triggered_samples).difference(set(WJ_model_local_prob['Ticker'])))
                Log_sample_missing = list(set(WJ_model_local_prob['Ticker']).difference(set(Log_triggered_samples)))
            # WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).reindex(Log_triggered_samples).rename(columns={'pred_Reg': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]
            if len(WJ_model_local_prob)>0:
                WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).rename(columns={'probability': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]/100
            else:
                WJ_model_local_prob = pd.DataFrame(columns=[ 'prediction',WJ_model_name + '_local_prob'])
            if WJ_model_name+'_probability' not in inf_df.columns.tolist():
                inf_df[WJ_model_name+'_probability'] = np.nan
            WJ_model_log_prob = inf_df[[WJ_model_name+'_probability']].rename(columns = {WJ_model_name+'_probability':WJ_model_name+'_%s_prob'%environment})
            WJ_model_log_prob[WJ_model_name+'_local_prob'] = WJ_model_local_prob.loc[WJ_model_log_prob[~WJ_model_log_prob[WJ_model_name+'_%s_prob'%environment].isna()].index].reindex(WJ_model_log_prob.index)[WJ_model_name+'_local_prob']#WJ_model_local_prob[WJ_model_name+'_local_prob']
            WJ_model_log_prob[WJ_model_name+'_diff_prob'] = WJ_model_log_prob[WJ_model_name+'_%s_prob'%environment]-WJ_model_local_prob[WJ_model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[WJ_model_name] = WJ_model_log_prob
            if 'Cla' in WJ_model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,WJ_model_local_prob.dropna()>=thred_dict[model_rename_dict[WJ_model_name]]],axis = 1)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,WJ_model_local_prob.dropna()>=thred_dict[model_rename_dict[WJ_model_name]]],axis = 1)
        #------------------------------核对谢璐遥的模型--------------------------------------
        XLY_model_name = ['ceres931inTimeXlyModel','ceres931outTimeXlyModel','ceres931totalXlyModel',
                          'ceres931t1PctHighXlyModel','ceres931t1PctLowXlyModel','ceres931ulLongXlyModel','ceres931ulShortXlyModel']
        XLY_model_name = [ 'ceres931totalXlyModel',
                          'ceres931t1PctHighXlyModel', 'ceres931t1PctLowXlyModel', 'ceres931ulLongXlyModel',
                          'ceres931ulShortXlyModel']
        XLY_model_name = ['ceres931t1PctHighXlyModel', 'ceres931t1PctLowXlyModel' ]

        for model_name in XLY_model_name:
            print(model_name)
            # 核对模型的预测数据
            # xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal/%s_ceres_931/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1)\
            #         .set_index('Ticker').reindex(Log_triggered_samples).rename(columns = {model_name+'_proba':model_name+'_local_prob'})[[model_name+'_local_prob']]
            #xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal_v2/%s_ceres_931/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1).set_index('Ticker').rename(columns = {model_rename_dict[model_name]+'_proba':model_name+'_local_prob'})[[model_name+'_local_prob']]
            xly_model_local_prob = pd.read_pickle(
                '/data/group/800463/xiely/model_signal/%s_ceres_931_v3/model_predict.pkl' % tradeDatestr).reset_index().drop(
                ['dt'], axis=1) \
                .set_index('Ticker').rename(
                columns={model_rename_dict[model_name] + '_proba': model_name + '_local_prob'})[
                [model_name + '_local_prob']]
            if model_name+'_probability' not in inf_df.columns.tolist():
                print('%s no prediction'%model_name)
                xly_model_log_prob = pd.DataFrame(inf_df.index,columns =[model_name+'_%s_prob'%environment]).fillna(0)
            else:
                xly_model_log_prob = inf_df[[model_name+'_probability']].rename(columns = {model_name+'_probability':model_name+'_%s_prob'%environment})
            xly_model_log_prob[model_name+'_local_prob'] = xly_model_local_prob.loc[xly_model_log_prob[~xly_model_log_prob[model_name+'_%s_prob'%environment].isna()].index].reindex(xly_model_log_prob.index)[model_name+'_local_prob']
            xly_model_log_prob[model_name+'_diff_prob'] = xly_model_log_prob[model_name+'_%s_prob'%environment]-xly_model_local_prob[model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[model_name] = xly_model_log_prob
            xly_model_signal = (xly_model_local_prob >= thred_dict[model_rename_dict[model_name]]).reindex(
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
        param = pd.read_pickle(
            '/data/group/800463/project/project3_prod/daily_data/%s_v3/ceres_factor_v3_%s.pkl' % (
                str(tradeDatestr), str(tradeDatestr)))#pd.read_pickle('/data/group/800463/project/project3_prod/daily_data/%s/ceres_factor_v0902_%s.pkl'%(tradeDatestr,tradeDatestr))
        #param['is_sample_931'] = ((param['ceres_T_day_first_ZT_Time'] <= 93100000) == False) & (param['ceres_lzt_day_pattern']>=3) &(param['ceres_T_open_is_zt'] == 0) & (param['ceres_T_open_is_dt'] == 0)
        param = param.reset_index().set_index('Ticker')
        # 对样本进行reindex，其他的填充为nan
        total_reg_model_predict_result.index.name = 'Ticker'
        total_cla_model_predict_result.index.name = 'Ticker'
        total_reg_model_predict_result = total_reg_model_predict_result.reindex(param.index)
        total_cla_model_predict_result = total_cla_model_predict_result.reindex(param.index)
        '''open_pct_high_model = ['ceres931OpenPctHighDjModel','ceres931OpenPctHighWjModel']
        open_pct_low_model = ['ceres931OpenPctLowDjModel','ceres931OpenPctLowWjModel']
        pat3_model = ['ceres931Pat3DjModel','ceres931Pat3XgbModel']
        pat4_model = ['ceres931Pat4DjModel','ceres931Pat4XgbModel']
        ret2o_high_model = ['ceres931Ret2oHighDjModel','ceres931Ret2oHighPMMLModel']
        ret2o_low_model = ['ceres931Ret2oLowDjModel','ceres931Ret2oLowPMMLModel']
        pct5_high_model = ['ceres931Pct5HighWjModel']
        pct5_low_model = ['ceres931Pct5LowWjModel']
        scene_thred_dict = {'ceres_T_o2pre':0,
                            'ceres_lzt_day_pattern':4,
                            'ceres_pj2r_931_ret2o':0,
                            'saturn_EFS_pct5_T1':0.1190024}
        # 顺序与下方对应
        model_scene_mother_list = [open_pct_high_model,open_pct_low_model,pat3_model,pat4_model,
                                   ret2o_high_model,ret2o_low_model,pct5_high_model,pct5_low_model]
        model_scene_dis_list = ['ceres_T_o2pre','ceres_T_o2pre','ceres_lzt_day_pattern','ceres_lzt_day_pattern',
                                'ceres_pj2r_931_ret2o','ceres_pj2r_931_ret2o','ceres_EFS_pct5_T1','ceres_EFS_pct5_T1']
        for i in range(len(model_scene_mother_list)):
            mother_list = model_scene_mother_list[i]
            for model_name in mother_list:
                if 'Cla' in model_name:
                    if 'High' in model_name:
                        total_cla_model_predict_result[param[model_scene_dis_list[i]]<scene_thred_dict[model_scene_dis_list[i]]][model_name] = np.nan
                    elif 'Low' in model_name:
                        total_cla_model_predict_result[param[model_scene_dis_list[i]]>=scene_thred_dict[model_scene_dis_list[i]]][model_name] = np.nan
                else:
                    if 'High' in model_name:
                        total_reg_model_predict_result[param[model_scene_dis_list[i]]<scene_thred_dict[model_scene_dis_list[i]]][model_name] = np.nan
                    elif 'Low' in model_name:
                        total_reg_model_predict_result[param[model_scene_dis_list[i]]>=scene_thred_dict[model_scene_dis_list[i]]][model_name] = np.nan'''

        # 生成本地投票结果
        reg_stacking = total_reg_model_predict_result.sum(axis = 1)
        cla_stacking = total_cla_model_predict_result.sum(axis = 1)
        local_predict = (reg_stacking+cla_stacking) >= thred_vote
        local_predict = pd.DataFrame(local_predict)
        local_predict.columns = ['本地投票结果']
        local_predict['本地投票数量'] = reg_stacking+cla_stacking


        excel_save_dict = {}
        excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
        excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(total_reg_model_predict_result).join(total_cla_model_predict_result)


        for model_name in total_model_list:
            excel_save_dict[model_rename_dict[model_name] + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]

        check_dir('/data/group/800463/日内强势股/log_parse/模型差异/%s'%tradeDatestr)
        excel_saver(excel_save_dict,'/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_%s_pj3_931.xlsx'%(tradeDatestr,tradeDatestr,environment))


    # excel_save_dict['Ret2oHighPMMLModel_预测概率差异']
    # excel_save_dict['Ret2oLowPMMLModel_预测概率差异']


