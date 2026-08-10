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

def get_sub_df(table,mode,freq):
    print('*'*50)
    print(table,mode,freq)
    prod_path = '/data/group/800080/warehouse/prod/DATABASE/SUNTIME/' + table + '/' + table + '.h5'
    
    if mode == 'increment':
        if freq == 'daily':
            sdate,edate,cdate_list = check_update_date(20191028,20191101)
            df_prod = IO.read_data([sdate,edate],alt=prod_path)
    if mode == 'overwrite':
        df_prod = IO.read_data([20000101,20250101],alt=prod_path)

    return df_prod
    

def main():
    _,date,_ = check_update_date()
    print(date)
    date = str(date)
    root = '/data/user/015626/slice_data/slice_data_gogoal/'
    slice_path = root + date + '/'
    if not os.path.exists(slice_path):
        os.makedirs(slice_path)
    

    table_list = ['con_forecast_schedule','stock_order3','stock_report_adjustment',
                  'stock_report_number','stock_order2','stock_report_adjustment2','stock_concern_level',
                  'con_stock_deviation3','con_stock_deviation2','con_stock_deviation',
                  'stock_diversity','stock_emotion','stock_report_extremum',
                  'der_report_subtable', 'cmb_report_score_adjust', 'i_organ_score', 'report_author', 
                  'cmb_report_adjust', 'gg_org_list', 'i_report_type', 'author_core_type', 'author_core',
                  'cmb_report_subtable', 'author_pj', 'author_pjhb', 't_great_author',
                  'con_forecast_c2_stk', 'con_forecast_c3_cgb_stk', 'con_forecast_c3_stk', 'con_forecast_cb_stk', 
                  'researcher_info', 't_author_honor','der_report_research','cmb_report_research']
                        
    overwrite_list = ['researcher_info', 'author_core', 'author_core_type', 'i_report_type', 't_author_honor',
                    'i_organ_score', 'gg_org_list', 't_great_author', 'author_pjhb']
                    
    daily_list = list(set(table_list) - set(overwrite_list) - set(['cmb_report_research','der_report_research','author_pj']))
    
    for table in daily_list:
        mode = 'increment' 
        if table in overwrite_list:
            mode = 'overwrite' 
        
        df_sub = get_sub_df(table,mode,'daily')
        df_sub.to_pickle(slice_path  + table + '.pkl')
    
       
    
    upload_path = root + 'data_upload/'
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    with zipfile.ZipFile(upload_path + date + '_sliced_data.zip','w') as z: 
        for i in os.listdir(slice_path):
            z.write(slice_path + i,i)    
    
    
    ftp.uploadFile(upload_path + date + '_sliced_data.zip', '/015626/check_data/gogoal/'+ date + '_sliced_data.zip')
    
    print('finish!')
    

if __name__=='__main__':
    main()
    