'''
S1每日模型信号差异
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
from ProdWork.CommonTools import excel_saver, ftp_download, ftp_upload
from ProdWork.Param_config_data import thred_dict_pj2_931_v5 as thred_dict

if __name__ == '__main__':
    print('=============pj2_931_prod_model_comparision=============')
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')
    tradeDatestr = s.tradingday(nowdate, -2)[0]
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
    if sys.argv[2:]:
        env_list = sys.argv[2:]
    else:
        env_list = ['prod', 'SZEX', 'SHEX', 'UAT', 'UAT_50_51', 'UAT_49_53', 'UAT_lite']
    for environment in env_list:  # ['night']:#['UAT_lite']:#
    # for environment in ['UAT_lite']:  # ['night']:#['UAT_lite']:#
        print(environment)

        '''model_rename_dict = {'saturn931OpenPctHighDjModel' : 'OpenPctHighDjModel',
                          'saturn931OpenPctHighWjModel' : 'OpenPctHighWjModel',
                          'saturn931OpenPctLowDjModel' : 'OpenPctLowDjModel',
                          'saturn931OpenPctLowWjModel' : 'OpenPctLowWjModel',
                          'saturn931Pat3DjModel' : 'Pat3DjModel',
                          'saturn931Pat3XgbModel' : 'Pat3XgbModel',
                          'saturn931Pat4DjModel' : 'Pat4DjModel',
                          'saturn931Pat4XgbModel' : 'Pat4XgbModel',
                          'saturn931Pct5HighWjModel' : 'Pct5HighWjModel',
                          'saturn931Pct5LowWjModel' : 'Pct5LowWjModel',
                          'saturn931Ret2oHighDjModel' : 'Ret2oHighDjModel',
                          'saturn931Ret2oHighPMMLModel' : 'Ret2oHighPMMLModel',
                          'saturn931Ret2oLowDjModel' : 'Ret2oLowDjModel',
                          'saturn931Ret2oLowPMMLModel' : 'Ret2oLowPMMLModel',
                          'saturn931TotalDjModel' : 'TotalDjModel',
                          'saturn931TotalWjModel' : 'TotalWjModel'}'''


        def check_dir(path):  # 路径生成函数
            if not os.path.exists(path):
                os.makedirs(path)


        All_model_predict_data_diff_out_dict = {}

        # ------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
        inf_df = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment),
                               sheetname='项目二931样本')
        inf_df = inf_df.rename(columns={'Unnamed: 0': 'Ticker'}).set_index('Ticker')
        inf_df = inf_df.loc[~inf_df.index.duplicated(keep='first')].sort_index()
        # UAT中的信号
        # log_signal = inf_df[['p2shouldBuySignal']].rename(columns={'p2shouldBuySignal': environment + '_signal'})
        log_signal = inf_df[['p2shouldBuySignal', 'sum_signals']].rename(
            columns={'p2shouldBuySignal': environment + '_signal', 'sum_signals': '%s_sum_signals' % environment})

        total_model_list = list(map(lambda x: x[:~11], np.array(inf_df.columns)[
            np.array(list(map(lambda x: 'probability' in x, list(inf_df.columns))))]))
        total_cla_model_predict_result = pd.DataFrame()
        total_reg_model_predict_result = pd.DataFrame()
        for model_name in thred_dict.keys():
            if model_name + '_probability' not in inf_df.columns:
                inf_df[model_name + '_probability'] = np.nan
        Log_triggered_samples = inf_df.index
        # ------------------------------核对董坚的模型--------------------------------------
        '''DJ_model_name_all = ['saturn931OpenPctHighDjModel','saturn931OpenPctLowDjModel','saturn931Pat3DjModel','saturn931Pat4DjModel',
                             'saturn931Ret2oHighDjModel','saturn931Ret2oLowDjModel','saturn931TotalDjModel']
        DJ_model_rename_dict = {'saturn931OpenPctHighDjModel':'931_openpct_high_v2',
                                'saturn931OpenPctLowDjModel':'931_openpct_low_v2',
                                'saturn931Pat3DjModel':'931_pat_23_v2',
                                'saturn931Pat4DjModel':'931_pat_14_v2',
                                'saturn931Ret2oHighDjModel':'931_ret2o_high_v2',
                                'saturn931Ret2oLowDjModel':'931_ret2o_low_v2',
                                'saturn931TotalDjModel':'931_reg_v2'}'''
        DJ_model_name_all = ['S1OpenPctHighDjModel', 'S1OpenPctLowDjModel', 'S1Pat3DjModel',
                             'S1Pat4DjModel',
                             'S1Ret2oHighDjModel', 'S1Ret2oLowDjModel', 'S1TotalDjModel']
        DJ_model_name_all = list(filter(lambda x: 'DjModel' in x, list(thred_dict.keys())))
        DJ_model_name_all_rename = ['931_openpct_high_v2', '931_openpct_low_v2', '931_pat_23_v2', '931_pat_14_v2',
                                    '931_ret2o_high_v2', '931_ret2o_low_v2', '931_reg_v2']
        DJ_model_rename_dict = dict(zip(DJ_model_name_all, DJ_model_name_all_rename))
        for DJ_model_name in DJ_model_name_all:
            print(DJ_model_name)
            # 核对模型的预测数据
            # DJ_model_local_prob = pd.read_hdf('/data/group/800463/dongj/model_signal/saturn/model_output_everyday/%s_%s/pred_prob.h5'%(tradeDatestr,DJ_model_rename_dict[DJ_model_name]))
            # DJ_model_local_prob = pd.read_hdf('/data/group/800463/dongj/model_signal/saturn/v5/model_output_everyday/%s_%s/pred_prob.h5' % (tradeDatestr, DJ_model_rename_dict[DJ_model_name]))
            dj_path = '/data/group/800463/dongj/model_signal/saturn/model_output_everyday/%s_%s/pred_prob.h5' % (
                tradeDatestr, DJ_model_rename_dict[DJ_model_name])
            DJ_model_local_prob = pd.read_hdf(dj_path)
            # DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(columns = {'pred_prob':DJ_model_name+'_local_prob'})\
            #         .reindex(Log_triggered_samples)
            DJ_model_local_prob = DJ_model_local_prob.reset_index().set_index('Ticker')[['pred_prob']].rename(
                columns={'pred_prob': DJ_model_name + '_local_prob'})
            DJ_model_log_prob = inf_df[[DJ_model_name + '_probability']].rename(
                columns={DJ_model_name + '_probability': DJ_model_name + '_%s_prob' % environment})
            DJ_model_log_prob[DJ_model_name + '_local_prob'] = DJ_model_local_prob[DJ_model_name + '_local_prob']
            DJ_model_log_prob[DJ_model_name + '_diff_prob'] = DJ_model_log_prob[
                                                                  DJ_model_name + '_%s_prob' % environment] - \
                                                              DJ_model_local_prob[DJ_model_name + '_local_prob']
            All_model_predict_data_diff_out_dict[DJ_model_name] = DJ_model_log_prob
            # DJ_model_signal = (DJ_model_local_prob >= thred_dict[DJ_model_name]).reindex(
            #     DJ_model_local_prob[DJ_model_local_prob[DJ_model_name+'_local_prob'].notnull()].index)
            if 'Cla' in DJ_model_name:
                total_cla_model_predict_result = pd.concat(
                    [total_cla_model_predict_result, DJ_model_local_prob >= thred_dict[DJ_model_name]], axis=1)
            else:
                total_reg_model_predict_result = pd.concat(
                    [total_reg_model_predict_result, DJ_model_local_prob >= thred_dict[DJ_model_name]], axis=1)
        # ------------------------------核对王敬的模型--------------------------------------
        '''WJ_model_name_all = ['saturn931OpenPctHighWjModel', 'saturn931OpenPctLowWjModel',
                             'saturn931Pct5HighWjModel','saturn931Pct5LowWjModel','saturn931TotalWjModel']
        WJ_model_rename_dict = {'saturn931OpenPctHighWjModel':'highopenregModel',
                                'saturn931OpenPctLowWjModel':'lowopenregModel',
                                'saturn931Pct5HighWjModel':'highpct5regModel',
                                'saturn931Pct5LowWjModel':'lowpct5regModel',
                                'saturn931TotalWjModel':'allregwjModel'}'''
        WJ_model_name_all = list(filter(lambda x: 'Wj' in x, list(thred_dict.keys())))
        WJ_model_name_all_rename = ['highopenregModel', 'lowopenregModel', 'highpct5regModel', 'lowpct5regModel',
                                    'allregwjModel']
        WJ_model_rename_dict = dict(zip(WJ_model_name_all, WJ_model_name_all_rename))
        for WJ_model_name in WJ_model_name_all:
            # WJ_model_name = 'RollLgbClaModel'
            print(WJ_model_name)
            # wj_new_models_path = '/data/user/013550/wjworkspace/Saturn_931/DataPrediction/Daily_result/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Saturn/S1/%s/%s' % (
                WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            # 核对模型的预测数据
            Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
            if len(Predict_file_csvs) > 0:
                csv_name = np.array(Predict_file_csvs)[np.array(list(map(lambda x: 'v2' not in x, Predict_file_csvs)))][0]
            else:
                csv_name = 'tmp.csv'
            try:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
            except:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            if WJ_model_name in ['saturn931TotalWjModel', 'S1TotalWjXgbModel']:
                # 在这里计算公共样本偏差
                Local_triggered_samples = WJ_model_local_prob['Ticker']
                Local_sample_missing = list(set(Log_triggered_samples).difference(set(WJ_model_local_prob['Ticker'])))
                Log_sample_missing = list(set(WJ_model_local_prob['Ticker']).difference(set(Log_triggered_samples)))
            # WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).reindex(Log_triggered_samples).rename(columns={'pred_Reg': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]
            WJ_model_local_prob = \
                WJ_model_local_prob.set_index(['Ticker']).rename(columns={'pred_Reg': WJ_model_name + '_local_prob'})[
                    [WJ_model_name + '_local_prob']]
            WJ_model_log_prob = inf_df[[WJ_model_name + '_probability']].rename(
                columns={WJ_model_name + '_probability': WJ_model_name + '_%s_prob' % environment})
            WJ_model_log_prob[WJ_model_name + '_local_prob'] = WJ_model_local_prob[WJ_model_name + '_local_prob']
            WJ_model_log_prob[WJ_model_name + '_diff_prob'] = WJ_model_log_prob[
                                                                  WJ_model_name + '_%s_prob' % environment] - \
                                                              WJ_model_local_prob[WJ_model_name + '_local_prob']
            All_model_predict_data_diff_out_dict[WJ_model_name] = WJ_model_log_prob
            if 'Cla' in WJ_model_name:
                total_cla_model_predict_result = pd.concat(
                    [total_cla_model_predict_result, WJ_model_local_prob.dropna() >= thred_dict[WJ_model_name]], axis=1)
            else:
                total_reg_model_predict_result = pd.concat(
                    [total_reg_model_predict_result, WJ_model_local_prob.dropna() >= thred_dict[WJ_model_name]], axis=1)
        # ------------------------------核对谢璐遥的模型--------------------------------------
        XLY_model_name = ['saturn931Pat3XgbModel', 'saturn931Pat4XgbModel',
                          'saturn931Ret2oHighPMMLModel', 'saturn931Ret2oLowPMMLModel']
        XLY_model_name = list(set(thred_dict) - set(DJ_model_name_all + WJ_model_name_all))
        for model_name in XLY_model_name:
            print(model_name)
            # 核对模型的预测数据
            # xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal/%s_saturn_931/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1)\
            #         .set_index('Ticker').reindex(Log_triggered_samples).rename(columns = {model_name+'_proba':model_name+'_local_prob'})[[model_name+'_local_prob']]
            xly_model_local_prob = pd.read_pickle(
                '/data/group/800463/xiely/model_signal/%s_saturn_931/model_predict.pkl' % tradeDatestr).reset_index().drop(
                ['dt'], axis=1) \
                .set_index('Ticker').rename(columns={model_name + '_proba': model_name + '_local_prob'})[
                [model_name + '_local_prob']]
            xly_model_log_prob = inf_df[[model_name + '_probability']].rename(
                columns={model_name + '_probability': model_name + '_%s_prob' % environment})
            xly_model_log_prob[model_name + '_local_prob'] = xly_model_local_prob[model_name + '_local_prob']
            xly_model_log_prob[model_name + '_diff_prob'] = xly_model_log_prob[model_name + '_%s_prob' % environment] - \
                                                            xly_model_local_prob[model_name + '_local_prob']
            All_model_predict_data_diff_out_dict[model_name] = xly_model_log_prob
            xly_model_signal = (xly_model_local_prob >= thred_dict[model_name]).reindex(
                xly_model_local_prob[xly_model_local_prob[model_name + '_local_prob'].notnull()].index)
            if 'Cla' in model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result, xly_model_signal], axis=1,
                                                           sort=True)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result, xly_model_signal], axis=1,
                                                           sort=True)
        # ------------------------------总结df------------------------------------------------
        summary_dict = {}
        for model in total_model_list:
            # model = total_model_list[0]
            model_question_list = []
            if (np.abs(All_model_predict_data_diff_out_dict[model][model + '_diff_prob']) > 1e-5).sum() > 0:
                model_question_list.append('模型存在概率差异！！！最大绝对差异为%f' % np.abs(
                    All_model_predict_data_diff_out_dict[model][model + '_diff_prob']).max())
            else:
                model_question_list.append('模型不存在概率差异~~~')
            summary_dict[model] = model_question_list

        # 对样本进行判断和对分场景进行切分
        # param = pd.read_pickle('/data/group/800463/project/project2_prod/everyday_Param_v2/%s/pj2_v0311_param_rename_%s_after_closed.pkl' % (tradeDatestr, tradeDatestr))
        param = pd.read_pickle(
            '/data/group/800463/project/project2_prod/daily_data/%s_v5/saturn_factor_v5_%s.pkl' % (
                tradeDatestr, tradeDatestr))
        param['is_sample_931'] = ((param['label_T_day_first_ZT_Time'] <= 93100000) == False) & (
                param['saturn_lzt_day_pattern'] >= 3) & \
                                 (param['label_T_open_is_zt'] == 0) & (param['label_T_open_is_zt'] == 0)
        param = param.reset_index().set_index('Ticker')
        # 对样本进行reindex，其他的填充为nan
        total_reg_model_predict_result.index.name = 'Ticker'
        total_cla_model_predict_result.index.name = 'Ticker'
        total_reg_model_predict_result = total_reg_model_predict_result.reindex(param.index)
        total_cla_model_predict_result = total_cla_model_predict_result.reindex(param.index)
        open_pct_high_model = ['S1OpenPctHighDjModel', 'S1OpenPctHighWjXgbModel']
        open_pct_low_model = ['S1OpenPctLowDjModel', 'S1OpenPctLowWjXgbModel']
        pat3_model = ['S1Pat3DjModel', 'S1Pat3PMMLModel']
        pat4_model = ['S1Pat4DjModel', 'S1Pat4PMMLModel']
        ret2o_high_model = ['S1Ret2oHighDjModel', 'S1Ret2oHighXgbModel']
        ret2o_low_model = ['S1Ret2oLowDjModel', 'S1Ret2oLowPMMLModel']
        pct5_high_model = ['S1Pct5HighWjXgbModel']
        pct5_low_model = ['S1Pct5LowWjXgbModel']
        scene_thred_dict = {'saturn_T_o2pre': 0,
                            'saturn_lzt_day_pattern': 4,
                            'saturn_t931_pj2r_931_ret2o': 0,
                            'saturn_EFS_pct5_T1': 0.1190024}
        # 顺序与下方对应
        model_scene_mother_list = [open_pct_high_model, open_pct_low_model, pat3_model, pat4_model,
                                   ret2o_high_model, ret2o_low_model, pct5_high_model, pct5_low_model]
        model_scene_dis_list = ['saturn_T_o2pre', 'saturn_T_o2pre', 'saturn_lzt_day_pattern', 'saturn_lzt_day_pattern',
                                'saturn_t931_pj2r_931_ret2o', 'saturn_t931_pj2r_931_ret2o', 'saturn_EFS_pct5_T1',
                                'saturn_EFS_pct5_T1']
        for i in range(len(model_scene_mother_list)):
            mother_list = model_scene_mother_list[i]
            for model_name in mother_list:
                if 'Cla' in model_name:
                    if 'High' in model_name:
                        total_cla_model_predict_result[
                            param[model_scene_dis_list[i]] < scene_thred_dict[model_scene_dis_list[i]]][
                            model_name] = np.nan
                    elif 'Low' in model_name:
                        total_cla_model_predict_result[
                            param[model_scene_dis_list[i]] >= scene_thred_dict[model_scene_dis_list[i]]][
                            model_name] = np.nan
                else:
                    if 'High' in model_name:
                        total_reg_model_predict_result[
                            param[model_scene_dis_list[i]] < scene_thred_dict[model_scene_dis_list[i]]][
                            model_name] = np.nan
                    elif 'Low' in model_name:
                        total_reg_model_predict_result[
                            param[model_scene_dis_list[i]] >= scene_thred_dict[model_scene_dis_list[i]]][
                            model_name] = np.nan

        # 生成本地投票结果
        reg_stacking = total_reg_model_predict_result.sum(axis=1)
        cla_stacking = total_cla_model_predict_result.sum(axis=1)
        local_predict = reg_stacking >= 4
        local_predict = pd.DataFrame(local_predict)
        local_predict.columns = ['本地投票结果']
        local_predict['本地投票数量'] = reg_stacking + cla_stacking
        if environment == 'prod':
            local_predict['是否在黑名单'] = 0
            sub_index = list(set(local_predict.index.tolist()) & set(filter_black_list))
            local_predict.loc[sub_index, '是否在黑名单'] = 1

        excel_save_dict = {}
        excel_save_dict['差异汇总'] = pd.Series(summary_dict, name='差异汇总')
        excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(param[['is_sample_931']]).join(
            total_reg_model_predict_result)

        for model_name in total_model_list:
            # excel_save_dict[model_rename_dict[model_name] + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]
            excel_save_dict[model_name + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]

        check_dir('/data/group/800463/日内强势股/log_parse/模型差异/%s' % tradeDatestr)
        excel_saver(excel_save_dict, '/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_%s_pj2_931.xlsx' % (
            tradeDatestr, tradeDatestr, environment))

    # excel_save_dict['Ret2oHighPMMLModel_预测概率差异']
    # excel_save_dict['Ret2oLowPMMLModel_预测概率差异']

    aa = local_predict.join(log_signal).join(param[['is_sample_931']]).join(total_reg_model_predict_result)

    '''environment_lst = ['prod', 'UAT', 'SZEX', 'SHEX', 'night1', 'test']
    for environment in environment_lst[:1] + environment_lst[2:4]:  ## night



        model_rename_dict = {'saturn931OpenPctHighDjModel' : 'OpenPctHighDjModel',
                          'saturn931OpenPctHighWjModel' : 'OpenPctHighWjModel',
                          'saturn931OpenPctLowDjModel' : 'OpenPctLowDjModel',
                          'saturn931OpenPctLowWjModel' : 'OpenPctLowWjModel',
                          'saturn931Pat3DjModel' : 'Pat3DjModel',
                          'saturn931Pat3XgbModel' : 'Pat3XgbModel',
                          'saturn931Pat4DjModel' : 'Pat4DjModel',
                          'saturn931Pat4XgbModel' : 'Pat4XgbModel',
                          'saturn931Pct5HighWjModel' : 'Pct5HighWjModel',
                          'saturn931Pct5LowWjModel' : 'Pct5LowWjModel',
                          'saturn931Ret2oHighDjModel' : 'Ret2oHighDjModel',
                          'saturn931Ret2oHighPMMLModel' : 'Ret2oHighPMMLModel',
                          'saturn931Ret2oLowDjModel' : 'Ret2oLowDjModel',
                          'saturn931Ret2oLowPMMLModel' : 'Ret2oLowPMMLModel',
                          'saturn931TotalDjModel' : 'TotalDjModel',
                          'saturn931TotalWjModel' : 'TotalWjModel'}

        def check_dir(path):  # 路径生成函数
            if not os.path.exists(path):
                os.makedirs(path)

        All_model_predict_data_diff_out_dict = {}

        #------------------------------读取log中因子耗时文件中各个模型的预测数据------------------------------
        inf_df = pd.read_excel( '/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_%s.xlsx'%(tradeDate, environment),sheetname = '项目二931样本')
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
        #------------------------------核对董坚的模型--------------------------------------
        DJ_model_name_all = ['saturn931OpenPctHighDjModel','saturn931OpenPctLowDjModel','saturn931Pat3DjModel','saturn931Pat4DjModel',
                             'saturn931Ret2oHighDjModel','saturn931Ret2oLowDjModel','saturn931TotalDjModel']
        DJ_model_rename_dict = {'saturn931OpenPctHighDjModel':'931_openpct_high_v2',
                                'saturn931OpenPctLowDjModel':'931_openpct_low_v2',
                                'saturn931Pat3DjModel':'931_pat_23_v2',
                                'saturn931Pat4DjModel':'931_pat_14_v2',
                                'saturn931Ret2oHighDjModel':'931_ret2o_high_v2',
                                'saturn931Ret2oLowDjModel':'931_ret2o_low_v2',
                                'saturn931TotalDjModel':'931_reg_v2'}
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
            # DJ_model_signal = (DJ_model_local_prob >= thred_dict[DJ_model_name]).reindex(
            #     DJ_model_local_prob[DJ_model_local_prob[DJ_model_name+'_local_prob'].notnull()].index)
            if 'Cla' in DJ_model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,DJ_model_local_prob>=thred_dict[DJ_model_name]],axis = 1)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,DJ_model_local_prob>=thred_dict[DJ_model_name]],axis = 1)
        #------------------------------核对王敬的模型--------------------------------------
        WJ_model_name_all = ['saturn931OpenPctHighWjModel', 'saturn931OpenPctLowWjModel',
                             'saturn931Pct5HighWjModel','saturn931Pct5LowWjModel','saturn931TotalWjModel']
        WJ_model_rename_dict = {'saturn931OpenPctHighWjModel':'highopenregModel',
                                'saturn931OpenPctLowWjModel':'lowopenregModel',
                                'saturn931Pct5HighWjModel':'highpct5regModel',
                                'saturn931Pct5LowWjModel':'lowpct5regModel',
                                'saturn931TotalWjModel':'allregwjModel'}
        for WJ_model_name in WJ_model_name_all:
            # WJ_model_name = 'RollLgbClaModel'
            print(WJ_model_name)
            #wj_new_models_path = '/data/user/013550/wjworkspace/Saturn_931/DataPrediction/Daily_result/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Saturn/S1/%s/%s' % (WJ_model_rename_dict[WJ_model_name], tradeDatestr)
            # 核对模型的预测数据
            Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
            csv_name = np.array(Predict_file_csvs)[np.array(list(map(lambda x:'v2' not in x,Predict_file_csvs)))][0]
            try:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
            except:
                WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            if WJ_model_name == 'saturn931TotalWjModel':
                # 在这里计算公共样本偏差
                Local_triggered_samples = WJ_model_local_prob['Ticker']
                Local_sample_missing = list(set(Log_triggered_samples).difference(set(WJ_model_local_prob['Ticker'])))
                Log_sample_missing = list(set(WJ_model_local_prob['Ticker']).difference(set(Log_triggered_samples)))
            # WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).reindex(Log_triggered_samples).rename(columns={'pred_Reg': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]
            WJ_model_local_prob = WJ_model_local_prob.set_index(['Ticker']).rename(columns={'pred_Reg': WJ_model_name + '_local_prob'})[[WJ_model_name + '_local_prob']]
            WJ_model_log_prob = inf_df[[WJ_model_name+'_probability']].rename(columns = {WJ_model_name+'_probability':WJ_model_name+'_%s_prob'%environment})
            WJ_model_log_prob[WJ_model_name+'_local_prob'] = WJ_model_local_prob[WJ_model_name+'_local_prob']
            WJ_model_log_prob[WJ_model_name+'_diff_prob'] = WJ_model_log_prob[WJ_model_name+'_%s_prob'%environment]-WJ_model_local_prob[WJ_model_name+'_local_prob']
            All_model_predict_data_diff_out_dict[WJ_model_name] = WJ_model_log_prob
            if 'Cla' in WJ_model_name:
                total_cla_model_predict_result = pd.concat([total_cla_model_predict_result,WJ_model_local_prob.dropna()>=thred_dict[WJ_model_name]],axis = 1)
            else:
                total_reg_model_predict_result = pd.concat([total_reg_model_predict_result,WJ_model_local_prob.dropna()>=thred_dict[WJ_model_name]],axis = 1)
        #------------------------------核对谢璐遥的模型--------------------------------------
        XLY_model_name = ['saturn931Pat3XgbModel','saturn931Pat4XgbModel',
                          'saturn931Ret2oHighPMMLModel','saturn931Ret2oLowPMMLModel']

        for model_name in XLY_model_name:
            print(model_name)
            # 核对模型的预测数据
            # xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal/%s_saturn_931/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1)\
            #         .set_index('Ticker').reindex(Log_triggered_samples).rename(columns = {model_name+'_proba':model_name+'_local_prob'})[[model_name+'_local_prob']]
            xly_model_local_prob = pd.read_pickle('/data/group/800463/xiely/model_signal/%s_saturn_931/model_predict.pkl'%tradeDatestr).reset_index().drop(['dt'],axis = 1)\
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
        param['is_sample_931'] = ((param['saturn_T_day_first_ZT_Time'] <= 93100000) == False) & (param['saturn_lzt_day_pattern']>=3) &\
                                 (param['saturn_T_open_is_zt'] == 0) & (param['saturn_T_open_is_dt'] == 0)
        param = param.reset_index().set_index('Ticker')
        # 对样本进行reindex，其他的填充为nan
        total_reg_model_predict_result.index.name = 'Ticker'
        total_cla_model_predict_result.index.name = 'Ticker'
        total_reg_model_predict_result = total_reg_model_predict_result.reindex(param.index)
        total_cla_model_predict_result = total_cla_model_predict_result.reindex(param.index)
        open_pct_high_model = ['saturn931OpenPctHighDjModel','saturn931OpenPctHighWjModel']
        open_pct_low_model = ['saturn931OpenPctLowDjModel','saturn931OpenPctLowWjModel']
        pat3_model = ['saturn931Pat3DjModel','saturn931Pat3XgbModel']
        pat4_model = ['saturn931Pat4DjModel','saturn931Pat4XgbModel']
        ret2o_high_model = ['saturn931Ret2oHighDjModel','saturn931Ret2oHighPMMLModel']
        ret2o_low_model = ['saturn931Ret2oLowDjModel','saturn931Ret2oLowPMMLModel']
        pct5_high_model = ['saturn931Pct5HighWjModel']
        pct5_low_model = ['saturn931Pct5LowWjModel']
        scene_thred_dict = {'saturn_T_o2pre':0,
                            'saturn_lzt_day_pattern':4,
                            'saturn_pj2r_931_ret2o':0,
                            'saturn_EFS_pct5_T1':0.1190024}
        # 顺序与下方对应
        model_scene_mother_list = [open_pct_high_model,open_pct_low_model,pat3_model,pat4_model,
                                   ret2o_high_model,ret2o_low_model,pct5_high_model,pct5_low_model]
        model_scene_dis_list = ['saturn_T_o2pre','saturn_T_o2pre','saturn_lzt_day_pattern','saturn_lzt_day_pattern',
                                'saturn_pj2r_931_ret2o','saturn_pj2r_931_ret2o','saturn_EFS_pct5_T1','saturn_EFS_pct5_T1']
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
                        total_reg_model_predict_result[param[model_scene_dis_list[i]]>=scene_thred_dict[model_scene_dis_list[i]]][model_name] = np.nan

        # 生成本地投票结果
        reg_stacking = total_reg_model_predict_result.sum(axis = 1)
        cla_stacking = total_cla_model_predict_result.sum(axis = 1)
        local_predict = reg_stacking >= 4
        local_predict = pd.DataFrame(local_predict)
        local_predict.columns = ['本地投票结果']

        excel_save_dict = {}
        excel_save_dict['差异汇总'] = pd.Series(summary_dict,name = '差异汇总')
        excel_save_dict['本地投票结果'] = local_predict.join(log_signal).join(param[['is_sample_931']]).join(total_reg_model_predict_result)


        for model_name in total_model_list:
            excel_save_dict[model_rename_dict[model_name] + '_预测概率差异'] = All_model_predict_data_diff_out_dict[model_name]

        check_dir('/data/group/800463/日内强势股/log_parse/模型差异/%s'%tradeDatestr)
        excel_saver(excel_save_dict,'/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_%s_pj2_931.xlsx'%(tradeDatestr,tradeDatestr,environment))


    # excel_save_dict['Ret2oHighPMMLModel_预测概率差异']
    # excel_save_dict['Ret2oLowPMMLModel_预测概率差异']

    aa = local_predict.join(log_signal).join(param[['is_sample_931']]).join(total_reg_model_predict_result)'''
