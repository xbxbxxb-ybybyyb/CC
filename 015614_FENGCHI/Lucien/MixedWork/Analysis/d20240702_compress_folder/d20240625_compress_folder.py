# coding: utf-8
# Author：fengchi863
# Date ：2024/7/2 9:38

import zipfile
import os
from tqdm import tqdm
import pandas as pd

# 压缩文件
# def compress_folder(folder_path, zip_file_path):
#     with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         for root, dirs, files in os.walk(folder_path):
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_in_zip_path = os.path.relpath(file_path, os.path.dirname(folder_path))
#                 zipf.write(file_path, file_in_zip_path)
#
#
# # 使用函数压缩文件夹
# folder_to_compress = '/data/group/800463/日内强势股/log_parse/日志拆分/'  # 要压缩的文件夹路径
# zip_file_name = '日志拆分.zip'  # 压缩后的ZIP文件名
# compress_folder(folder_to_compress, zip_file_name)

# 复制文件
# rsync -av /data/group/800463/日内强势股/log_parse/日志拆分 /arch1/group/800463/日内强势股/log_parse/日志拆分

# 解压缩文件
# file_list = os.listdir('/dfs/group/800463/data/news_data/datayes_content/')
# zip_list = list(filter(lambda x: x[-4:] == '.zip', file_list))
# for zip in tqdm(zip_list):
#     print(zip)
#     os.system(f'unzip /dfs/group/800463/data/news_data/datayes_content/{zip} -d /dfs/group/800463/data/news_data/datayes_content/ && rm /dfs/group/800463/data/news_data/datayes_content/{zip}')
# check = pd.read_hdf('/dfs/group/800463/data/news_data/datayes_content/20200720.h5')

#%% 测试解压文件是否正常
from dataApi import tradeDate
from dataApi.sendInfo import send_message
date_list = tradeDate.get_date_range(20180101, 20201231)
# date_list = [20190715, 20200928] # 20190715 20200928 这两个有问题
for _dat in date_list:
    if os.path.exists(f'/dfs/group/800463/data/news_data/datayes_content/{_dat}.h5'):
        try:
            check = pd.read_hdf(f'/dfs/group/800463/data/news_data/datayes_content/{_dat}.h5')
            print(_dat, check.shape, check.iloc[0, 1][:10])
        except:
            send_message(f'{_dat}有问题')
            print(f'{_dat} is wrong!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    else:
        print(f'{_dat}缺失')

