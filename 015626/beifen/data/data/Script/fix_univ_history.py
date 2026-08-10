    # -*- coding: utf-8 -*-
"""
fix Universe
@gzj
"""


from WindPy import w
import pandas as pd
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt
import os 
import datetime as dt
import subprocess
import json

def fix_hist():
    h5_sourse_path = 'S:\\Quant\\data\\md\\CHINA_STOCK\\DAILY\\WIND\\MD_CHINA_STOCK_DAILY_WIND.h5'
    # df = IO.read_data([20090101, 20180703], ['open', 'pre_close', 'amt'], alt = alt)
    root_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\'
    store_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\'
    factor_list = ['SUSPEND', 'OPENUPLIMIT', 'OPENDOWNLIMIT', 'SSO']
    path = root_path +'STPT\\'
    for csv_file in os.listdir(path):
        date = int(csv_file[:-4])
        print(date)
        df = IO.read_data(date, ['open', 'pre_close', 'amt'], alt = h5_sourse_path)
        df.dropna(axis=0,how='any', inplace=True)
        df['SUSPEND'] = df.apply(lambda x: 1 if x.amt > 0 else 0, axis = 1)
        df['SUSPEND'] = df['SUSPEND'].astype(float)

        # OPENDOWNLIMIT
        df['OPENDOWNLIMIT'] = df.apply(lambda x: 0 if x.open <= round(0.9 * x.pre_close , 2)  else 1, axis = 1)
        df['OPENDOWNLIMIT'] = df['OPENDOWNLIMIT'].astype(float)

        #  OPENUPLIMIT
        df['OPENUPLIMIT'] = df.apply(lambda x: 0 if x.open >= round(1.1 * x.pre_close , 2)  else 1, axis = 1)
        df['OPENUPLIMIT'] = df['OPENUPLIMIT'].astype(float)

        #  SSO
        df['SSO'] = df.apply(lambda x: 0 if x.open >= round(x.pre_close * 1.1 , 2) or 
                                        x.amt <= 0 else 1, axis = 1)

        STPT_file = root_path + 'STPT\\' + csv_file
        df_STPT = pd.read_csv(STPT_file)
        df_STPT = df_STPT[df_STPT['STPT']==0.0]
        STPT_list = df_STPT['Ticker'].tolist()
        # print(df)
        for index, row in df.iterrows():
            if index[1] in STPT_list:
                row['SSO'] = 0
        # print('SUSPEND')
        # file_path_suspend = store_path + 'SUSPEND\\'
        # df_suspend = df.drop(columns = ['open', 'pre_close','amt','OPENDOWNLIMIT', 'OPENUPLIMIT', 'SSO'])
        # df_suspend.to_csv(file_path_suspend + str(date) + '.csv')
        # print('Completed')

        # # opendownlimit
        # print('OPENDOWNLIMIT')
        # file_path_opendownlimit = store_path + 'OPENDOWNLIMIT\\'
        # df_opendownlimit = df.drop(columns = ['open', 'pre_close','amt','SUSPEND', 'OPENUPLIMIT', 'SSO'])
        # df_opendownlimit.to_csv(file_path_opendownlimit + str(date) + '.csv')
        # print('Completed')

        # # openuplimit
        # print('OPENUPLIMIT')
        # file_path_openuplimit = store_path + 'OPENUPLIMIT\\'
        # df_openuplimit = df.drop(columns = ['open', 'pre_close','amt','SUSPEND', 'OPENDOWNLIMIT', 'SSO'])
        # df_openuplimit.to_csv(file_path_openuplimit + str(date) + '.csv')
        # print('Completed')

        # SSO
        print('SSO')
        file_path_sso = store_path + 'SSO\\'
        df_sso = df.drop(columns = ['open', 'pre_close','amt','SUSPEND', 'OPENDOWNLIMIT', 'OPENUPLIMIT'])
        df_sso.to_csv(file_path_sso + str(date) + '.csv')
        print('Completed')

        # total
        file_path_total = store_path + 'total\\'
        df.to_csv(file_path_total+str(date)+'.csv')

def fix_sso():
    root_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\'
    store_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\'
    factor_list = ['SUSPEND', 'OPENUPLIMIT', 'OPENDOWNLIMIT', 'SSO']
    path = root_path +'SSO\\'
    STPT_path = root_path + 'STPT\\'
    for csv_file in os.listdir(path):
        date = int(csv_file[:-4])
        print(date)
        STPT_file = STPT_path + csv_file
        df = pd.read_csv(STPT_file)
        df = df[df['STPT']==0.0]
        STPT_list = df['Ticker'].tolist()
        df_sso = pd.read_csv(path + csv_file)
        for index, row in df_sso.iterrows():
            if row['Ticker'] in STPT_list:
                if row['SSO'] == 1:
                    print(row['Ticker'])
                    row['SSO'] = 0
        df_sso.to_csv(path + csv_file)

def filter_stock_code():
    root_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\'
    stock_path = root_path + 'stock_list\\'
    factor_list = ['STPT', 'SUSPEND', 'OPENUPLIMIT', 'OPENDOWNLIMIT', 'SSO']
    for factor in factor_list:
        print(factor)
        path = root_path + factor + '\\'
        for csv_file in os.listdir(path):
            print(csv_file)
            stock_csv = stock_path + csv_file
            df = pd.read_csv(stock_csv)
            stock_list = df['Ticker'].tolist()
            df_csv = pd.read_csv(path + csv_file)
            df_csv = df_csv.set_index('Ticker')
            drop_index = list(set(df_csv.index.values) - set(stock_list))
            df_csv.drop(drop_index, inplace=True)
            df_csv.to_csv(path + csv_file)
if __name__ == '__main__':
    filter_stock_code()