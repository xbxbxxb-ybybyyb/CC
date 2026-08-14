import pandas as pd
import os

factor_list = ['factor_qyh_n1mtick_20231214_' + str(i) for i in range (1,3)]
df = pd.DataFrame()
for factor in factor_list:
    df[factor] = pd.read_hdf('/data/user/015585/01-因子挖掘/06-SaturnNext/20231214/' + factor + '_20160101_20191231.h5')[factor[7:]]
res = df.corr(method = 'spearman').iloc[-1]
print(res[abs(res)>0.6])
