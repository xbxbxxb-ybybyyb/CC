import warnings
warnings.filterwarnings("ignore")

factor_code_path = '/data/user/016700/fuck/' #因子代码路径
root_path = '/dfs/user/016700/fuck_hard/'    #因子保存根目录 


import sys, os
sys.path.insert(4, '/data/user/016700/')
sys.path.insert(4, '/dfs/user/016700/')
sys.path.insert(4, '/data/user/015626/data/share/Code/git_space/commodity_framework/')
sys.path.insert(4, factor_code_path)
from multifactor.IO import IO
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from commodity_framework import *
import matplotlib.pyplot as plt
import os, importlib
import numpy as np
import time
import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 


if __name__ == '__main__':

    holder_1 = pd.read_csv('/data/user/016700/Data/facs/1min_list_v1.csv', index_col = 0).values
    holder_3 = pd.read_csv( '/data/user/016700/Data/facs/3min_list_v1.csv', index_col = 0).values
    holder_5 = pd.read_csv( '/data/user/016700/Data/facs/5min_list_v1.csv', index_col = 0).values
    holder_15 = pd.read_csv( '/data/user/016700/Data/facs/15min_list_v1.csv', index_col = 0).values

    fs_1 = [f for f in os.listdir(factor_code_path) if ('.py' in f) & (f.replace('.py', '') in holder_1)]
    fs_3 = [f for f in os.listdir(factor_code_path) if ('.py' in f) & (f.replace('.py', '') in holder_3)]
    fs_5 = [f for f in os.listdir(factor_code_path) if ('.py' in f) & (f.replace('.py', '') in holder_5)]
    fs_15 = [f for f in os.listdir(factor_code_path) if ('.py' in f) & (f.replace('.py', '') in holder_15)]

    
    try:
        os.makedirs(root_path)
    except:
        pass
    
    ticker_list = ['EC.INE']

    
    his_holder = {}
    his_holder['EC.INE'] = [20230821, 20250501]
        
    # FULL HISTORY
    
    error_holder = []
    for minutes in [1, 3, 5, 15]:
        if minutes == 1:
            for f1 in fs_1:
                importlib.import_module(f1[:-3])
        elif minutes == 3:
            for f3 in fs_3:
                importlib.import_module(f3[:-3])
        elif minutes == 5:
            for f5 in fs_5:
                importlib.import_module(f5[:-3])
        elif minutes == 15:
            for f15 in fs_15:
                importlib.import_module(f15[:-3])
                
        flist = FutureFactor.__subclasses__()
        needed_list = []
        days_past_holder = []
        for f in flist:
            temp_object = f('AU.SHF', minutes)
            needed_list = needed_list + temp_object.required_columns
            days_past_holder.append(temp_object.days_past)
        needed_list = list(set(needed_list))
        dp = np.nanmax(days_past_holder)
        print(pd.Series(days_past_holder).describe())

        
        
        for ticker in ticker_list:
            start_date = int(his_holder[ticker][0])
            end_date = int(his_holder[ticker][-1])
            dc = DataCenter([ticker],  str(minutes) + 'MIN', needed_list, start_date, end_date, dp, parallel_num = 24)
            for f in flist:
                try:
                    #if 'fac_1_df' in f.__name__:
                    if True: 
                        factor_name = f.__name__ + '_' + ticker.upper() + '_' + str(minutes) + 'M'
                        save_path = root_path + ticker + '/' + str(minutes) + '/'
                        ts = TaskRunner(save_factor = True, factor_root_path = save_path)
                        try:
                            os.makedirs(save_path)
                        except:
                            pass
                        
                        if os.path.exists(save_path + '/minute_norm/' +  factor_name + '.h5'):
                            continue
                        
                        start_date = his_holder[ticker][0]
                        end_date = his_holder[ticker][-1]
                        fac = f(ticker, minutes)
                        start_date2 = udt.get_trading_day_offset(start_date, fac.days_past)[0].strftime('%Y%m%d')
                        stime = time.time()
                        
                        factor = ts.run_factor_multi_day(fac, start_date = start_date2, end_date = end_date, variety = ticker, data_center=dc, parallel_num = 24)
                        etime = time.time()
                        usetime = round((etime - stime)/60,3)
                        print(usetime)
                except Exception as e:
                    error_holder.append([factor_name, minutes, ticker, e])
                
            break
        print(error_holder)
        save_pickle(error_holder, 'error_%s.pkl'%minutes)