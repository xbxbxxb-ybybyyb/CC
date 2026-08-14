# coding: utf-8
# Author：fengchi863
# Date ：2025/3/19 13:29
import os

# root_path = '/data/user/015614/shared/for_XT/Ceres/logs/'
# prefix_path = f'20250704/' # 整合一个文件夹里的放在外面
#
#
# log_file_list = os.listdir(root_path + prefix_path)
#
# # 开始整合
# lines = list()
# for log_file in log_file_list:
#     with open(root_path + prefix_path + log_file, 'r', encoding='utf-8') as t:
#         line = t.readlines()
#     lines.extend(line)
#
# file_name = f'utt_20250704.log'
# with open(root_path + file_name, 'w', encoding='utf-8') as outfile:
#     for line in lines:
#         outfile.write(line + '\n')
# print(f'保存{file_name}')


root_path = '/data/user/015614/shared/for_XT/Ceres/logs/'
prefix_path = f'20250722/' # 整合一个文件夹里的放在外面


log_file_list = os.listdir(root_path + prefix_path)
log_file_list = list(filter(lambda x: 'ceres' in x, log_file_list))

# 开始整合
lines = list()
for log_file in log_file_list:
    # with open(root_path + prefix_path + log_file, 'r', encoding='utf-8') as t:
    with open(root_path + prefix_path + log_file, 'r', encoding='latin1') as t:
        line = t.readlines()
    lines.extend(line)

file_name = f'ceres_20250722.log'
with open(root_path + file_name, 'w', encoding='utf-8') as outfile:
    for line in lines:
        outfile.write(line + '\n')
print(f'保存{file_name}')

