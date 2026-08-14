# @Time : 2020/7/20 10:25
# @Author : Zhichen Lu
# @File : load_updown_limit.py

import pandas as pd
import os
import datetime
h5_path = "/data/group/wdb_h5/WIND/universe_complete/universe_complete.h5"
up_out_path = '/data/group/800319/junkData/IntraFactorModel/DataForTplusN/up_limit/'
down_out_path = '/data/group/800319/junkData/IntraFactorModel/DataForTplusN/down_limit/'


def clear(path):
    file_list = os.listdir(path)
    for file_name in file_list:
        os.remove(path + file_name)


clear(up_out_path)
clear(down_out_path)

if not os.path.exists(up_out_path):
    os.mkdir(up_out_path)
if not os.path.exists(down_out_path):
    os.mkdir(down_out_path)

# file_list = os.listdir(up_out_path)
# for file_name in file_list:
#     os.remove(up_out_path+file_name)
#     print(file_name,'remove')


up_info = pd.read_hdf(h5_path,'OPENUPLIMIT')
up_info = up_info.reset_index().pivot_table(index='dt',columns='Ticker',values='OPENUPLIMIT')
up_info.index = [int(x.strftime('%Y%m%d')) for x in up_info.index]
up_info.columns = [int(x[:-3]) for x in up_info.columns]
up_info = up_info.loc[20130101:]
check = up_info[2912]
for x in up_info.columns:
    if os.path.exists(up_out_path+'%d.pkl'%x):
        continue
    pd.to_pickle(up_info[x],up_out_path+'%d.pkl'%x)
    print(x,'up done')

down_info = pd.read_hdf(h5_path,'OPENDOWNLIMIT')
down_info = down_info.reset_index().pivot_table(index='dt',columns='Ticker',values='OPENDOWNLIMIT')
down_info.index = [int(x.strftime('%Y%m%d')) for x in down_info.index]
down_info.columns = [int(x[:-3]) for x in down_info.columns]
down_info = down_info.loc[20130101:]
for x in down_info.columns:
    if os.path.exists(down_out_path+'%d.pkl'%x):
        continue
    pd.to_pickle(down_info[x],down_out_path+'%d.pkl'%x)
    print(x,'down done')

######################################

"""
import pandas as pd
import numpy as np
from dataApi.stockList import clean_stock_list
import os

pool_info_path = '/data/group/800319/junkData/IntraFactorModel/StrongPoolInfo/FactorBackTestPool/'
if not os.path.exists(pool_info_path):
    os.mkdir(pool_info_path)
stock_list = clean_stock_list('HS300',no_ST=True,start_date=20130101,end_date=20200805)
isin = stock_list.sum()
stock_list = stock_list[isin[isin>0].index]
for col in stock_list.columns:
    pd.to_pickle(stock_list[col],pool_info_path+'%d.pkl'%col)
    print(col,'done')
"""
