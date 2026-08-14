import pandas as pd
import os
from xquant.factordata import FactorData
import numpy as np
import csv
from test_factor_demo_jupiter import strongFactorTest
from project_sell_factor_test_origin import FactorTest

s = FactorData()
# 同花顺人气，多列
# df = pd.read_csv('同花顺人气--2019.csv')
# df['code'] = df['证券代码'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
# df['date'] = df['日期'].apply(lambda x: pd.Timestamp(x))
# df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
# df = df.drop(['日期','证券代码','证券简称'],axis = 1)
# df = df.rename({'code':'Ticker','date':'dt'},axis=1)
# df = df.set_index(['dt','Ticker'])
# res = pd.DataFrame()
# start_date = '20190101'
# end_date = '20191231'
# # Jupiter
# factor_test = strongFactorTest(int(start_date), int(end_date))
# result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/测试结果汇总/'
# for col in df.columns:
#     factor_name = col
#     print(factor_name)
#     df_test = df[[col]].unstack().shift(1).stack()
#     df_test = df_test.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
#     factor_test.factor_test(df_test, result_path, factor_corr_test=True)
#     check_score = factor_test.check_score(factor_test.result_dic['double_group_sort']['ZT_Time'].copy(),
#                                  factor_test.result_dic['corr_month'].copy(),
#                                  np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']))[1]
#     print('check_score:',check_score.loc['score','tot_score'])
#     print('IC：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
#     print('高corr库中因子：')
#     print(factor_test.result_dic['factor_corr_summary'])
#     print('均值和中位数: ',factor_test.basic_df['factor'].mean(),"",factor_test.basic_df['factor'].median())
#     print('重复值: ',factor_test.result_dic['other_sta'])
#     res.loc['Jupiter' + factor_name,'IC'] = factor_test.result_dic['corr_sta'].loc['corr_tot','value']
#     res.loc['Jupiter' + factor_name, 'score'] = check_score.loc['score','tot_score']
#     res.loc['Jupiter' + factor_name, 'corr_factor'] = str(factor_test.result_dic['factor_corr_summary'])
#
# # Sell
# start_date = '20190101'
# end_date = '20191231'
# factor_test = FactorTest(int(start_date), int(end_date),
#                         test_sample = 'bt',
#                         style_list=['T_o2pre', 'free_turn'],
#                         cal_mi = True,
#                         buy_type='0931')
# result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/测试结果汇总/'
# for col in df.columns:
#     factor_name = col
#     print(factor_name)
#     df_test = df[[col]].unstack().shift(1).stack()
#     df_test = df_test.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
#     factor_test.factor_test(df_test, result_path, factor_corr_test=True)
#     check_score = factor_test.result_dic['check_score_res']
#     print('总分:',check_score.loc['score','tot_score'])
#     print('CORR：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
#     print('高corr库中因子：')
#     print(factor_test.result_dic['factor_corr_summary'])
#     print('均值与中位数:',factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median())
#     print(factor_test.result_dic['max_same_ratio'])
#     res.loc['Sell' + factor_name,'IC'] = factor_test.result_dic['corr_sta'].loc['corr_tot','value']
#     res.loc['Sell' + factor_name, 'score'] = check_score.loc['score','tot_score']
#     res.loc['Sell' + factor_name, 'corr_factor'] = str(factor_test.result_dic['factor_corr_summary'])

# 同花顺点击量占比与自选股占比
start_date = '20160101'
end_date = '20191231'
for i in ['点击量占比','自选股占比']:
    factor_name = 'factor_qyh_ths_' + i
    if i == '点击量占比':
        df = pd.read_csv('thsindex1.csv')
    if i == '自选股占比':
        df = pd.read_csv('thsindex4.csv')
    df['code'] = df['code'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
    df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df.columns = ['dt', 'Ticker', 'name', 'ori']
    df = df[['dt','Ticker','ori']]
    df = df.set_index(['dt', 'Ticker'])
    # ori
    ## Jupiter
    factor_test = strongFactorTest(int(start_date), int(end_date))
    result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/测试结果汇总/'
    for col in df.columns:
        factor_name = col
        print('Jupiter_' + factor_name + '_' + i)
        df_test = df[[col]].unstack().shift(1).stack()
        df_test = df_test.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
        factor_test.factor_test(df_test, result_path, factor_corr_test=True)
        check_score = factor_test.check_score(factor_test.result_dic['double_group_sort']['ZT_Time'].copy(),
                                     factor_test.result_dic['corr_month'].copy(),
                                     np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']))[1]
        print('check_score:',check_score.loc['score','tot_score'])
        print('IC：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
        print('高corr库中因子：')
        print(factor_test.result_dic['factor_corr_summary'])
        print('均值和中位数: ',factor_test.basic_df['factor'].mean(),"",factor_test.basic_df['factor'].median())
        print('重复值: ',factor_test.result_dic['other_sta'])
    ## Sell
    factor_test = FactorTest(int(start_date), int(end_date),
                             test_sample = 'bt',
                             style_list=['T_o2pre', 'free_turn'],
                             cal_mi = True,
                             buy_type='0931')
    result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/测试结果汇总/'
    for col in df.columns:
        factor_name = col
        print('Sell_' + factor_name + '_' + i)
        df_test = df[[col]].unstack().shift(1).stack()
        df_test = df_test.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
        factor_test.factor_test(df_test, result_path, factor_corr_test=True)
        check_score = factor_test.result_dic['check_score_res']
        print('总分:',check_score.loc['score','tot_score'])
        print('CORR：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
        print('高corr库中因子：')
        print(factor_test.result_dic['factor_corr_summary'])
        print('均值与中位数:',factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median())
        print(factor_test.result_dic['max_same_ratio'])
    # change
    df['change'] = (df['ori'].unstack() / df['ori'].unstack().shift(1) - 1).stack()
    df_change = df['change'].unstack()
    def get_lma(a,n):
        weight = [(n-i)/(n+1)/n*2 for i in range (0,n)]
        counter = 1
        df = pd.DataFrame()
        for x in weight:
            if (counter == 1):
                df = a*x
            else:
                df = df + a.shift(counter-1)*x
            counter += 1
        return df
    df = pd.DataFrame(get_lma(df_change,20).stack())
    df.columns = ['ori_change']
    df_test = pd.DataFrame(df['ori_change']).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    ## Jupiter
    factor_test = strongFactorTest(int(start_date), int(end_date))
    result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/测试结果汇总/'
    for col in df_test.columns:
        factor_name = col
        print('Jupiter_' + factor_name + '_' + i)
        df_test = df_test[[col]].unstack().shift(1).stack()
        factor_test.factor_test(df_test, result_path, factor_corr_test=True)
        check_score = factor_test.check_score(factor_test.result_dic['double_group_sort']['ZT_Time'].copy(),
                                     factor_test.result_dic['corr_month'].copy(),
                                     np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']))[1]
        print('check_score:',check_score.loc['score','tot_score'])
        print('IC：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
        print('高corr库中因子：')
        print(factor_test.result_dic['factor_corr_summary'])
        print('均值和中位数: ',factor_test.basic_df['factor'].mean(),"",factor_test.basic_df['factor'].median())
        print('重复值: ',factor_test.result_dic['other_sta'])

    ## Sell
    factor_test = FactorTest(int(start_date), int(end_date),
                             test_sample = 'bt',
                             style_list=['T_o2pre', 'free_turn'],
                             cal_mi = True,
                             buy_type='0931')
    result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/测试结果汇总/'
    for col in df.columns:
        print('Sell_' + factor_name + '_' + i)
        factor_test.factor_test(df_test, result_path, factor_corr_test=True)
        check_score = factor_test.result_dic['check_score_res']
        print('总分:',check_score.loc['score','tot_score'])
        print('CORR：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
        print('高corr库中因子：')
        print(factor_test.result_dic['factor_corr_summary'])
        print('均值与中位数:',factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median())
        print(factor_test.result_dic['max_same_ratio'])
