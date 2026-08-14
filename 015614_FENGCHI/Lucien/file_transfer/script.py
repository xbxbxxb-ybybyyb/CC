# coding: utf-8
# Author：fengchi863
# Date ：2022/6/28 16:57

import shutil
import os
from tqdm import tqdm


def dir_copy(src_path, target_path):
    # 获取文件夹里面内容
    _file_list = os.listdir(src_path)
    # 遍历列表
    for file in tqdm(_file_list):
        print(file)
        # 拼接路径
        path = os.path.join(src_path, file)
        tar_path = target_path
        # 判断是文件夹还是文件
        if os.path.isdir(path):
            tar_path = os.path.join(tar_path, file)
            os.makedirs(tar_path, exist_ok=True)
            # 递归调用copy
            dir_copy(path, tar_path)
        else:
            # 不是文件夹则直接进行复制
            with open(path, 'rb') as rstream:
                container = rstream.read()
                path1 = os.path.join(target_path, file)
                if os.path.exists(path1): continue  # 如果已经有这个文件就不再复制一次
                with open(path1, 'wb') as wstream:
                    wstream.write(container)
    else:
        print('复制完成！')

# 复制基础数据
# src_addr = '/data/group/800442/800319/junkData/daily'
# des_addr = '/data/user/015614/easy_transfer/basic_data/daily/'
# shutil.copyfile(src_addr, des_addr)

"""
# 复制一个文件夹的内容到另一个文件夹
src_addr = '/data/group/800442/800319/junkData/daily/'
des_addr = '/data/user/015614/easy_transfer/basic_data/daily/'
file_list = os.listdir(src_addr)
for file_name in tqdm(file_list):
    shutil.copy(src_addr + file_name, des_addr)
"""

# 递归复制整个文件夹（包括文件内的文件夹）
# src_addr = '/data/group/800442/800319/Afengchi'
# src_addr = '/data/group/800442/800319/dolphinDB'
# src_addr = '/data/group/800442/800319/zczyDataAnalysis'

# src_addr = '/data/group/800442/800319/junkData/ZCZY'
# des_addr = '/data/user/015614/easy_transfer/data/group/800442/800319/junkData/ZCZY'

# src_addr = '/data/group/800319/strategy_local_path3'
# des_addr = '/data/user/015614/easy_transfer/data/group/strategy_local_path3'
# dir_copy(src_addr, des_addr)

# src_addr = '/data/group/800442/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten.pkl'
# des_addr = '/data/user/015614/easy_transfer/data/group/800442/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten.pkl'
# os.makedirs(os.path.dirname(des_addr))
# shutil.copyfile(src_addr, des_addr)

#%% 迁移就团队个人NAS文件夹到金融工程团队fengc文件夹
# src_addr = '/data/user/015614'
# des_addr = '/data/group/800463/fengc/015614'
# os.makedirs(des_addr, exist_ok=True)
# dir_copy(src_addr, des_addr)

#%% 相隔了一天，更新昨天最新的basic_data
# src_addr = '/data/user/015614/easy_transfer/basic_data'
# des_addr = '/data/group/800463/fengc/015614/easy_transfer/basic_data'
# os.makedirs(des_addr, exist_ok=True)
# dir_copy(src_addr, des_addr)

# for proj in ['AWorkHandOver', 'BWorkHandOver', 'MyWork', 'Lucien']:
#     src_addr = f'/data/user/015614/{proj}'
#     des_addr = f'/data/group/800463/fengc/015614/{proj}'
#     os.makedirs(des_addr, exist_ok=True)
#     dir_copy(src_addr, des_addr)

#%% 转移到arch1盘 低速盘
# src_addr = '/data/group/800463/fengc/015614'
# des_addr = '/arch1/user/015614'
# os.makedirs(des_addr, exist_ok=True)
# dir_copy(src_addr, des_addr)

# 从group盘转移到user盘
# src_addr = '/data/group/800463/fengc/015614/easy_transfer'
# des_addr = '/data/user/015614/easy_transfer'
# os.makedirs(des_addr, exist_ok=True)
# dir_copy(src_addr, des_addr)

# src_addr = '/data/group/800463/fengc/015614/easy_transfer'
# des_addr = '/data/user/015614/easy_transfer'
# os.makedirs(des_addr, exist_ok=True)
# dir_copy(src_addr, des_addr)

# 还没有运行
# src_addr = '/data/group/800463/日内强势股/'
# des_addr = '/arch1/user/015614/日内强势股/'
# src_addr = '/data/group/800463/日内强势股/实盘分析记录/'
# des_addr = '/arch1/group/800463/日内强势股/实盘分析记录/'
# src_addr = '/data/user/015614/easy_transfer/'
# des_addr = '/dfs/user/015614/easy_transfer/'
# os.makedirs(des_addr, exist_ok=True)
# dir_copy(src_addr, des_addr)


# ##% ！！！！！！！！！！删除！！！！！！！！！！路径注意！！！！！！！！！！！！！
# for dirpath, dirnames, filenames in os.walk('/data/group/800463/日内强势股'):
#     if '模型数据' in dirpath.split('/'):
#         print(f'delete {dirpath}')
#         shutil.rmtree(dirpath)
#     if '行情数据' in dirpath.split('/'):
#         print(f'delete {dirpath}')
#         shutil.rmtree(dirpath)
#     if '日志拆分' in dirpath.split('/'):
#         print(f'delete {dirpath}')
#         shutil.rmtree(dirpath)

for dirpath, dirnames, filenames in os.walk('/data/user/015614/Zeus/'):
    print(dirnames)
    shutil.rmtree(dirpath)