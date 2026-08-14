# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 15:40

import os
import re
from tqdm import tqdm
from itertools import product

d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
factor_name = None
root_path = f'/data/user/015614/fcfactor/fefactorframework/batch_factor/{strategy_name}/{d_date}/{digging_name}/'
basic_factor_fpath = root_path + 'factor_fc_ttickab_n20240808_1.py'

with open(basic_factor_fpath) as basic_code:
    lines = basic_code.readlines()

for line in lines:
    if 'class' in line:
        factor_name = re.findall(r'class (.*?)\(BaseFactor\)', line)[0]
        break

factor_name_prefix = '_'.join(factor_name.split('_')[:-1])

param_list = [[f'Buy{x}Price' for x in range(1, 6)],
              ['WeightedAvgBidPx', 'TotalValueTrade', 'TotalVolumeTrade', 'TotalOfferQty', 'TotalBidQty', 'NumTrades'],
              [5, 10, 15, 20, 25, 30],
              [0.01, 0.02, 0.03, 0.04, 0.05]]
param_list = list(product(*param_list))

def generate_param_line(param_tuple):
    param_num = len(param_tuple)
    line_left = ', '.join([f'param{idx}' for idx in range(1, param_num + 1)])
    line_right = ''
    for param in param_tuple:
        if type(param) in [int, float]:
            line_right += str(param) + ', '
        if type(param) in [str]:
            line_right += f'"{param}", '
    return line_left + ' = ' + line_right[:-2] + ' # 配置超参数'

for idx, param_tuple in enumerate(param_list):
    print(idx)
    new_factor_name = f'{factor_name_prefix}_{idx + 1}'
    os.makedirs(root_path + f'factor/', exist_ok=True)
    with open(root_path + f'factor/{new_factor_name}.py', 'w') as new_code:
        for line in lines:
            if '# 配置超参数' in line:
                new_code.write(generate_param_line(param_tuple) + '\n')
            elif 'class' in line:
                new_code.write(f'class {new_factor_name}(BaseFactor):\n')
            else:
                new_code.write(line)

