# coding: utf-8
# Author：fengchi863
# Date ：2023/11/1 15:10

import gzip
import os
log_path = '/data/user/013551/forXT/log/local_log/2023-10-31_17-54-37/'
file_list = os.listdir(log_path)

dic = {}
for file_name in file_list:
    dat = file_name[:8]
    if dat not in dic.keys():
        dic[dat] = [file_name]
    else:
        dic[dat] = dic[dat] + [file_name]

for dat in dic.keys():
    dat_str = str(dat)[:4] + '-' + str(dat)[4:6] + '-' + str(dat)[6:]
    all_lines = ''
    for file_name in dic[dat]:
        log_file = open(log_path + file_name)
        log_lines = log_file.readlines()
        for line in log_lines:
            all_lines += line
    f = open(log_path + f'EventDrivenStrategy-{dat_str}.log', 'w')
    f.writelines(all_lines)
    f.close()