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
copy_path = f'/data/user/015614/fcfactor/fefactorframework/NewNeptune/factor_20250424/'

submit_factors_name_list = [
'fc_n20250424_132',
'fc_n20250424_129',
'fc_n20250424_126',
'fc_n20250424_156',
'fc_n20250424_153',
'fc_n20250424_182',
'fc_n20250424_150',
'fc_n20250424_204',
'fc_n20250424_276',
'fc_n20250424_255',
'fc_n20250424_271',
'fc_n20250424_235',
'fc_n20250424_300',
'fc_n20250424_295',
'fc_n20250424_422',
'fc_n20250424_458',
'fc_n20250424_420',
'fc_n20250424_482',
'fc_n20250424_55',
'fc_n20250424_506',
'fc_n20250424_91',
                            ]

for idx, fname in enumerate(tqdm(submit_factors_name_list)):
    with open(root_path + f'factor_{fname}.py', 'r') as old_code:
        lines = old_code.readlines()

    fname_idx = idx+1+12
    with open(copy_path + f'factor_fc_n20250424_{fname_idx}.py', 'w') as new_code:
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
                # if '20250410' in line:
                #     line = line.replace('20250410', '20250424')
                if 'class' in line:
                    line = f'class factor_fc_n20250424_{fname_idx}(BaseFactor):\n'
                new_code.write(line)