import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from LucienUtil import IO

def excel_saver(output_dict, excel_name):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        if len(output_dict[key]) == 0 and len(output_dict[key].columns) == 0:
            pd.DataFrame().to_excel(writer, sheet_name=key)
        else:
            output_dict[key].to_excel(writer, sheet_name=key)
    writer.save()
    print('create sheets %s for %s！！！！！！！！！！' % (list(output_dict.keys()), excel_name))
    return

def check_dir(path):
    from xquant.pyfilelib import Pyfile
    py = Pyfile()
    if not py.exists(path):
        py.mkdir(path)

def timestr2int(x):
    out = '0'
    if len(x) == 2:
        out = str(int(x+'0000000'))
    if len(x) == 5:
        out = str(int(x[0]+x[1]+x[3]+x[4]+'00000'))
    if len(x) == 8:
        out = str(int(x[0]+x[1]+x[3]+x[4]+x[6]+x[7]+'000'))
    if len(x) == 12:
        out = str(int(x[0]+x[1]+x[3]+x[4]+x[6]+x[7]+x[9]+x[10]+x[11]))
    return out

def check_missing(list_UAT, list_python, name, environment):
    if len(list_UAT) == 0:
        list_UAT += ['无%s遗失' % (name)]
    if len(list_python) == 0:
        list_python += ['无%s遗失' % (name)]
    Missing_df = pd.DataFrame([[list_UAT], [list_python]], index=['%s%s' % (environment,name), '本地%s' % (name)],
                              columns=['%s遗失情况' % (name)])
    return Missing_df

def factor_comparison(local_data_path, local_factor_path,UAT_factor_path,daily_zuhe_path,date,date_hyphen
                      ,factor_time_path,output_folder,all_sample_environment,environment,local_basic_path):
    import time
    while not os.path.exists(local_data_path+'%s.pkl' % date):
        print('缺失' + local_data_path+'%s.pkl' % date)
        time.sleep(60)
    local_data = pd.read_pickle(local_data_path+'%s.pkl' % date)
    while not os.path.exists(local_factor_path + 'all_factor_zt_merge_v2412_BJ_%s.pkl' % date):
        print('缺失' + local_factor_path + 'all_factor_zt_merge_v2412_BJ_%s.pkl' % date)
        time.sleep(60)
    python_factors = pd.read_pickle(local_factor_path + 'all_factor_zt_merge_v2412_BJ_%s.pkl' % date)
    # python_factors = python_factors.query('last_is_zt==0')

    basic_df = pd.read_hdf(local_basic_path + 'Basic_zt_BJ_%s_%s.h5' % (date, date))
    python_factors = python_factors[(basic_df['ZT_Time'] <= 143000000)]
    UAT_factors = pd.read_excel(UAT_factor_path + '因子数据_%s-%s-%s_%s.xlsx' % (Year, Month, Day, environment))
    if len(UAT_factors) > 0:
        UAT_factors = UAT_factors[~UAT_factors['Unnamed: 0'].duplicated()]
    else:
        UAT_factors = pd.DataFrame(columns=['Unnamed: 0'])
    UAT_factors['dt'] = python_factors.index[0][0]
    UAT_factors = UAT_factors.rename(columns={'Unnamed: 0':'Ticker'}).set_index(['dt','Ticker'])
    # 20210813添加nan数量判断
    nan_samples = pd.DataFrame()
    label_cols = python_factors.filter(regex='label_').columns.tolist()

    python_factors_joined = python_factors.reindex(UAT_factors.index)[list(set(python_factors.columns.tolist())-set(label_cols))]

    Lzt_nan_count = UAT_factors.loc[python_factors_joined[python_factors_joined['last_is_zt']==1].index].isnull().sum(axis = 1)
    LNzt_nan_count = UAT_factors.loc[python_factors_joined[python_factors_joined['last_is_zt']==0].index].isnull().sum(axis = 1)
    Lzt_nan_sample = Lzt_nan_count[(Lzt_nan_count!=85) & (Lzt_nan_count!=0)]
    LNzt_nan_sample = LNzt_nan_count[(LNzt_nan_count!=29) & (LNzt_nan_count!=0)]
    if (len(LNzt_nan_sample) +len(Lzt_nan_sample)) != 0:
        nan_samples = pd.concat([Lzt_nan_sample,LNzt_nan_sample])
    # ----------------------检查因子数量有没有差异---------------------
    python_factors_names = python_factors.columns
    UAT_factors_names = UAT_factors.columns
    UAT_missing_factors = list(set(python_factors_names).difference(UAT_factors_names))
    UAT_missing_factors_abnormal = list(set(UAT_missing_factors)
        .difference(['T_max_up_pct_bid_order',
        'T_max_down_pct_ask_order',
        'T_max_down_pct_ask_order_amt',
        'T_l5_act_buy_amt_mean']))
    python_missing_factors = list(set(UAT_factors_names).difference(python_factors_names))
    # ----------------------检查自由流通股本差异样本--------------------
    # ----------------------检查样本数量和自由流通股本有没有差异---------------------
    ff_shares_diff_out_df = pd.DataFrame(['无ff_shares差异样本'])
    try:
        f_data = IO.read_data([date, date],
                          columns=['open','pre_close']
                          ,alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        open_filter_list = list(f_data[f_data['open']>f_data['pre_close']*0.95].index.get_level_values(1).drop_duplicates())

        zuhe_file = pd.read_excel('/data/group/800463/日内强势股/实盘测试参数/param-%s-%s.xlsx' % (date,environment))

        total_zuhe =  list(zuhe_file['股票代码'])
        zuhe_file['dt'] = pd.Timestamp(date)
        zuhe_file = zuhe_file.rename(columns = {'股票代码':'Ticker'}).set_index(['dt','Ticker'])
        # -------------------------------------------------------
        python_factors_samples = list(set(total_zuhe).intersection(list(python_factors.index.get_level_values(1))).intersection(open_filter_list))
        #### all_ffs_data = python_factors[['ff_shares']].join(zuhe_file[['自由流通股本']])
        local_ff_shares = basic_df[['float_shares']].groupby(level=['dt', 'Ticker']).mean()
        diff_check = np.abs(local_ff_shares['float_shares'].loc[date, python_factors_samples]-zuhe_file['自由流通股本'].loc[date, python_factors_samples])>1e-8
        ff_share_diff_list = list(diff_check[diff_check].index.get_level_values(1).drop_duplicates())
        if len(ff_share_diff_list) !=0:
            ff_shares_diff_out_df = pd.DataFrame(local_ff_shares['float_shares'].loc[date,ff_share_diff_list]).rename(columns = {'float_shares':'local_ff_shares'})\
                .join(pd.DataFrame(zuhe_file['自由流通股本'].loc[date,ff_share_diff_list]).rename(columns = {'自由流通股本':'%s_ff_shares'%(environment)}))
            ff_shares_diff_out_df['diff'] = ff_shares_diff_out_df['local_ff_shares'] - ff_shares_diff_out_df['%s_ff_shares'%(environment)]
    except FileNotFoundError:
        print('组合数据缺失')
        python_factors_samples = list(python_factors.index.get_level_values(1))
    UAT_factors_samples = list(UAT_factors.index.get_level_values(1))
    UAT_missing_samples = list(set(python_factors_samples).difference(UAT_factors_samples))
    python_missing_samples = list(set(UAT_factors_samples).difference(python_factors_samples))
    # ----------------------检查ZT_Time有没有差异--------------------------------
    # local_correct_samples = local_data.index.get_level_values(1).drop_duplicates()
    ZT_Time_local = pd.DataFrame(local_data.groupby(level=['dt','Ticker']).apply(lambda x:str(int(x['MDTime'].iloc[~0]))))
    ZT_Time_local.columns = ['ZT_Time_local']
    ZT_Time_local = pd.DataFrame(ZT_Time_local['ZT_Time_local'].loc[date,python_factors_samples])
    ZT_Time_local[ZT_Time_local['ZT_Time_local'].apply(lambda x:int(x))<100000000].sort_values(by = 'ZT_Time_local')
    ZT_Time_UAT = pd.read_excel(factor_time_path + '因子耗时_%s_%s.xlsx'%(date_hyphen,environment))
    ZT_Time_UAT = ZT_Time_UAT[~ZT_Time_UAT['Unnamed: 0'].duplicated()]

    if 'ZT_Time_str' in ZT_Time_UAT.columns:    # 当天有触发
        ZT_Time_UAT['ZT_Time_%s' % environment] = ZT_Time_UAT['ZT_Time_str'].apply(timestr2int)
    else:   # 当天因子耗时文件中无触发
        ZT_Time_UAT['ZT_Time_%s' % environment] = np.nan
    ZT_Time_UAT['dt'] = pd.Timestamp(date)
    ZT_Time_UAT = ZT_Time_UAT.rename(columns = {'Unnamed: 0':'Ticker'}).set_index(['dt','Ticker'])
    ZT_Time_comparison = pd.concat([ZT_Time_UAT[['ZT_Time_%s'%(environment)]],ZT_Time_local[['ZT_Time_local']]],axis = 1)
    ZT_Time_comparison['ZT_Time_check'] = ZT_Time_comparison['ZT_Time_%s'%(environment)] == ZT_Time_comparison['ZT_Time_local']

    # ----------------------检查重合的样本的因子值有没有差异---------------------
    ready_samples = list(set(python_factors.index).intersection(UAT_factors.index))
    ready_factor = list(set(python_factors_names).intersection(UAT_factors_names))
    python_factors_check_df = python_factors.loc[ready_samples]
    UAT_factors_check_df = UAT_factors.loc[ready_samples]
    # 检测每个因子是否有样本不一样
    all_diff_samples = pd.DataFrame()
    for factor in ready_factor:
        approx_samples = (np.abs(python_factors_check_df[factor] - UAT_factors_check_df[factor]) > 1e-8)\
                         | (np.abs(UAT_factors_check_df[factor]/python_factors_check_df[factor] -1) > 1e-8)
        this_factor_diff_samples_python = python_factors_check_df[factor][approx_samples].reset_index()
        this_factor_diff_samples_python['factor_name'] = factor
        this_factor_diff_samples_python = this_factor_diff_samples_python.set_index(['factor_name', 'Ticker']).rename(columns={factor: 'local'})
        this_factor_diff_samples_UAT = UAT_factors_check_df[factor][approx_samples].reset_index()
        this_factor_diff_samples_UAT['factor_name'] = factor
        this_factor_diff_samples_UAT = this_factor_diff_samples_UAT.set_index(['factor_name', 'Ticker']).rename(columns={factor:environment})
        this_factor_diff_both = this_factor_diff_samples_python[['local']].join(this_factor_diff_samples_UAT[[environment]])
        all_diff_samples = pd.concat([all_diff_samples, this_factor_diff_both])

    if 'local' in all_diff_samples.columns: # 没有触发样本，ready_factor为空，所以没有进入上面循环，没有赋值local列
        all_diff_samples['diff'] = np.abs(all_diff_samples['local']- all_diff_samples[environment])
        all_diff_samples['ratio_diff'] =  np.abs(all_diff_samples[environment] / all_diff_samples['local']-1)
    else:
        all_diff_samples['diff'], all_diff_samples['ratio_diff'] = np.nan, np.nan
    Difference_matrix = np.abs(python_factors_check_df[ready_factor] - UAT_factors_check_df[ready_factor])
    if len(all_diff_samples) == 0:
        all_diff_samples = pd.DataFrame(['无因子差异'])
    output_dict = {'差值大于1e-8':all_diff_samples.reset_index(),
                   '全样本差值':Difference_matrix,
                   '因子存在NAN样本':nan_samples}
    if all_sample_environment:
        output_dict['样本遗失情况'] = check_missing(UAT_missing_samples,python_missing_samples,'样本',environment)
        output_dict['未在参数中样本'] = pd.DataFrame(list(set(python_factors.index.get_level_values(1)).difference(set(python_factors_samples))))
        output_dict['触发时间和样本对比'] = ZT_Time_comparison
        # output_dict['因子耗时与数据量对比'] = Local_data_stats
        output_dict['自由流通股本数据有差距的样本'] = ff_shares_diff_out_df
    check_dir(output_folder)
    excel_name = os.path.join(output_folder, 'Factor_diff_%s_%s_3.xlsx' % (date,environment) )
    try:
        excel_saver(output_dict, excel_name)
    except:
        print('error!!!!!!!!!!')



if __name__ == '__main__':
    print('==========jupBj_prod_factor_comparision==========')
    import datetime as dt
    from xquant.factordata import FactorData
    s = FactorData()
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = dt.datetime.now().strftime('%Y%m%d')
        # date = '20250214'
    datelist = s.tradingday(date,date)
    # datelist = s.tradingday(20241008, 20241014)
    for date in datelist:
        #date = '20230308'
        comparison_date = s.tradingday(date,-1)[0]
        Year = comparison_date[0:4]
        Month = comparison_date[4:6]
        Day = comparison_date[6:8]
        date = Year + Month + Day
        date_hyphen = '%s-%s-%s'%(Year,Month,Day)
        # environment = 'UAT'
        if sys.argv[2:]:
            env_list = sys.argv[2:]
        else:
            env_list = ['prod']
            # env_list = ['prod', 'UAT']
            # env_list = ['test']
            # env_list = ['UAT']
        for environment in env_list:  #
        # for environment in ['UAT_lite']:  #
            print(date, environment)
            # 是否计算样本偏差
            all_sample_environment = True
            # 需要王伟地的每日本地因子数据
            local_basic_path = '/data/group/800463/project/project1_prod/left_v2310/daily_data/%s/' % date
            local_factor_path = '/data/group/800463/project/project1_prod/right_v2412_BJ/daily_data/%s/'%(str(date))
            # 需要传入日志解析中的因子值数据
            # UAT_factor_path = '/data/user/013550/%s_factor_data/'%(environment)
            UAT_factor_path = '/data/group/800463/日内强势股/jupiterBj_log_parse/因子数据/'
            # 输出路径
            # output_folder = '/data/user/013550/%s_factor_test_result/%s_%s/' % (environment,date,environment)
            output_folder = '/data/group/800463/日内强势股/jupiterBj_log_parse/因子差异/%s_%s/' % (date,environment)
            # 需要传入谢璐遥的每日组合
            # daily_zuhe_path = '/data/user/013550/%s_daily_zuhe/'%(environment)
            daily_zuhe_path = '/data/group/800463/日内强势股/实盘测试参数/'
            # 需要王伟地的每日本地行情数据（这里主要需要突破时间）
            # prod
            # local_data_path = '/data/group/800463/data/project1_prod/transaction_zt_bs/'
            local_data_path = '/data/group/800463/data/project1_prod/tick_jupiter_BJ/'  # 20241230北交所用这个地址

            # 需要传入日志解析中的因子耗时数据
            # factor_time_path = '/data/user/013550/%s_factor_time/'%(environment)
            factor_time_path = '/data/group/800463/日内强势股/jupiterBj_log_parse/因子耗时/'

            factor_comparison(local_data_path = local_data_path, local_factor_path=local_factor_path, UAT_factor_path=UAT_factor_path
                              ,daily_zuhe_path = daily_zuhe_path, factor_time_path = factor_time_path, output_folder=output_folder
                              ,date=date ,date_hyphen=date_hyphen, all_sample_environment = all_sample_environment,environment = environment,
                              local_basic_path = local_basic_path)
            print('finished')





