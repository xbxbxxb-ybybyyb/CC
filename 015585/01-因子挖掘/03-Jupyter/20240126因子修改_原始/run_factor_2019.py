import pandas as pd
import numpy as np
import os
from run_factor_demo_parallel_new import run_factor
# excel
res_excel = pd.read_excel('/data/user/015585/01-因子挖掘/03-Jupyter/20240126因子修改/因子列表_qyh.xlsx')
basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
#
date_list = os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/20240126因子修改_原始/')
date_list = [x for x in date_list if 'factor_' in x and '.py' not in x]
res = pd.DataFrame()
for date in date_list:
    factor_list_date = os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/20240126因子修改_原始/' + date + '/')
    factor_list_date = [x[:-3] for x in factor_list_date  if 'factor_' in x]
    for factor in factor_list_date:
        name = factor[7:]
        print(factor)
        if (type(res_excel[res_excel['factor_name'] == name]['修改内容'].iloc[0]) == str) & \
                (name not in  ['qyh_ttick_20231116_8','qyh_torder_20231102_2','qyh_ttick_20231130_10']):
            path1 = date + '.' + factor
            m = __import__(path1,fromlist=[factor])
            func = getattr(m, factor)
            factor_type = res_excel[res_excel['factor_name'] == name]['factor_type'].iloc[0]
            factor_df0 = run_factor(func,
                                    name,
                                    factor_type,
                                    ## TTickab,TOrder,TTransaction,T-1_factor,MarketIndTTick,TOrder_TTickab
                                    20190101, 20191231,
                                    basic_file_path,
                                    '/data/user/015585/01-因子挖掘/03-Jupyter/20240126因子修改_原始/save_file/', interval_res=False)
            res[name] = factor_df0[name]
            # print(res.head(5))
res.to_pickle('/data/user/015585/01-因子挖掘/03-Jupyter/20240126因子修改_原始/save_file/res_ori.pkl')