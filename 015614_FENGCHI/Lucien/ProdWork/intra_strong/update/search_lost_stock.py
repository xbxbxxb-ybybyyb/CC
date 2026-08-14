# coding: utf-8
# Author：fengchi863
# Date ：2024/2/8 15:28

import pandas as pd

tupo_fpath = '/data/group/800463/日内强势股/cpp_实盘分析记录/每日突破/每日突破_20240219_prod.xlsx'
tupo = pd.read_excel(tupo_fpath, sheet_name='每日订单')

jup_tupo_stk_list = list(tupo.query('actionSource == "JupiterN"')['stockcode'].unique())
eur_tupo_stk_list = list(tupo.query('actionSource == "JupiterNew"')['stockcode'].unique())

jup = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_2024-02-19_prod.xlsx', sheet_name='因子耗时', index_col=0).index.tolist()
eur = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_2024-02-19_prod.xlsx', sheet_name='因子耗时New', index_col=0).index.tolist()

print(list(set(eur_tupo_stk_list).difference(set(eur))))
print(list(set(jup_tupo_stk_list).difference(set(jup))))