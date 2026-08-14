import pandas as pd
import numpy as np
import os
from run_factor_demo import run_factor
# excel
res_excel = pd.read_excel('/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改/因子列表_qyh.xlsx')
basic_file_path = '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
#
date_list = os.listdir('/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改/')
date_list = [x for x in date_list if 'factor_' in x and '.py' not in x]
res = pd.DataFrame()
for date in date_list:
    factor_list_date = os.listdir('/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改/' + date + '/')
    factor_list_date = [x[:-3] for x in factor_list_date  if 'factor_' in x]
    for factor in factor_list_date:
        name = factor[7:]
        print(factor)
        if (type(res_excel[res_excel['factor_name'] == name]['修改原因'].iloc[0]) == str):
            path1 = date + '.' + factor
            m = __import__(path1,fromlist=[factor])
            func = getattr(m, factor)
            factor_type = res_excel[res_excel['factor_name'] == name]['factor_type'].iloc[0]
            factor_df0 = run_factor(func,
                                    name,
                                    factor_type,
                                    20160101, 20191231,
                                    basic_file_path,
                                    '/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改/save_file/', interval_res=False)
            for col in factor_df0:
                print(col, abs(factor_df0[col]).max())
            res[name] = factor_df0[name]
            print(len(res.columns))

res.to_pickle('/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改/save_file/res_ori.pkl')

# df1 = pd.read_pickle('/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改/save_file/res_ori.pkl') # 新
# df2 = pd.read_pickle('/data/user/015585/01-因子挖掘/05-Saturn/20240202因子修改_原始/save_file/res_ori.pkl') # 旧
# import test_factor_demo as sft
# sample_sft = sft.strongFactorTest(20191001, 20191231)
# df1 = df1.reindex(sample_sft.basic_df.index)
# df2 = df2.reindex(sample_sft.basic_df.index)
# res_corr = pd.DataFrame(columns = ['pearson相关系数','不相同值比例'])
# for col in df2.columns:
#     df_col = pd.concat([df1[col],df2[col]],axis=1)
#     df_col.columns = [0,1]
#     corr = df_col.corr(method = 'pearson').iloc[0,1]
#     ratio = len(df_col[df_col[0] != df_col[1]]) / len(df_col)
#     res_corr.loc[col,'pearson相关系数'] = corr
#     res_corr.loc[col,'不相同值比例'] = ratio
#     print(col,"",corr,"",ratio)
# res_corr.to_csv('res_corr.csv')