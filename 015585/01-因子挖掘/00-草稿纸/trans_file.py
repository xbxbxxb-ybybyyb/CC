import os

import pandas as pd
import shutil
ori_path = '/dfs/group/800463/public/xdb_data_lag3_new/neptune/xdb_tick1m/'
list_file = list(os.listdir(ori_path))
list_file = [x for x in list_file if int(x[:4]) >= 2017]

list_file.sort()
new_path = '/dfs/user/015585/test/zz1000/xdb_tick1m/'
for file in list_file:
    print(file)
    # shutil.copy(ori_path + file, f'{new_path}{file}')
    df = pd.read_pickle(f'{ori_path}{file}')
    df.to_pickle(f'{new_path}{file}', compression='gzip')

