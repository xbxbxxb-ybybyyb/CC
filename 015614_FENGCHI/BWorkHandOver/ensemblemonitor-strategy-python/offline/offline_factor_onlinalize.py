# @Time : 2021/2/9 8:45
# @Author : Zhichen Lu
# @File : offline_factor_onlinalize.py
import pandas as pd
import numpy as np
import os,gc
from multiprocessing import Pool
from tqdm import tqdm

date_list = [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113,
             20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122,
             20210125, 20210126, 20210127]
time_list = [1000,1030,1100,1300,1330,1400,1430]

fake_online_factor_path = '/data/group/800319/fake_realtime_path/'
realtime_factor_path = '/data/group/800002/realtime/alpha/x_day_lib/'

if not os.path.exists(fake_online_factor_path):
    os.mkdir(fake_online_factor_path)

offline_factor_path = '/data/group/800002/alpha_factor/lib/x_factor_lib/'


for date in date_list:
    if not os.path.exists(f'{fake_online_factor_path}{date}/'):
        os.mkdir(f'{fake_online_factor_path}{date}/')
        for time_point in time_list:
            os.mkdir(f'{fake_online_factor_path}{date}/{time_point}/')



def factor_transfer(factor_name):
    already_exist = True
    for date in date_list:
        time_point = int(factor_name[3:7])
        online_corresponding_path = f'{realtime_factor_path}{date}/{time_point}/'
        fake_corresponding_path = f'{fake_online_factor_path}{date}/{time_point}/'
        if os.path.exists(online_corresponding_path+factor_name):
            if not os.path.exists(fake_corresponding_path+factor_name):
                already_exist=False
    if not already_exist:
        factor = pd.read_pickle(offline_factor_path + factor_name)
        for date in date_list:
            time_point = int(factor_name[3:7])
            online_corresponding_path = f'{realtime_factor_path}{date}/{time_point}/'
            fake_corresponding_path = f'{fake_online_factor_path}{date}/{time_point}/'
            if os.path.exists(online_corresponding_path + factor_name):
                if not os.path.exists(fake_corresponding_path + factor_name):
                    factor.loc[[str(date)]].to_pickle(fake_corresponding_path+factor_name)
        del factor
        gc.collect()
    return True
factor_list = os.listdir(offline_factor_path)
factor_list = list(filter(lambda x : x.startswith('Fix'),factor_list))
bar = tqdm(total=len(factor_list))
def update(*param):
    bar.update()
    if bar.last_print_n==len(factor_list):
        bar.close()

res = {}
pool = Pool(40)
for fac in factor_list:
    res[fac] = pool.apply_async(factor_transfer,(fac,),callback=update)

pool.close()
pool.join()

for fac in res:
    try:
        a = res[fac].get()
    except:
        print(fac)