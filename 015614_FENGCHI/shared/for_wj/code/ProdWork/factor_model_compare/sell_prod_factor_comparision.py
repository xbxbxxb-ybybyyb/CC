''''
Saturn因子数据对比）定时任务可部署
'''
import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from LucienUtil import IO
from ProdWork.CommonTools import excel_saver, ftp_download, ftp_upload

def check_dir(path):
    from xquant.pyfilelib import Pyfile
    py = Pyfile()
    if not py.exists(path):
        py.mkdir(path)

def check_missing(list_UAT, list_python, name, environment):
    if len(list_UAT) == 0:
        list_UAT += ['无%s遗失' % (name)]
    if len(list_python) == 0:
        list_python += ['无%s遗失' % (name)]
    Missing_df = pd.DataFrame([[list_UAT], [list_python]], index=['%s%s' % (environment,name), '本地%s' % (name)],
                              columns=['%s遗失情况' % name])
    return Missing_df

def factor_comparison(basic_pj2_path, local_factor_path, java_factor_path, date
                      ,output_folder,all_sample_environment,environment):
    basic_pj2 = pd.read_pickle(basic_pj2_path)
    def merge_filter(df, delay=False):
        open_filter = (df['T_open_is_zt'] == False) & (df['T_open_is_dt'] == False)
        after_not_ul_len_filter = df['after_not_ul_len'] > 10
        can_buy_filter = df['T_first_trans_ZT'] != 1
        if delay:
            delay_10_filter = (df['T_day_first_ZT_Time'] <= 94000000) == False
            return df[open_filter & after_not_ul_len_filter & can_buy_filter & delay_10_filter]
        else:
            return df[open_filter & after_not_ul_len_filter & can_buy_filter]
    basic_pj2_filtered = basic_pj2.copy()#merge_filter(basic_pj2)


    '''local_factor_raw = pd.DataFrame()
    for file in os.listdir(local_factor_path):
        if '.h5' in file:
            factor_name = file[:~20]
            this_factor_data = pd.read_hdf(local_factor_path+file)
            local_factor_raw = pd.concat([local_factor_raw,this_factor_data],axis = 1)'''
    local_factor_raw = pd.read_pickle(local_factor_path)
    local_factor = local_factor_raw.reset_index().set_index('Ticker')[local_factor_raw.columns]

    # 合并T日和T-1日因子生成盘后参数
    '''factor_info_path = '/data/group/800463/project/project2_prod/factor_lib_v210311/total_factors_20210311.xlsx'
    factor_info_file = pd.read_excel(factor_info_path)

    T_930_factors = list(
        factor_info_file[factor_info_file['factor_type'].apply(lambda x: x in ['TTickab','TTransaction','TTickab_cs'])]['factor_name'])
    T_931_factors = list(
        factor_info_file[factor_info_file['factor_type'].apply(lambda x: x in ['T1mTickab', 'T1mTransaction', 'T1mTickab_cs'])]['factor_name'])
    T_940_factors = list(
        factor_info_file[factor_info_file['factor_type'].apply(lambda x: x in ['T10mTransaction','T10mTickab'])]['factor_name'])
    # ----------------------['T-1_factor','LastZtLastTick','LastZtLastTrans']三类因子改名，在前面加上saturn_------------------------
    def saturn_factor_rename(factor_data):
        origin_factor_name = list(factor_data.columns)
        rename_dict = {}
        for factor_name in origin_factor_name:
            if factor_name in T_930_factors:
                rename_dict[factor_name] = 'saturn_t930_' + factor_name
            elif factor_name in T_931_factors:
                rename_dict[factor_name] = 'saturn_t931_' + factor_name
            elif factor_name in T_940_factors:
                rename_dict[factor_name] = 'saturn_t940_' + factor_name
            else:
                rename_dict[factor_name] = 'saturn_' + factor_name
        return factor_data.rename(columns=rename_dict)
    local_factor = saturn_factor_rename(local_factor)'''
    for trade_time in ['930','931']:
        java_factor = pd.read_excel(java_factor_path, sheet_name='%ssell'%trade_time)
        if 'Unnamed: 0' in java_factor.columns.tolist():
            java_factor = java_factor.rename(columns = {'Unnamed: 0':'Ticker'}).set_index('Ticker')
        # ----------------------检查因子数量有没有差异---------------------
        local_factor_names = local_factor.columns
        java_factor_names = java_factor.columns
        java_missing_factor = list(set(local_factor_names).difference(java_factor_names))
        local_missing_factors = list(set(java_factor_names).difference(local_factor_names))
        # ----------------------检查样本数量和自由流通股本有没有差异---------------------
        local_samples = list(basic_pj2_filtered.reset_index()['Ticker'])
        java_samples = list(java_factor.index)
        local_missing_samples = list(set(java_samples).difference(local_samples))
        java_missing_samples = list(set(local_samples).difference(java_samples))
        # ----------------------检查重合的样本的因子值有没有差异---------------------
        ready_samples = list(set(local_samples).intersection(set(java_samples)))
        ready_factor = list(set(local_factor_names).intersection(set(java_factor_names)))
        local_factors_check_df = local_factor.loc[ready_samples]
        java_factors_check_df = java_factor.loc[ready_samples]
        # 检测每个因子是否有样本不一样
        all_diff_samples = pd.DataFrame()
        for factor in ready_factor:
            approx_samples = (np.abs(local_factors_check_df[factor] - java_factors_check_df[factor]) > 1e-8)
            this_factor_diff_samples_python = local_factors_check_df[factor][approx_samples].reset_index()
            this_factor_diff_samples_python['factor_name'] = factor
            this_factor_diff_samples_python = this_factor_diff_samples_python.set_index(['factor_name', 'Ticker']).rename(columns={factor: 'local'})
            this_factor_diff_samples_UAT = java_factors_check_df[factor][approx_samples].reset_index()
            this_factor_diff_samples_UAT['factor_name'] = factor
            this_factor_diff_samples_UAT = this_factor_diff_samples_UAT.set_index(['factor_name', 'Ticker']).rename(columns={factor: environment})
            this_factor_diff_both = this_factor_diff_samples_python[['local']].join(this_factor_diff_samples_UAT[[environment]])
            all_diff_samples = pd.concat([all_diff_samples, this_factor_diff_both])
        all_diff_samples['diff'] = np.abs(all_diff_samples['local'] - all_diff_samples[environment])
        all_diff_samples['ratio_diff'] = np.abs(all_diff_samples[environment] / all_diff_samples['local'] - 1)
        Difference_matrix = np.abs(local_factors_check_df[ready_factor] - java_factors_check_df[ready_factor])
        if len(all_diff_samples) == 0:
            all_diff_samples = pd.DataFrame(['无差异因子'])
        output_dict = {'差值大于1e-8': all_diff_samples,
                       '全样本差值': Difference_matrix,
                       '因子遗失情况': check_missing(java_missing_factor, local_missing_factors, '因子', environment)}
        if all_sample_environment:
            if date>='20210323':
                param_samples = list()
            else:
                param_samples = list(pd.read_excel('/data/group/800463/日内强势股/实盘测试参数/param-%s-prod.xlsx'%date)['股票代码'])
            java_in_param_missing_samples = list(set(java_missing_samples).intersection(set(param_samples)))
            local_in_param_missing_samples = list(set(local_missing_samples).intersection(set(param_samples)))
            java_not_in_param_missing_samples = list(set(java_missing_samples).difference(set(java_in_param_missing_samples)))
            local_not_in_param_missing_samples = list(set(local_missing_samples).difference(set(local_in_param_missing_samples)))
            output_dict['未在参数中样本'] = check_missing(java_not_in_param_missing_samples, local_not_in_param_missing_samples, '样本', environment)
            output_dict['样本遗失情况'] = check_missing(java_in_param_missing_samples, local_in_param_missing_samples, '样本', environment)
        check_dir(output_folder)
        excel_name = os.path.join(output_folder, 'Factor_diff_Sell13_%s_%s_%s.xlsx' % (trade_time, date, environment))
        try:
            excel_saver(output_dict, excel_name)
        except:
            print('saving error!!!!!!!!!!!!')

if __name__ == '__main__':
    print('============sell_prod_factor_comparision===========')
    from xquant.factordata import FactorData
    import datetime as dt
    s = FactorData()

    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
    else:
        nowdate = dt.datetime.now().strftime('%Y%m%d')

    date = s.tradingday(nowdate,-2)[0]

    for date in s.tradingday(date,date):
        print('nowdate = %s' % date)
        date_h = pd.Timestamp(date).strftime('%Y-%m-%d')
        print(date_h)
        # sel_environment = ['prod', 'SHEX', 'SZEX', 'UAT', 'UAT_50_51', 'UAT_49_53', 'UAT_lite', 'UAT_other', 'night1', 'test']
        if sys.argv[2:]:
            environment_lst = sys.argv[2:]
        else:
            environment_lst = ['UAT', 'UAT_50_51', 'UAT_49_53','night']
        # environment_lst = ['UAT_50_51']
        for environment in environment_lst:
            print(environment)
            # 是否计算样本偏差
            all_sample_environment = True
            basic_pj2_path = '/data/group/800463/project/projectS_prod/daily_data/%s_v1/sell_factor_v1_%s.pkl' % (date,date)
            # 需要陈睿的每日本地因子数据
            #local_factor_path = '/data/group/800463/project/project2_prod/everyday_Factor_v2/T_day_factor/%s_%s/' % (date, date)

            # 需要陈睿的每日本地因子数据
            local_factor_path = '/data/group/800463/project/projectS_prod/daily_data/%s_v1/sell_factor_v1_%s.pkl' % (date,date)

            # 需要传入日志解析中的因子值数据
            java_factor_path = '/data/group/800463/日内强势股/log_parse/因子数据/卖出Sell13因子数据_%s_%s.xlsx' % (date_h, environment)

            # 输出路径
            output_folder = '/data/group/800463/日内强势股/log_parse/因子差异/%s_%s/' % (date, environment)
            factor_comparison(basic_pj2_path = basic_pj2_path, local_factor_path = local_factor_path,java_factor_path = java_factor_path,date = date,
                              output_folder = output_folder,all_sample_environment = all_sample_environment,environment = environment)
            print('finished')

