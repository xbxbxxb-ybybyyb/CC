# coding: utf-8
# Author：fengchi863
# Date ：2024/1/29 16:22

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from EuropaLocal.TestTool.test1_factor_demo import strongFactorTest

start_date, end_date = 20191001, 20191231
sft = strongFactorTest(start_date, end_date)

fixed_factor_df = pd.read_excel('/data/user/015614/fcfactor/Europa/JupEur冯炽修改_20240126/因子列表_fc.xlsx').set_index('factor_name')
fixed_factor_list = fixed_factor_df.query('是否需要修改=="是"').index.tolist()

old_fpath = '/data/user/015614/factor/Europa_fix_20240126/'
new_fpath = '/data/user/015614/factor/Europa_nofix_20240126/'

for fixed_factor in fixed_factor_list:
    # if fixed_factor != 'fc_trans_order_20230907_9':
    #     continue
    old_df = pd.read_hdf(old_fpath + fixed_factor + '.h5')
    new_df = pd.read_hdf(new_fpath + fixed_factor + '.h5')
    old_df = old_df.reindex(sft.basic_df.index)
    new_df = new_df.reindex(sft.basic_df.index)


    # old_df['datelist'] = old_df.index.get_level_values(0).strftime('%Y%m%d').astype(int)
    # new_df['datelist'] = new_df.index.get_level_values(0).strftime('%Y%m%d').astype(int)
    # old_df = old_df.query('20191001 <= datelist <= 20191231')
    # new_df = new_df.query('20191001 <= datelist <= 20191231')
    fixed_factor_df.loc[fixed_factor, 'pearson相关系数'] = pearsonr(old_df[fixed_factor].values, new_df[fixed_factor].values)[0]
    fixed_factor_df.loc[fixed_factor, 'spearson相关系数'] = spearmanr(old_df[fixed_factor].values, new_df[fixed_factor].values)[0]
    fixed_factor_df.loc[fixed_factor, '不相同值比例'] = (old_df != new_df).sum()[fixed_factor] / len(old_df)

    print(fixed_factor, round(pearsonr(old_df[fixed_factor].values, new_df[fixed_factor].values)[0], 4), round((old_df != new_df).sum()[fixed_factor] / len(old_df), 3))
    fixed_factor_df.to_excel('/data/user/015614/fcfactor/Europa/JupEur冯炽修改_20240126/因子列表_fc.xlsx')