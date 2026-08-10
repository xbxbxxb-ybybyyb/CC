import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk
from xquant.factordata import FactorData

kind = 'IF'
corr_threshold = 0.6

pathlist = glob.glob('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_factors/minute_norm/*.h5' % kind) \
         + glob.glob('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_gp/minute_norm/*.h5' % kind)
factor_all_insample_list = []
def get_factor(path):
    return pd.read_hdf(path).loc['20180101':'20200630']
with Pool(24) as pool:
    factor_all_insample_list = pool.map(get_factor, pathlist)
factor_all_insample = pd.concat(factor_all_insample_list, axis = 1)

report_full = pd.read_csv('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/factor_report/%s_factors/%s_factors_20180101_20200630/%s_factors_20180101_20200630.csv'%(kind,kind,kind), index_col=0)\
                .append(pd.read_csv('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/factor_report/%s_gp/%s_gp_20180101_20200630/%s_gp_20180101_20200630.csv'%(kind,kind,kind), index_col=0))
report_full.index.name = 'factor_name'

corrdf = pd.DataFrame()
factorslist = factor_all_insample.columns
count = 0
for i in range(len(factorslist) - 1):
    for j in range(i + 1, len(factorslist)):
        corrdf.loc[count, 'factor1'] = factorslist[i]
        corrdf.loc[count, 'factor2'] = factorslist[j]
        corrdf.loc[count, 'corr'] = factor_all_insample[factorslist[i]].corr(factor_all_insample[factorslist[j]])
        count = count + 1
corrdf = corrdf.sort_values(by = 'corr', ascending=True)

print('select high corr factors')
bigcorr = corrdf[corrdf['corr'] > corr_threshold]
if len(bigcorr) == 0:
    print('all factors are in low correlation')
bigcorrlist = list(set(bigcorr.factor1.tolist()) | set(bigcorr.factor2.tolist()))
lowcorrlist = list(set(factorslist) - set(bigcorrlist))
print(len(lowcorrlist))

# 将相关性高的因子按夏普率从大到小排序
all_factor_report = report_full.reset_index()
df2bigcorrdf = all_factor_report[all_factor_report.factor_name.isin(bigcorrlist)]
df2bigcorrdf = df2bigcorrdf.sort_values(by='IC-1min', ascending=False)

waitlist = df2bigcorrdf.factor_name.tolist()

print('start select factors whose correlation is high')
inlist = []
for x in waitlist:
    maxcorr = 0
    for y in lowcorrlist:
        corr = factor_all_insample[x].corr(factor_all_insample[y])
        maxcorr = max(maxcorr, corr)
    if maxcorr <= corr_threshold:
        lowcorrlist.append(x)
        inlist.append(x)
print(len(lowcorrlist))

pd.DataFrame(lowcorrlist,columns=['factor_name']).set_index('factor_name').join(report_full['IC-1min'],how = 'left').to_csv('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/factor_report/%s_corr_%f.csv'%(kind, corr_threshold))