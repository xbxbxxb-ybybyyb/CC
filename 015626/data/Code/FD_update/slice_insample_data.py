import pandas as pd
import os
from multiprocessing import Pool

root_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/'
target_path = '/data/group/800080/warehouse/insample/LOCAL_DATA/CSV/WIND/MINUTE/'

file_list = ['stock']
for file in file_list:
    
    for pickle_file in os.listdir(os.path.join(root_path, file)):
        now_root_path = os.path.join(root_path, file, pickle_file)
        now_target_path = os.path.join(target_path, file, pickle_file)
        # print('$$$',now_root_path)
        print('***',now_target_path)
        
        
        
        df = pd.read_pickle(now_root_path, compression='gzip')
        data = df[df.index.get_level_values(0) < 20180701]
        if len(data) == 0:
            continue
        data.to_pickle(now_target_path,compression='gzip')
        
# def make_insample(pickle_file):
    # now_root_path = os.path.join(root_path, file, pickle_file)
    # now_target_path = os.path.join(target_path, file, pickle_file)
    # # print('$$$',now_root_path)
    # print('***',now_target_path)
    
    
    
    # df = pd.read_pickle(now_root_path, compression='gzip')
    # data = df[df.index.get_level_values(0) < 20180701]
    # if len(data) == 0:
        # continue
    # data.to_pickle(now_target_path,compression='gzip')
    
# pickle_file_list = os.listdir(os.path.join(root_path, file))
# with Pool(processes = 20) as pool:
    # pool.map(mak_insample, pickle_file_list)