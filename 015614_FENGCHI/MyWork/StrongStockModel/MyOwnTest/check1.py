# coding: utf-8
# Author：fengchi863
# Date ：2020/7/27 14:27

'''
测试下来发现，每个时间点的因子数量不一样，所以说可能内部的每个因子的逻辑是不同的
'''
from StrongStockModel.System.LoadFactor.factor_utils import *
import pandas as pd

fix_factor_list = fetch_factor_list()
fix1000 = []
fix1030 = []
fix1100 = []
fix1300 = []
fix1330 = []
fix1400 = []
fix1430 = []

count_dict = {'930':  0,
              '1000': 0,
              '1030': 0,
              '1100': 0,
              '1130': 0,
              '1300': 0,
              '1330': 0,
              '1330': 0,
              '1400': 0,
              '1430': 0}

for factor in fix_factor_list:
    if '1000' in factor:
        count_dict['1000'] += 1
        fix1000.append(factor)
    elif '1030' in factor:
        count_dict['1030'] += 1
        fix1030.append(factor)
    elif '1100' in factor:
        count_dict['1100'] += 1
        fix1100.append(factor)
    elif '1300' in factor:
        count_dict['1300'] += 1
        fix1300.append(factor)
    elif '1330' in factor:
        count_dict['1330'] += 1
        fix1330.append(factor)
    elif '1400' in factor:
        count_dict['1400'] += 1
        fix1400.append(factor)
    elif '1430' in factor:
        count_dict['1430'] += 1
        fix1430.append(factor)
    else:
        pass

fix1000 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1000))
fix1030 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1030))
fix1100 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1100))
fix1300 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1300))
fix1330 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1330))
fix1400 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1400))
fix1430 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1430))

fix_factor_list = list(set(fix1000).intersection(set(fix1030)).intersection(set(fix1100)).intersection(set(fix1300)).
     intersection(set(fix1330)).intersection(set(fix1400)).intersection(set(fix1430)))

# from StrongStockModel.conf.path_config import root_path
# with pd.ExcelWriter(root_path + 'check.xlsx') as writer:
#     pd.DataFrame(fix1000).to_excel(writer, 'fix1000')
#     pd.DataFrame(fix1030).to_excel(writer, 'fix1030')
#     pd.DataFrame(fix1100).to_excel(writer, 'fix1100')
#     pd.DataFrame(fix1300).to_excel(writer, 'fix1300')
#     pd.DataFrame(fix1330).to_excel(writer, 'fix1330')
#     pd.DataFrame(fix1400).to_excel(writer, 'fix1400')
#     pd.DataFrame(fix1430).to_excel(writer, 'fix1430')
# print(count_dict)
print(len(fix_factor_list))