# coding: utf-8
# Author：fengchi863
# Date ：2023/3/24 13:34
"""
孙康康的统计目录下文件的数量
"""

import os

def walkfile(file):
    all_file = []
    from tqdm import tqdm
    for root, dirs, files in tqdm(os.walk(file)):
        for f in files:
            all_file.append(os.path.join(root, f))
    return all_file

all_file = walkfile('/data/user/015614/')
print(len(all_file))