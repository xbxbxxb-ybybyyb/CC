# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from itertools import product
import os
from run_factor_demo_parallel_new import run_factor
from test_factor_demo import strongFactorTest
from xquant.factordata import FactorData
import IO
import re
def get_corr_factor(df):
    r = ''
    for i in df.index:
        r = r+str(i)+':'+str(round(df.loc[i,'in_score'],2))+";"
    return r

def is_first_chinese(text):
    return bool(re.match(r'[\u4e00-\u9fff]+', text))
def rank_(data_):
    data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
    return data_r
# 读取同花顺-点击量占比 & 同花顺-自选股占比，构造原始数据/相对rank/5日diff/5日diff相对rank/5日均值/5日均值相对rank 6种因子
def data_prepare_ths1(name): # 读取同花顺点击量、自选股占比，预处理,name = 'thsindex1''thsindex4'
    name_dic = {'clicknum':'thsindex1',
                'savestocknum':'thsindex4'}
    name_csv = name_dic[name]
    df = pd.read_csv('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/' + '{}.csv'.format(name_csv))
    df['code'] = df['code'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
    df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df.columns = ['dt', 'Ticker', 'name', name]
    df = df[['dt','Ticker',name]]
    df = df.set_index(['dt', 'Ticker'])
    return df
def calculate_type(df,name,type): # type : ori,diff5,avg5
    if type == 'ori':
        pass
    elif type == 'diff5':
        df[name] = df[name] - df[name].unstack().shift(5).stack()
    elif type == 'avg5':
        df[name] = df[name].unstack().rolling(5,1).mean().stack()
    else:
        print('type错误,type={}'.format(type))
        raise TypeError
    return df
def calculate_rank(df,name,is_rank):
    if is_rank == 'value':
        pass
    elif is_rank == 'rank':
        df[name] = rank_(df[name])
    else:
        print('rank入参错误,rank={}'.format(is_rank))
        raise TypeError
    return df
def calculate_factor_ths1(df,name,type,is_rank): # 因子计算方式
    factor_name = name + '_' + type + '_' + is_rank
    df_type = calculate_type(df.copy(),name,type)
    df_final = calculate_rank(df_type.copy(),name,is_rank)
    df_final = df_final.rename(columns = {name:factor_name})
    return df_final
print('开始计算同花顺点击量和个股留存因子')
name_list = ['clicknum','savestocknum']
type_list = ['ori','diff5','avg5']
rank_list = ['value','rank']
start_date = '20160101'
end_date = '20191231'
for name in name_list:
    df_ths1 = data_prepare_ths1(name)
    for type, is_rank in product(type_list,rank_list):
        factor_name = name + '_' + type + '_' + is_rank
        print(factor_name)
        df_final = calculate_factor_ths1(df_ths1.copy(),name,type,is_rank).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        # print(df_final.head(3))
        df_final.to_pickle('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/file/' + factor_name + '.pkl')

# 读取同花顺人气csv，同样对每一列构造原始数据/相对rank/5日diff/5日diff相对rank/5日均值/5日均值相对rank 6种因子
print('开始计算同花顺人气因子')
def data_prepare_ths2():
    df = pd.read_csv('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/同花顺人气--2019.csv')
    df['Ticker'] = df['证券代码'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['dt'] = df['日期'].apply(lambda x: pd.Timestamp(x))
    df['Ticker'] = df['Ticker'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df = df.set_index(['dt', 'Ticker'])
    df = df.drop(['日期','证券代码','证券简称'],axis=1)
    return df
def calculate_factor_ths2(df,col,type,is_rank): # 因子计算方式
    factor_name = col + '_' + type + '_' + is_rank
    df_type = calculate_type(df.copy(),col,type)
    df_final = calculate_rank(df_type.copy(),col,is_rank)
    df_final = df_final.rename(columns = {col:factor_name})
    return df_final[[factor_name]]
type_list = ['ori','diff5','avg5']
rank_list = ['value','rank']
start_date = '20190101'
end_date = '20191231'
df_ths2 = data_prepare_ths2()
for col in df_ths2.columns:
    for type, is_rank in product(type_list, rank_list):
        factor_name = col + '_' + type + '_' + is_rank
        print(factor_name)
        df_final = calculate_factor_ths2(df_ths2.copy(), col, type, is_rank).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        # print(df_final.head(5))
        df_final.to_pickle('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/file/' + factor_name + '.pkl')

# 对金工行业merge上述因子，groupby后得到行业均值作为行业因子值
jg_indu = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for sss/tmp/20240307_中信行业分类.pkl')# 读取金工行业
factor_list = list(os.listdir('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/file/'))
print('开始与金工行业整合')
for factor in factor_list:
    factor_name = factor.replace('.pkl','')
    print(factor_name)
    jg_indu[factor_name] = pd.read_pickle('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/file/' + factor)[factor_name] # 以金工行业为基准
jg_indu.to_pickle('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/res/jg_indu_factor_ori.pkl') # 所有原始个股因子值
print('开始计算行业因子值')
tmp_jg_indu = jg_indu.reset_index().set_index(['dt','final_indu_number'])

for factor in factor_list:
    factor_name = factor.replace('.pkl', '')
    print(factor_name)
    indu_factor_value = jg_indu.groupby(['dt','final_indu_number'])[factor_name].mean() # 按金工行业/日期的因子值
    tmp_jg_indu[factor_name + '_indu'] = indu_factor_value
res_jg_indu = tmp_jg_indu.reset_index().set_index(['dt','Ticker'])
res_jg_indu.to_pickle('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/res/jg_indu_factor_final.pkl') # 所有原始个股加行业因子值
# #
print('开始行业因子测试')
res_jg_indu = pd.read_pickle('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/res/jg_indu_factor_final.pkl')
res = pd.DataFrame(columns = ['start_date','end_date','IC','score','high_corr_factor','repeat_ratio'])
for col in res_jg_indu.columns:
    if (col.endswith('_indu')) & ('自选' not in col):
        print(col)
        if is_first_chinese(col[0]): # 中文字符开头的是同花顺人气csv，只有2019年
            start_date = 20190101
            end_date = 20191231
        else:
            start_date = 20160101
            end_date = 20191231
        def factor_test(start_date, end_date, IO, return_fillna_dic=False):
            if return_fillna_dic:
                # 返回因子为nan时的填充值
                return {col: 0, 'data': ['MD']}
            df_res = res_jg_indu[[col]]
            return df_res
        basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
        factor_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/factor_h5/'
        factor_df0 = run_factor(func=factor_test,
                                factor_name=col,
                                factor_type='T-1_factor',
                                start_date=start_date,
                                end_date=end_date,
                                basic_file_path=basic_file_path,
                                result_path=factor_path,
                                interval_res=False)
        df = pd.read_hdf(factor_path + col + '.h5')
        result_path = '/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/20240314_叠加金工行业计算热度/factor_report/'
        factor_test = strongFactorTest(start_date, end_date, cal_mi=None)
        factor_test.factor_test(df[[col]], result_path,
                                factor_corr_test=True, generate_pdf=False)
        check_score = factor_test.result_dic['check_score_res']
        res.loc[col,'start_date'] = start_date
        res.loc[col,'end_date'] = end_date
        res.loc[col,'IC'] = factor_test.result_dic['corr_sta'].loc['corr_tot', 'value']
        res.loc[col,'score'] = check_score.loc['score', 'tot_score']
        res.loc[col,'high_corr_factor'] = get_corr_factor(factor_test.result_dic['factor_corr_summary'])
        res.loc[col,'repeat_ratio'] = factor_test.result_dic['other_sta'].iloc[0,2]
        print(res.loc[col])