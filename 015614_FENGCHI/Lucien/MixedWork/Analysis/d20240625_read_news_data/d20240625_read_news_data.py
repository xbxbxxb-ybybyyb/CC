# coding: utf-8
# Author：fengchi863
# Date ：2024/6/25 17:19

import pandas as pd
import numpy as np
import os

root_path = '/dfs/group/800463/data/news_data/AI_newsdata/'
file_list = os.listdir(root_path)

news_demo = pd.read_pickle(root_path + file_list[0])
check = news_demo[['tags', 'new_tags']]
print(1)