# coding: utf-8
# Author：fengchi863
# Date ：2025/3/19 13:29

root_path = '/data/user/013551/forXT/Saturn/log/'
prefix_path = '20250319/'

log_date = 20241008
file_name = f'docker-saturn-{log_date}'
log_path_list = [
    root_path + prefix_path + f'{file_name}-sh.log',
    root_path + prefix_path + f'{file_name}-sz.log',
]

lines = list()
for log_path in log_path_list:
    with open(log_path, 'r', encoding='utf-8') as t:
        line = t.readlines()
    lines.extend(line)

with open(root_path + file_name + '.log', 'w', encoding='utf-8') as outfile:
    for line in lines:
        outfile.write(line, + '\n')
