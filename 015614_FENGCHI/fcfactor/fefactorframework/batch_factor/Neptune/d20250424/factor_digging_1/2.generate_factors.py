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
basic_factor_fpath = root_path + 'factor_fc_n20250424_1.py'

with open(basic_factor_fpath) as basic_code:
    lines = basic_code.readlines()

for line in lines:
    if 'class' in line:
        factor_name = re.findall(r'class (.*?)\(BaseFactor\)', line)[0]
        break

factor_name_prefix = '_'.join(factor_name.split('_')[:-1])

param_list = [[
    # 'BUY_VALUE_EXLARGE_ORDER', 'SELL_VALUE_EXLARGE_ORDER',
    #                'BUY_VALUE_LARGE_ORDER', 'SELL_VALUE_LARGE_ORDER',
    #                'BUY_VALUE_MED_ORDER', 'SELL_VALUE_MED_ORDER', 'BUY_VALUE_SMALL_ORDER',
    #                'SELL_VALUE_SMALL_ORDER', 'BUY_VOLUME_EXLARGE_ORDER',
    #                'SELL_VOLUME_EXLARGE_ORDER', 'BUY_VOLUME_LARGE_ORDER',
    #                'SELL_VOLUME_LARGE_ORDER', 'BUY_VOLUME_MED_ORDER',
    #                'SELL_VOLUME_MED_ORDER', 'BUY_VOLUME_SMALL_ORDER',
    #                'SELL_VOLUME_SMALL_ORDER', 'TRADES_COUNT', 'BUY_TRADES_EXLARGE_ORDER',
    #                'SELL_TRADES_EXLARGE_ORDER', 'BUY_TRADES_LARGE_ORDER',
    #                'SELL_TRADES_LARGE_ORDER', 'BUY_TRADES_MED_ORDER',
    #                'SELL_TRADES_MED_ORDER', 'BUY_TRADES_SMALL_ORDER',
    #                'SELL_TRADES_SMALL_ORDER', 'VOLUME_DIFF_SMALL_TRADER',
    #                'VOLUME_DIFF_SMALL_TRADER_ACT', 'VOLUME_DIFF_MED_TRADER',
                   'VOLUME_DIFF_MED_TRADER_ACT', 'VOLUME_DIFF_LARGE_TRADER',
                   'VOLUME_DIFF_LARGE_TRADER_ACT', 'VOLUME_DIFF_INSTITUTE',
                   'VOLUME_DIFF_INSTITUTE_ACT', 'VALUE_DIFF_SMALL_TRADER',
                   'VALUE_DIFF_SMALL_TRADER_ACT', 'VALUE_DIFF_MED_TRADER',
                   'VALUE_DIFF_MED_TRADER_ACT', 'VALUE_DIFF_LARGE_TRADER',
                   'VALUE_DIFF_LARGE_TRADER_ACT', 'VALUE_DIFF_INSTITUTE',
                   'VALUE_DIFF_INSTITUTE_ACT', 'S_MFD_INFLOWVOLUME',
                   'NET_INFLOW_RATE_VOLUME', 'S_MFD_INFLOW_OPENVOLUME',
                   'OPEN_NET_INFLOW_RATE_VOLUME', 'S_MFD_INFLOW_CLOSEVOLUME',
                   'CLOSE_NET_INFLOW_RATE_VOLUME', 'S_MFD_INFLOW', 'NET_INFLOW_RATE_VALUE',
                   'S_MFD_INFLOW_OPEN', 'OPEN_NET_INFLOW_RATE_VALUE', 'S_MFD_INFLOW_CLOSE',
    #                'CLOSE_NET_INFLOW_RATE_VALUE', 'TOT_VOLUME_BID', 'TOT_VOLUME_ASK',
    #                'MONEYFLOW_PCT_VOLUME', 'OPEN_MONEYFLOW_PCT_VOLUME',
    #                'CLOSE_MONEYFLOW_PCT_VOLUME', 'MONEYFLOW_PCT_VALUE',
    #                'OPEN_MONEYFLOW_PCT_VALUE', 'CLOSE_MONEYFLOW_PCT_VALUE',
    #                'S_MFD_INFLOWVOLUME_LARGE_ORDER', 'NET_INFLOW_RATE_VOLUME_L',
    #                'S_MFD_INFLOW_LARGE_ORDER', 'NET_INFLOW_RATE_VALUE_L',
    #                'MONEYFLOW_PCT_VOLUME_L', 'MONEYFLOW_PCT_VALUE_L',
    #                'S_MFD_INFLOW_OPENVOLUME_L', 'OPEN_NET_INFLOW_RATE_VOLUME_L',
    #                'S_MFD_INFLOW_OPEN_LARGE_ORDER', 'OPEN_NET_INFLOW_RATE_VALUE_L',
    #                'OPEN_MONEYFLOW_PCT_VOLUME_L', 'OPEN_MONEYFLOW_PCT_VALUE_L',
    #                'S_MFD_INFLOW_CLOSEVOLUME_L', 'CLOSE_NET_INFLOW_RATE_VOLUME_L',
    #                'S_MFD_INFLOW_CLOSE_LARGE_ORDER', 'CLOSE_NET_INFLOW_RATE_VALU_L',
    #                'CLOSE_MONEYFLOW_PCT_VOLUME_L', 'CLOSE_MONEYFLOW_PCT_VALUE_L',
    #                'BUY_VALUE_EXLARGE_ORDER_ACT', 'SELL_VALUE_EXLARGE_ORDER_ACT',
    #                'BUY_VALUE_LARGE_ORDER_ACT', 'SELL_VALUE_LARGE_ORDER_ACT',
    #                'BUY_VALUE_MED_ORDER_ACT', 'SELL_VALUE_MED_ORDER_ACT',
    #                'BUY_VALUE_SMALL_ORDER_ACT', 'SELL_VALUE_SMALL_ORDER_ACT',
    #                'BUY_VOLUME_EXLARGE_ORDER_ACT', 'SELL_VOLUME_EXLARGE_ORDER_ACT',
    #                'BUY_VOLUME_LARGE_ORDER_ACT', 'SELL_VOLUME_LARGE_ORDER_ACT',
    #                'BUY_VOLUME_MED_ORDER_ACT', 'SELL_VOLUME_MED_ORDER_ACT',
    #                'BUY_VOLUME_SMALL_ORDER_ACT', 'SELL_VOLUME_SMALL_ORDER_ACT'
               ],
                  [1, 2, 3, 6, 10, 20, 30, 40, 60, 90, 120, 240]]
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

