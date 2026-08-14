# coding: utf-8
# Author：fengchi863
# Date ：2025/7/4 8:48

import pandas as pd
from tqdm import tqdm
import os

root_path = '/data/user/015614/junkData/分红养老/'

file_list = os.listdir(root_path)
res_df = pd.DataFrame(columns=['证券名称', '过去3年最高平均股息率'])

for fname in tqdm(file_list):
    if not fname.endswith('xlsx'): continue
    df = pd.read_excel(root_path + fname, index_col=0)
    indicator = df.iloc[-5:-2]['最高股息率'].mean()
    stock_name = df['证券名称'].iloc[0]
    stock_code = df['证券代码'].iloc[0]
    if stock_code.endswith('BJ') or stock_code.startswith('688'): continue
    if indicator > 0.03:
        res_df.loc[stock_code] = [stock_name, indicator]

res_df = res_df.sort_values('过去3年最高平均股息率', ascending=False)
