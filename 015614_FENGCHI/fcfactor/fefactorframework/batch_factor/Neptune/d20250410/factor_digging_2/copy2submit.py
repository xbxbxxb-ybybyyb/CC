# coding: utf-8
# Author：fengchi863
# Date ：2024/4/11 15:52

import shutil
import os
from tqdm import tqdm

d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
root_path = f'/data/user/015614/fcfactor/fefactorframework/batch_factor/{strategy_name}/{d_date}/{digging_name}/factor/'
copy_path = f'/data/user/015614/fcfactor/fefactorframework/NewNeptune/factor_20250410/'

submit_factors_name_list = [
    'fc_n20250410_132',
    'fc_n20250410_106',
    'fc_n20250410_128',
    'fc_n20250410_109',
    'fc_n20250410_125',
    'fc_n20250410_123',
    'fc_n20250410_14',
    'fc_n20250410_189',
    'fc_n20250410_17',
    'fc_n20250410_15',
                            ]

for idx, fname in enumerate(tqdm(submit_factors_name_list)):
    with open(root_path + f'factor_{fname}.py', 'r') as old_code:
        lines = old_code.readlines()

    fname_idx = idx+1 + 25
    with open(copy_path + f'factor_fc_n20250410_{fname_idx}.py', 'w') as new_code:
        for line in lines:
            if 'param1, param2' in line:
                parse1 = line.split('=')[1].split('#')[0]
                parse2 = parse1.replace('"', '').replace(' ', '').split(',')
                param1 = parse2[0]
                param2 = int(parse2[1])

            else:
                if 'param1' in line or 'param2' in line:
                    line = line.replace('param1', f'"{param1}"')
                    line = line.replace('param2', f'{param2}')
                if '20250403' in line:
                    line = line.replace('20250403', '20250410')
                if 'class' in line:
                    line = f'class factor_fc_n20250410_{fname_idx}(BaseFactor):\n'
                new_code.write(line)