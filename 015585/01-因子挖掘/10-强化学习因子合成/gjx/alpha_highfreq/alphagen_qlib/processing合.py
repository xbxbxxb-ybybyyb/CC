
import pandas as pd
import os
from tqdm import tqdm
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
data = []
all_label = []
for i in range(5):
    df = pd.read_pickle(f'./high_data{i+1}.pkl')
    # label = pd.read_pickle(f'./label{i+1}.pkl')
    # label = pd.DataFrame(label, columns=['label'])
    # if i ==1:
    #     ddf = df.loc[('2018-10-24', '603996.SH'), :]
    #     df = pd.concat((df, ddf))  # 这一步做不了？？ 太大了？在细分里面做
    #     ddf = label.loc[('2018-10-24', '603996.SH'), :]
    #     label = pd.concat((label, ddf))
    df = df.sort_index(level=None)
    # label = label.sort_index(level=None)
    data.append(df)
    # all_label.append(label)

df = pd.concat(data)
df.to_pickle('./high_data.pkl')
print(df)
#
# all_label = pd.concat(all_label)
# # 20181024只有499支股票，补一行进去【随便复制一个】
# all_label.to_pickle('./label.pkl')
# print(all_label)
#

# import numpy as np
# data = []
# for i in range(1,6):
#     arr = np.load(f'./high_data{i}.npy')
#     data.append(data)
# data = np.concatenate(data)
# print(data.shape)
# np.save(data,'high_data.npy')

# 最后存下来的是["Date", "stock_codes", "features"]为索引，MDTime是列