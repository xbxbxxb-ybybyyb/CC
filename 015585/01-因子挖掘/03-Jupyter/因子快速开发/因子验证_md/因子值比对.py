import os
import pandas as pd
import numpy as np

factor_name_list = os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/因子验证_md/factor/')
factor_name_list = [x.replace('.py','') for x in factor_name_list if '.py' in x and 'factor_' in x and 'run_factor' not in x]
factor_name_list.sort()

result_path1 = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/因子验证_md/factor_value_file/'
result_path2 = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_filter/'

date = '20170110'
res = {}
for factor in factor_name_list[:10]:
    df1= pd.read_hdf(f'{result_path1}{factor}.h5').loc[pd.Timestamp(date)]
    df2 = pd.read_hdf(f'{result_path2}{factor.replace("factor_", "")}.h5').loc[pd.Timestamp(date)]
    delta = abs(df1[factor.replace('factor_','')] - df2[factor.replace('factor_','')]).max()
    res[factor] = [df1, df2, delta]
    print(factor,'', delta)
