# coding: utf-8
# Author：fengchi863
# Date ：2023/12/21 11:25

import os
import pandas as pd

week_date = 20240229
root_path = f'/data/user/015614/fcfactor/Metis/factor_{week_date}/'
factor_fpath_list = os.listdir(root_path)
factor_fpath_list = list(filter(lambda x: x.endswith('.py'), factor_fpath_list))
factor_fpath_list.sort()

res = pd.DataFrame(columns=['factor_name', 'factor_type', 'factor_owner', 'factor_explain', 'factor_date', '填充值', '是否对注册制做调整', 'T-1日类别', '逻辑类别', '是否是低耗时因子'])
for factor_idx, factor_fpath in enumerate(factor_fpath_list):
    factor_name = factor_fpath[7:-3]
    with open(root_path + factor_fpath, 'r') as f:
        codes = f.readlines()
    idx = 0
    zcz_times = 0
    for idx, code in enumerate(codes):
        if 'zcz' in code:
            zcz_times += 1
        if '"""' in code:
            break
    factor_explain = codes[idx+1].replace(' ', '').replace('\n', '')
    factor_owner = 'fc'
    res.loc[factor_idx, 'factor_name'] = factor_name
    res.loc[factor_idx, 'factor_owner'] = 'fc'
    res.loc[factor_idx, 'factor_explain'] = factor_explain
    res.loc[factor_idx, 'factor_date'] = week_date
    res.loc[factor_idx, '是否对注册制做调整'] = '否' if zcz_times < 2 else '是'
    res.loc[factor_idx, '是否是低耗时因子'] = '是'

res.to_excel(f'/data/user/015614/junkData/{week_date}_fc_metis.xlsx', index=False)



