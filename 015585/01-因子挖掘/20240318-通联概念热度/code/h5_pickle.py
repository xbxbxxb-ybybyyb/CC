import pandas as pd
import os

# 把h5文件转存为pickle
## basic
# theme_basic = pd.read_hdf('/data/user/015585/01-因子挖掘/20240318-通联概念热度/file_ori/theme_basicinfo.h5')
# theme_basic.to_pickle('/data/user/015585/01-因子挖掘/20240318-通联概念热度/file_ori/theme_basicinfo.pkl')
## theme_heat
# path1 = '/dfs/user/015585/20240318-通联概念热度/file_ori/theme_heat_h5/'
# list_file_heat = os.listdir(path1)
# for file in list_file_heat:
#     print(file)
#     if '.h5' in file:
#         df = pd.read_hdf(path1 + file)
#         path = '/dfs/user/015585/20240318-通联概念热度/file_ori/theme_heat/'
#         df.to_pickle(path + file[:-3] + '.pkl')
#     elif '.pkl' in file:
#         os.remove(path1 + file)
# correlation
path1 = '/dfs/user/015585/20240318-通联概念热度/file_ori/correlation_h5/'
list_file_heat = os.listdir(path1)
for file in list_file_heat:
    print(file)
    if ('.h5' in file) & (os.path.getsize(path1 + file) > 2048) :
        df = pd.read_hdf(path1 + file)
        path = '/dfs/user/015585/20240318-通联概念热度/file_ori/correlation/'
        df.to_pickle(path + file[:-3] + '.pkl')

