import datetime as dt
import pandas as pd
import scipy.io as sio
import os
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multiprocessing import Pool, Process, Manager
from multifactor.data.utils import *
import logging
from log import Log
import multifactor.utility.dt as tdt
import pickle
import pyodbc
from dateutil.parser import parse

start_date, end_date, cdate_list = check_update_date(20050515,20191015)
root = 'A:\\weiyc\\data\\Reuters\\CSV\\TRE\\'

conn = pyodbc.connect(driver='{SQL Server}', server='qai97-qadirectcloud-default-0j.database.windows.net',
                      database='qai', uid='0j.sujian.zhi', pwd='j#Bd5kDQzYMouvcO')
cursor = conn.cursor()

TRE_tables = ['TREBrokers','TREAnalysts','TRECode','TRECode2']#'TRECoverage
cdate_list = ['111']
for table in TRE_tables:
    table_csv_path = root + table
    if not os.path.exists(table_csv_path):
        os.makedirs(table_csv_path)
    for date in cdate_list:
        print(table,date)
        sql = 'SELECT * FROM [dbo].[' + table + ']'
        print(sql)
        cursor.execute(sql)
        rs = cursor.fetchall()
        if(len(rs) == 0):
            continue

        content_list = []
        for content in rs:
            content_list.append(list(content))

        df = pd.DataFrame(content_list)

        info = cursor.description
        column_names = []
        for i in range(len(info)):
            column_names.append(info[i][0])
        df.columns = column_names

        df.to_csv(os.path.join(table_csv_path,table + '.csv'), encoding='utf-8')

