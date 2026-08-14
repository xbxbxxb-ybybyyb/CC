'''
1、主要对低频数据的因子 和 高频数据的因子进行合成
2、合成方法：
step1:标准化(2种)
step2:
    IC/ICIR等
    等权
    随机公式：目前先测试乘法
3、输出物：
    合成后的IC，score，相关性等
    和原来因子的相关性
'''
import pandas as pd
import numpy as np
import os
from test_factor_demo import strongFactorTest
from joblib import Parallel, delayed
import IO
import itertools
# para
start_date = 20160101
end_date = 20191231
path1_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017T-1_combination/'
path1_test = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/回测报告/20241017T-1_combination/'
path2_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017TTick_combination/'
path2_test = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/回测报告/20241017TTick_combination/'
list_std_method = ['zscore','minmax']

def get_data(path1_factor, path2_factor, start_date, end_date):
    # 取低频因子数据
    res1 = pd.DataFrame()
    file_list_path1 = os.listdir(path1_factor)
    file_list_path1.sort()
    for file in file_list_path1[:30]:
        factor_file = pd.read_hdf(path1_factor + file)
        res1 = pd.concat([res1,factor_file], axis = 1)
    res1 = res1.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    # 取高频因子数据
    res2 = pd.DataFrame()
    file_list_path2 = os.listdir(path2_factor)
    file_list_path2.sort()
    for file in file_list_path2[:30]:
        factor_file = pd.read_hdf(path2_factor + file)
        res2 = pd.concat([res2,factor_file], axis = 1)
    res2 = res2.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    return res1,res2
# 因子标准化:zscore and minmax
def factor_std(res1, res2, std_method):
    if std_method == 'zscore':
        res1 = res1.apply(lambda x : (x - x.mean()) / x.std())
        res2 = res2.apply(lambda x : (x - x.mean()) / x.std())
    elif std_method == 'minmax':
        res1 = res1.apply(lambda x : (x - x.min()) / (x.max() - x.min()))
        res2 = res2.apply(lambda x : (x - x.min()) / (x.max() - x.min()))
    return res1, res2
# 量纲识别，有标准化模块暂时可以不要
def get_unit_T_1(factor_name):
    if not 'nodiv' in factor_name:
        return 'pct'
    else:
        for i in ['cv','cct','kurt','skew','m2m','pos']:
            if i in factor_name:
                return 'pct'
        for i in ['high','open','low','close']:
            if i in factor_name:
                return 'price'
        for i in ['']:
            if i in factor_name:
                return 'amt'
# 合成方法 & 因子测试主函数
def ic_combinate(factor1, factor2, res1, res2):
    ic1 = pd.read_pickle('{}{}.pkl'.format(path1_test, factor1))['corr_sta'].loc['corr_tot', 'value']
    ic2 = pd.read_pickle('{}{}.pkl'.format(path2_test, factor2))['corr_sta'].loc['corr_tot', 'value']
    res = ic1 * res1[factor1] + ic2 * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'ic', factor2)])
def ir_combinate(factor1, factor2, res1, res2):
    ir1 = pd.read_pickle('{}{}.pkl'.format(path1_test, factor1))['corr_sta'].loc['corr_month_std', 'value']
    ir2 = pd.read_pickle('{}{}.pkl'.format(path2_test, factor2))['corr_sta'].loc['corr_month_std', 'value']
    res = ir1 * res1[factor1] + ir2 * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'ir', factor2)])
def equal_combinate(factor1, factor2, res1, res2):
    ic1 = pd.read_pickle('{}{}.pkl'.format(path1_test, factor1))['corr_sta'].loc['corr_tot', 'value']
    ic2 = pd.read_pickle('{}{}.pkl'.format(path2_test, factor2))['corr_sta'].loc['corr_tot', 'value']
    res = np.sign(ic1) * res1[factor1] + np.sign(ic2) * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'equal', factor2)])
def mult_combinate(factor1, factor2, res1, res2):
    res = res1[factor1] * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'mult', factor2)])

def factor_test_parallel(factor1, factor2, combine_method, result_path1, result_path2,):
    if '{}*{}*{}'.format(factor1, combine_method, factor2) in list_del:
        print('{}*{}*{}:已存在文件'.format(factor1, combine_method, factor2))
        return
    func = dic_combine_method[combine_method]
    factor_df = func(factor1, factor2, res1, res2)
    factor_df.to_pickle('{}{}*{}*{}.pkl'.format(result_path1, factor1, combine_method, factor2))
    factor_test = strongFactorTest(start_date, end_date, cal_mi=None)
    for col in factor_df.columns:

        factor_test.factor_test(factor_df[[col]], result_path2,
                                factor_corr_test=True, generate_pdf=False)
        check_score = factor_test.result_dic['check_score_res']
        print(col)
        print('总分:', check_score.loc['score', 'tot_score'])
        print('CORR:', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
    return

# 输出结果
res1, res2 = get_data(path1_factor, path2_factor, start_date, end_date)
dic_combine_method = {
    'ic': ic_combinate,
    'ir': ir_combinate,
    'equal': equal_combinate,
    'mult': mult_combinate
}

list_del = []
for std_method in list_std_method:
    res1, res2 = factor_std(res1, res2, std_method)
    for combine_method in dic_combine_method.keys():
        result_path1 = '/dfs/user/015585/01_factor_develop_store/fast_factor_combination/europa/20241017_ttick_t_1/h5/{}/{}/'.format(std_method, combine_method)
        result_path2 = '/dfs/user/015585/01_factor_develop_store/fast_factor_combination/europa/20241017_ttick_t_1/factor_test/{}/{}/'.format(std_method, combine_method)
        if not os.path.exists(result_path1):
            os.makedirs(result_path1)
        if not os.path.exists(result_path2):
            os.makedirs(result_path2)
        for file in result_path2:
            list_del.append(file.replace('.pkl', ''))
        factor_df_list = Parallel(n_jobs=30)(delayed(factor_test_parallel)(factor1, factor2, combine_method, result_path1, result_path2) \
                                             for factor1, factor2 in list(itertools.product(list(res1.columns), list(res2.columns)))
                                             )




