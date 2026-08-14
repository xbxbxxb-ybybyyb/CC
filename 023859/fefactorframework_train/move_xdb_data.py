import os
import shutil

local_data_path = '/dfs/user/023859/data/xdb_data_lag3_new/neptune/xdb_tick1m/'
public_data_path = '/dfs/group/800463/data/xdb_data_lag3_new/neptune/xdb_tick1m/'

for file in list(os.listdir(local_data_path)):
    if (".pkl" in file) and (file.startswith('2025')):
        shutil.copy(local_data_path + file, public_data_path + file)