import numpy as np
import pandas as pd
from gplearn.genetic import SymbolicTransformer
from gplearn.utils import check_random_state
import os
import IO
#
start_date = 20160101
end_date = 20191231
path2_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017TTick_combination/'
function_set = ['add', 'sub', 'mul', 'div',]
def get_factor_df(path2_factor):
    res2 = pd.DataFrame()
    file_list_path2 = os.listdir(path2_factor)
    file_list_path2.sort()
    for file in file_list_path2:
        factor_file = pd.read_hdf(path2_factor + file)
        res2 = pd.concat([res2, factor_file], axis=1)
    res2 = res2.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    return res2

factor_df = get_factor_df(path2_factor)
label_df = IO.read_data([start_date, end_date], alt='/data/group/800463/data/project1_public/factor_lib_v3/sft_update_europa.h5')
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
label_df = filter_label(label_df)
factor_df['label'] = label_df['label_pct_graded']
factor_df = factor_df[~factor_df['label'].isna()]
factor_df = factor_df.fillna(0)
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

gp = SymbolicTransformer(generations=5, # 迭代次数
                         population_size=150, # 种群大小
                         tournament_size=2,# 进化到下一代的数量
                         hall_of_fame=100, # 名人堂，用于生成n_components
                         n_components=50,# 存多少个到_best_programs中,也代表transform后的维度
                         p_crossover = 0.9, # 胜者交叉概率
                         p_subtree_mutation = 0.04, # 胜者子树变异比率
                         p_point_mutation = 0.04,# 突变比率
                         function_set=function_set,
                         init_depth=(2,5),
                         parsimony_coefficient=0.003, # 简约惩罚系数
                         metric='spearman',
                         max_samples=1, verbose=1,
                         random_state=0, n_jobs=1)
gp.fit(factor_df.iloc[:,:-1], factor_df[['label']])
for p in gp._best_programs: # 最终最好的
    print(p)
    print(p.raw_fitness_)