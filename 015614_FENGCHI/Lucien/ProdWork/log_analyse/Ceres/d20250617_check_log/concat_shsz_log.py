# coding: utf-8
# Author：fengchi863
# Date ：2025/3/19 13:29
import os

# root_path = '/data/user/013551/forXT/Ceres/logs/'
root_path = '/data/user/015614/shared/for_XT/Ceres/logs/'
# ceres_type = 'type1'
prefix_path = f'20250618/' # 整合一个文件夹里的放在外面

log_file_list = list(os.listdir(root_path + prefix_path))
lines = []

for log_file in log_file_list:
    with open(root_path + prefix_path + log_file, 'r', encoding='utf-8') as t:
        line = t.readlines()
    lines.extend(line)

file_name = f'20250516.log'
with open(root_path + file_name, 'w', encoding='utf-8') as outfile:
    for line in lines:
        outfile.write(line + '\n')
print(f'保存{file_name}')

