import pandas as pd
import pickle
import datetime
from QuantFramework import HDFSFileHandler
from xquant.xqutils.xqfile import HDFSFile
from xquant.pyfile import Pyfile
from multifactor.IO import IO
from multifactor.data.utils import *
import os
import datetime as dt 
import pickle
import zipfile
from xquant.xqutils.xqfile import FTPFile
ftp = FTPFile()

def get_sub_df(table,freq):
    print('*'*50)
    print(table,freq)
    prod_path = '/data/group/800080/warehouse/prod/' + table
    
    if freq == 'daily':
        sdate,edate,cdate_list = check_update_date(20191028,20191101)
        df_prod = IO.read_data([sdate,edate],alt=prod_path)
    if freq == 'quartly':
        df_prod = IO.read_data([20180601, 20250101], alt=prod_path)

    return df_prod
    

def main():
    date = str(time.strftime("%Y%m%d"))
    print(date)
    root = '/data/user/015626/slice_data/slice_data_fundamental/'
    slice_path = root + date + '/'
    if not os.path.exists(slice_path):
        os.makedirs(slice_path)
    
    table_list = ['UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5',
                'FDD/CHINA_STOCK/DAILY/WIND/FDD_CHINA_STOCK_DAILY_WIND.h5',
                'FDD/CHINA_STOCK/QUARTERLY/WIND/FDD_CHINA_STOCK_QUARTERLY_WIND.h5',
                'MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                'MD/CHINA_INDEX/DAILY/WIND/MD_CHINA_INDEX_DAILY_WIND.h5',
                'INDUSTRY/CHINA_STOCK/DAILY/WIND/INDUSTRY_CHINA_STOCK_DAILY_WIND.h5',
                'RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',
                'RISK/CHINA_STOCK/DAILY/STYLEFACTOR2/RISK_CHINA_STOCK_DAILY_STYLEFACTOR2.h5',
                'RISK/CHINA_STOCK/DAILY/DESCRIPTOR/RISK_CHINA_STOCK_DAILY_DESCRIPTOR.h5']
            
    qtr_list = ['FDD/CHINA_STOCK/QUARTERLY/WIND/FDD_CHINA_STOCK_QUARTERLY_WIND.h5']
    
    
    for table in table_list:
        freq = 'daily'
        if table in qtr_list:
            freq = 'quartly'
        df_sub = get_sub_df(table,freq)
        df_sub.to_pickle(slice_path  + table.replace('/','_')[:-3] + '.pkl')
    
    upload_path = root + 'data_upload/'
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    with zipfile.ZipFile(upload_path + date + '_sliced_data.zip','w') as z: 
        for i in os.listdir(slice_path):
            z.write(slice_path + i,i)    
    
    
    ftp.uploadFile(upload_path + date + '_sliced_data.zip', '/015626/check_data/fundamental/'+ date + '_sliced_data.zip')
    
    print('finish!')
    

if __name__=='__main__':
    main()
    