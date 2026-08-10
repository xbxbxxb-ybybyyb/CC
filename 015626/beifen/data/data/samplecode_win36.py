# -*- coding: utf-8 -*-
from dataapi_win36 import Client
import pandas as pd
import numpy as np
import datetime as dt
import pandas as pd
import scipy.io as sio  
import os
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import os
from multiprocessing import Pool, Process, Manager
from multifactor.data.utils import *
import logging
from log import Log
import multifactor.utility.dt as tdt


def ticker_match(ticker_num): # jit slow
    try:
        ticker_num = int(ticker_num)
        suffix = '.SH' if ticker_num>=600000 else '.SZ'
        pre_fill = (6 - len(str(ticker_num)))*'0'
        ticker = pre_fill + str(ticker_num) + suffix
        return ticker
    except Exception as e:
        return ticker_num

def get_data(date):
    client = Client()
    client.init('76218fd5ca1f579488c9a3d6dcad28019671055015df9f97717cd330fddefae6')
    
    # 获取一天某段时间内的新闻信息
    # url1 = '/api/subject/getNewsInfoByTime.json?field=&beginTime=&endTime=&newsBeginDate='
    # url1 = '/api/subject/getNewsBody.json?field=&newsID='
    url1 = '/api/subject/getNewsRelatedScore.json?field=&newsID=&secID=&ticker=&partyID='
    url1 = url1 + date+'&assetClass=E&equType=&beginDate=&endDate='
    code, result = client.getData(url1)
    if code==200:
        rst = result.decode()
        rst = eval(rst)
        if not 'data' in rst:
            print('no data')
            raise Exception
        rst = rst['data']
        columns_list = set()
        for row in rst:
            columns_list = columns_list | set(row.keys())
        columns_list = list(columns_list)
        columns_list.sort()
        rows = []
        for row in rst:
            tmp_list = []
            for key in columns_list:
                if not key in row:
                    tmp_list.append(np.nan)
                else:
                    if key == 'ticker':
                        tmp_list.append(ticker_match(row[key]))
                    else:
                        tmp_list.append(row[key])
            rows.append(tmp_list)
        df = pd.DataFrame(rows, columns=columns_list)
        # df.set_index('ticker', inplace = True)
        # df.drop('tradeDate', axis = 1, inplace= True)
        # df.drop('secID', axis = 1, inplace = True)
        # print(df)
        
        df.to_csv('Z:\\warehouse\\test\\u_quant_local\\getNewsRelated\\'+date+'.csv',sep=',', encoding='utf_8_sig')
    else:
        print (code)
        print (result)        


def save_pickle(csv_list):
    df_list = []
    for fname in csv_list:
        print(fname[-12:-4])
        df = pd.read_csv(fname, encoding='utf_8_sig')
        df['dt'] = dt.datetime.strptime(fname[-12:-4],'%Y%m%d')
        df.set_index(['dt', 'ticker'], inplace=True)
        print(df)
        df_list.append(df)
    rst_df = pd.concat(df_list)
    rst_df.sort_index(inplace = True)
    col_list = rst_df.columns
    print(rst_df)
    for col in col_list:
        with open('Z:\\warehouse\\test\\u_quant_h5\\uqer_professional_factors_' + col + '.pickle', 'wb') as file:
            pickle.dump(rst_df[col], file)



def csv2h5(csv_list,h5_path,table_name,operation,min_size=0):
    fail_list = []   
    if operation=='create':
        print('Create new h5: '+h5_path)
        if os.path.exists(h5_path):
            print('Remove existing h5:'+h5_path)
            os.remove(h5_path) 
    elif operation == 'append':
        print('Append to: '+ h5_path)
    with pd.HDFStore(h5_path) as h5_store:
        print('check date list takes some time')
        if table_name in list(h5_store.root._v_groups.keys()):
              dt_lst = list(set(h5_store.select_column(table_name, 'dt')))
        else:
            dt_lst = []
        for fname in csv_list:
            print(fname[-12:-4])
            print('read')
            dat = pd.read_csv(fname, encoding='utf_8_sig')
            columns = dat.columns.values
            dat['dt'] = dt.datetime.strptime(fname[-12:-4],'%Y%m%d')
            dat.set_index(['dt', 'ticker'], inplace=True)

            if len(dat)<min_size or dat.empty:
                print(dat)
                print('csv data too little!')
                fail_list.append(fname+'@amount_fail')
            else:
                if operation == 'append':      
                    curr_date = list(set(dat.index.get_level_values('dt')))[0]
                    print(curr_date)
                    if curr_date in dt_lst:
                        print('Already exists: '+str(curr_date))
                        # dummy_id = h5_store.remove(table_name,'dt=curr_date')
                        # print('Append: '+str(curr_date))
                        continue
                dat['MktValue'] = dat['MktValue'].astype('int64')
                print('insert')
                h5_store.append(table_name,dat,data_columns=True)
                print('done')


    print('data loading complete!')     
    return fail_list    

def get_data_by_partyID():
    df = pd.read_csv('D:\\013160\\Desktop\\security.csv')
    party_list = list(set(list(df['PARTY_ID'])))
    for party_id in party_list:
        try:
            get_data(party_id)
        except Exception as e:
            print(e)
if __name__ == '__main__':
    # get_data_by_partyID()
    # sdate = 20/171031
    # sdate = 20160101
    # edate = 20181121
    # sdate,edate,cdate_list = check_update_date(sdate, edate)
    # for date in cdate_list:
        # get_data(str(date))
    # df = pd.read_csv('D:\\013160\\data\\data\\DateTime.csv')
    # df['DateTime'] = df['DateTime'].apply(lambda x : dt.datetime.strptime(x,'%Y/%m/%d'))
    # df['DateTime'] = df['DateTime'].apply(lambda x : x.strftime('%Y%m%d'))
    # cdate_list = list(df['DateTime'])

    # source_path = 'Z:\\warehouse\\test\\u_quant_local\\uqer_professional_factors\\'
    # csv_list = [source_path+i for i in os.listdir(source_path)]
    # csv_list.sort()
    # csv_date_list = [int(i[-12:-4]) for i in csv_list]
    # csv_date_list_take = [i for i in csv_date_list if i>=sdate and i<=edate]
    # csv_list_take = [source_path+str(i)+'.csv' for i in csv_date_list_take]
    # csv_list_take.sort()
    # save_pickle(csv_list_take)
    from multifactor.IO import IO
    df = pd.read_csv('Z:\\warehouse\\test\\u_quant_local\\stock_list.csv')
    # df.reset_index(inplace=True)
    stock_list  = list(df['partyID'])
    for stock in stock_list:
        stock = str(stock)
        try:
            get_data(stock)
        except Exception as e:
            print(e)