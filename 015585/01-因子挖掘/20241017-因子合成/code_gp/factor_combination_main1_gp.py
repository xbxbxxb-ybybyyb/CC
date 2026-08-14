import numpy as np
import pandas as pd
import gplearn
from gplearn.genetic import SymbolicTransformer
import os
import IO
from test import metric_corr_ic_,_mul_10,_div_2,_square
import time
#
'''
生成基于多重数据的因子:目前因子都是单一数据源，将高频和低频因子组合可以得到新的因子，作为补充
输入：开发中IC尚可的高频/低频因子
输出：结合后的高频/低频因子
改进：fit函数考虑和库中因子相关性
'''
start_date = 20160101
end_date = 20191231
path2_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017TTick_combination/'
path1_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/回测报告/20241017TTick_combination/'
def get_factor_df(path2_factor):
    res2 = pd.DataFrame()
    file_list_path2 = os.listdir(path2_factor)
    file_list_path2.sort()
    for file in file_list_path2:
        if 'compare_1' not in file and 'compare_2' not in file and 'compare_3' not in file and 'compare_len_half12' not in file and 'compare_len_h2t' not in file:
            ic_file = pd.read_pickle(path1_factor + file.replace('.h5','.pkl'))['corr_sta'].loc['corr_tot', 'value']
            if abs(ic_file) <= 0.1:
                factor_file = pd.read_hdf(path2_factor + file)
                res2 = pd.concat([res2, factor_file], axis=1)
    res2 = res2.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    return res2
def factor_std(factor_df, std_method):
    if std_method == 'zscore':
        factor_df = factor_df.apply(lambda x : (x - x.mean()) / x.std())
    elif std_method == 'minmax':
        factor_df = factor_df.apply(lambda x : (x - x.min()) / (x.max() - x.min()))
    return factor_df
factor_df = get_factor_df(path2_factor)
print(f'共计{len(factor_df.columns)}个基础因子')
factor_df_ori = factor_df.copy()
# factor_df = factor_std(factor_df, 'zscore')
label_df = IO.read_data([start_date, end_date], alt='/data/group/800463/data/project1_public/factor_lib_v3/sft_update_europa_filter_20160101_20191231.h5')
def filter_label(df):
    time_interval = [93000000, 143000000]
    last_is_zt = False
    first_is_zt = False
    open_is_zt = False
    Flag_SH_SZ = None
    last_buy_rise = 0.025,
    low_open = -0.05
    after_not_ul_len = 10
    low_price = 2,
    df['first_is_zt'] = (df['high_price'] >= (df['trigger_price']))
    time_interval_filter = (df['ZT_Time'] >= time_interval[0]) & (df['ZT_Time'] <= time_interval[1])
    open_is_zt_filter = df['open_is_zt'] == open_is_zt
    low_open_filter = df['T_o2pre'] >= low_open
    after_not_ul_len_filter = df['after_not_ul_len'] > after_not_ul_len
    low_price_filter = df['pre_close'] >= low_price
    first_is_zt_filter = df['first_is_zt'] == first_is_zt
    last_is_zt_filter = df['last_is_zt'] == int(last_is_zt) if last_is_zt is not None else (
                df['last_is_zt'] == df['last_is_zt'])
    last_buy_rise_filter = df['last_buy_rise'] <= last_buy_rise
    sh_sz_filter = df['Flag_SH_SZ'] == int(Flag_SH_SZ) if Flag_SH_SZ is not None else (
                df['Flag_SH_SZ'] == df['Flag_SH_SZ'])
    all_filter = time_interval_filter & open_is_zt_filter & low_open_filter & after_not_ul_len_filter & low_price_filter \
                 & first_is_zt_filter & last_is_zt_filter & last_buy_rise_filter & sh_sz_filter
    df = df[all_filter]
    return df
factor_df = factor_df.reindex(index = label_df.index)
factor_df['label'] = label_df['value']
factor_df = factor_df[~factor_df['label'].isna()]
factor_df = factor_df.fillna(0)
#
def drop_inf(factor_df):
    for col in factor_df.columns:
        column_data = factor_df[col]
        finite_data = column_data[np.isfinite(column_data)]
        if len(finite_data) > 0:
            max_value = finite_data.max()
            min_value = finite_data.min()
            factor_df[col] = column_data.replace(np.inf, max_value)
            factor_df[col] = column_data.replace(-np.inf, min_value)
    return factor_df
factor_df = drop_inf(factor_df)
#
label_df = label_df[~label_df['value'].isna()]
# 自定义算子
mul_10 = gplearn.functions.make_function(function = _mul_10,name = 'mul10',arity = 1)
div_2 = gplearn.functions.make_function(function = _div_2,name = 'div2',arity = 1)
square = gplearn.functions.make_function(function = _square,name = 'square',arity = 1)
# 自定义评估
metric_corr_ic = gplearn.fitness.make_fitness(metric_corr_ic_, greater_is_better=True)

function_set = ['add', 'sub', 'mul', 'div', 'sqrt', 'log', 'abs', 'inv', 'max', 'min', mul_10, div_2, square]
gp = SymbolicTransformer(generations=7, # 迭代次数
                         population_size=5000, # 种群大小
                         tournament_size=4,# 进化到下一代的数量
                         hall_of_fame=80, # 名人堂，用于生成n_components
                         n_components=80,# 存多少个到_best_programs中,也代表transform后的维度
                         p_crossover = 0.9, # 胜者交叉概率
                         p_subtree_mutation = 0.04, # 胜者子树变异比率
                         p_point_mutation = 0.04,# 突变比率
                         function_set=function_set,
                         init_depth=(2,6),
                         parsimony_coefficient=0.001, # 简约惩罚系数
                         # metric='spearman',
                         metric = metric_corr_ic,
                         max_samples=1, verbose=1,
                         random_state=0, n_jobs=30)

gp.fit(factor_df.iloc[:,:-1], factor_df[['label']])
# df_statistics = pd.DataFrame(gp.run_details_)
for p in gp._best_programs[0:5]: # 最终最好的
    print(p)
    print(p.raw_fitness_)
# abs(sub(X49, add(X97, X195)))
# 0.11216155773625512

for i in [49,97,195]:
    print(i,factor_df.columns[i],factor_df.iloc[:,i].mean(),factor_df.iloc[:,i].std(),
          f'ic={pd.read_pickle(path1_factor + factor_df.columns[i] + ".pkl")["corr_sta"].loc["corr_tot","value"]}')
# factor_df['36tmp'] = np.where(np.abs(factor_df.iloc[:,36]) > 0.001, np.log(np.abs(factor_df.iloc[:,36])), 0.)
# factor_df['test'] = (1/(factor_df.iloc[:,60] + 10 * factor_df.iloc[:,15])).fillna(0)
# print(metric_corr_ic_(factor_df['label'],factor_df['test'],np.ones(len(factor_df))))
# factor_df[['label']].corrwith(factor_df['test'], method='spearman')

# metric_corr_ic_