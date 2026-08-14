# coding: utf-8
# Author：fengchi863
# Date ：2025/5/26 17:10

import pandas as pd

log_path = '/data/user/013551/forXT/Ceres/log/'
# date_list = [20241008, 20241009, 20241010, 20241011, 20241014]
date_list = [20250526]
# date_list = [20250227, 20250228, 20250303, 20250304, 20250305, 20250306, 20250307, 20250310]
univ = 'xdev'
type = 'type2'

for _dat in date_list:
    log_fpath = log_path + f'{_dat}_{type}.log'
    log_file = open(log_fpath)
    log_lines = log_file.readlines()
    log_lines = list(filter(lambda x: 'algo' in str(x) and 'INFO' in str(x), log_lines))
    order_line = list()
    order_num = 0
    for line in log_lines:
        if line.lower().find(' order ') > 0:
            order_line.extend([line])
            order_num += 1
        # if 'Cancel' in line:
        #     order_line.extend([line])
        #     order_num += 1

    file_name = f'{_dat}_{type}_cancel.log'
    with open(log_path + file_name, 'w', encoding='utf-8') as outfile:
        for line in order_line:
            outfile.write(line + '\n')

    print(f'==========={_dat}_{type}===========')
    print(f'{order_num}')