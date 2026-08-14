import pandas as pd
import os
import IO
from xquant.thirdpartydata.factordata import FactorData

s = FactorData()
'''
1、是否漏表:字典表没有做H5文件
2、数据是否全
    1）日均数据量：未发现问题
    2）早期数据样例核查：未发现问题
3、格式是否有问题
'''
root_path = '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/'
# 是否漏表
true_list = ['DWD_EXP_RESEARCHREPORT',
            'DWD_EXP_REPORTRATINGADJ',
            'DWD_EXP_REPORTTARGETPRICEADJ',
            'DWD_EXP_RESEARCHREPORTADJ',
            'EXP_ORALIST',
            'DWD_EXP_RPTRATINGCOMPARE',
            'DWD_EXP_RPTGOGOALRATING',
            'DWD_EXP_REPORTTYPE',
            'DWD_EXP_FORECASTSECU',
            'DWD_EXP_FORECASTSCHEDULE',
            'DWD_EXP_FORECASTSCHEDULE',
            'DWD_EXP_FORECASTSECUDERIVED']
for i in true_list:
    if i not in os.listdir(root_path):
        print(i,'未在root_path中')
# 数据是否全
## 日均数据量2016以后
res_full = {}
for i in os.listdir(root_path):
    if i not in  ['EXP_ORALIST', 'DWD_EXP_RPTRATINGCOMPARE', 'DWD_EXP_REPORTTYPE', 'DWD_EXP_RPTGOGOALRATING']:
        df = IO.read_data([20250430, 20250604], alt = f'{root_path}{i}/{i}.h5')
        print(i)
        res_full[i] = df.groupby(['dt']).count()
    else:
        df = pd.read_hdf(f'{root_path}{i}/{i}.h5')

print(res_full.keys())

## 日均数据量2012
res_2012 = {}
for i in os.listdir(root_path):
    if i not in  ['EXP_ORALIST', 'DWD_EXP_RPTRATINGCOMPARE', 'DWD_EXP_REPORTTYPE', 'DWD_EXP_RPTGOGOALRATING']:
        df = IO.read_data([20120101, 20151231], alt = f'{root_path}{i}/{i}.h5')
    else:
        df = pd.read_hdf(f'{root_path}{i}/{i}.h5')
    print(i)
    res_2012[i] = df.groupby(['dt']).count()
print(res_2012.keys())
tmp = res_2012['DWD_EXP_FORECASTSECU']

# 数据是否准确
res_detail = {}
for i in os.listdir(root_path):
    if i not in  ['EXP_ORALIST', 'DWD_EXP_RPTRATINGCOMPARE', 'DWD_EXP_REPORTTYPE', 'DWD_EXP_RPTGOGOALRATING']:
        df = IO.read_data([20160101, 20160131], alt = f'{root_path}{i}/{i}.h5')
    else:
        df = pd.read_hdf(f'{root_path}{i}/{i}.h5')
    print(i)
    res_detail[i] = df
tmp = res_detail['DWD_EXP_FORECASTSECU']

# 字典表
'''
DWD_EXP_RPTRATINGCOMPARE 未在root_path中
DWD_EXP_RPTGOGOALRATING 未在root_path中
DWD_EXP_REPORTTYPE 未在root_path中
'''
i = 'DWD_EXP_RPTRATINGCOMPARE'
tmp = pd.read_hdf(f'{root_path}{i}/{i}.h5')