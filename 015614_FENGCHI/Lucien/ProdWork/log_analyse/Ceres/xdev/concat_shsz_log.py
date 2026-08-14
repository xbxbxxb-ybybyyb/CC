# coding: utf-8
# Author：fengchi863
# Date ：2025/3/19 13:29
import os

root_path = '/data/user/013551/forXT/Ceres/log//'
ceres_type = 'type1'
prefix_path = f'20250526_1/{ceres_type}/' # 整合一个文件夹里的放在外面

date_list = list(set(map(lambda x: x[:8], os.listdir(root_path + prefix_path))))
for log_date in date_list:
    log_file_list = list(set(filter(lambda x: x[:8] == log_date, os.listdir(root_path + prefix_path))))

    # 开始整合
    lines = list()
    for log_file in log_file_list:
        with open(root_path + prefix_path + log_file, 'r', encoding='utf-8') as t:
            line = t.readlines()
        lines.extend(line)

    file_name = f'{log_date}_{ceres_type}.log'
    with open(root_path + file_name, 'w', encoding='utf-8') as outfile:
        for line in lines:
            outfile.write(line + '\n')
    print(f'保存{file_name}')

