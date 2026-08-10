# -*- coding: utf-8 -*-
import datetime as dt
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import matplotlib.pyplot as plt
import pickle
def get_root_keys(h5_store):
    '''
    --- DESCRIPTION ---
    Get group keys
    '''
    if type(h5_store) is pd.io.pytables.HDFStore:
        return ['/' + item for item in list(h5_store.root._v_groups.keys())]

def get_qtr_list(end_date=None,num_qtr=3):
    end_date = end_date[-1] if type(end_date)==list else end_date
    if end_date == None:
        end_date = get_current_date(new_date_time=18)

    if end_date< 20090105:
        last_day = 20090105
    else:
        last_day = end_date
    year_list = [str(i) for i in range(2000,2200)]
    month_date = ['0331','0630','0930','1231']
    date_list_complete = [i+j for i in year_list for j in month_date]
    qtr_list = [int(i) for i in date_list_complete if int(i)<=last_day][-1*num_qtr:]

    return qtr_list



def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    print ('-'*20+'\ndata used: %d - %d '%(sdate_prev,edate))
    print ('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    print ('-'*20)
    return sdate_prev,edate,cdate_list

def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print ('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        print ('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        print ('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        print ('Right on time: '+str(current_date))
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print ('update for one day: '+str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate

def check_FDD_qtr(date):
    h5_path_test = 'Z:\\warehouse\\prod\\FDD\\CHINA_STOCK\\QUARTERLY\\WIND\\FDD_CHINA_STOCK_QUARTERLY_WIND.h5'
    h5_path_s = 'S:\\Quant\\data\\FDD\\CHINA_STOCK\\QUARTERLY\\WIND\\FDD_CHINA_STOCK_QUARTERLY_WIND.h5'
    # h5_path_s = 'W:\\guozj\\FDD_TMP\\FDD_CHINA_STOCK_QUARTERLY_WIND.h5'

    # col_list = IO.get_available_cols(alt=h5_path_test)
    col_list = ['qfa_ocftoor']
# ,'ebitdatosales','ocftodividend','qfa_yoycf','qfa_yoyocf','qfa_ocftoor'
    rst_dict = {}
    for col in col_list: 
        dict_test = {}
        diff = 0
        miss1 = 0
        miss2 = 0
        if col == 'stm_issuingdate':
            continue
        print('-----' + col)
        df_test = IO.read_data(date, columns = col,alt=h5_path_test)
        df_s = IO.read_data(date, columns = col,alt=h5_path_s)
        try:
            dt = df_s.index.values[0][0]
        except Exception as e:
            print(e)
            continue
        df_s.fillna('NAN', inplace = True)
        df_test.fillna('NAN', inplace = True)
        for index, row in df_test.iterrows():
            dict_test[index] = row[col]
        if len(dict_test.keys()) == 0:
            print(col)
        for index, row in df_s.iterrows():
            if index in dict_test:
                if dict_test[index] == 'NAN' and row[col] != 'NAN':
                    miss1 += 1
                elif dict_test[index] != 'NAN' and row[col] == 'NAN':
                    miss2 += 1
                elif abs(float(dict_test[index]) - float(row[col])) > 0.1:
                    diff += 1
            else:
                diff += 1
        rst_dict[col] = diff
        print(miss1,miss2,diff)
    return rst_dict



def check_MD_daily(date):
    h5_path_test = r'Z:\warehouse\prod\INDUSTRY\CHINA_STOCK\DAILY\WIND\tmp.h5'
    h5_path_s = r'S:\Quant\data\industry\CHINA_STOCK\DAILY\WIND\INDUSTRY_CHINA_STOCK_DAILY_WIND.h5'
    dict_s = {}
    dt_list = [date]
    # col_list = IO.get_available_cols(alt=h5_path_test)
    col_list = ['dividendyield2']
    print(col_list)
    err_list = []
    rst_dict = {}
    for date in dt_list:
        print('-' * 10, date, '-' * 10)
        for col in col_list: 
            if col == 'stm_issuingdate':
                continue
            print('-----' + col)
            df_test = IO.read_data(date, columns = col,alt=h5_path_test)
            df_s = IO.read_data(date, columns = col,alt=h5_path_s)
            try:
                dt = df_s.index.values[0][0]
            except Exception as e:
                err_list.append(col)
                continue
            df_s.fillna('NAN', inplace = True)
            df_test.fillna('NAN', inplace = True)
            dict_test = {}
            dict_s = {}
            diff = 0
            total_diff = 0
            data_miss = 0
            s_miss = 0
            test_miss = 0
            miss_ticker = []
            for index, row in df_test.iterrows():
                dict_test[index] = row[col]
            for index, row in df_s.iterrows():
                if index in dict_test:
                    if dict_test[index] == 'NAN' and row[col] != 'NAN':
                        diff += 1
                        test_miss += 1
                        print(index)
                    elif dict_test[index] != 'NAN' and row[col] == 'NAN':
                        diff += 1
                        s_miss += 1
                    else:
                        total_diff += abs((dict_test[index] - row[col]) / dict_test[index])
                    # elif row[col] == 0:
                    #     if dict_test[index] != 0:
                    #         diff+=1

                    # elif  abs(float(dict_test[index]) / float(row[col]) - 1) > 0.001:
                    #     diff += 1
                     
                else:
                    miss_ticker.append((index[1], row[col]))
                    data_miss += 1

            rst_dict[col] = total_diff
    # rst = 0
    # for col in rst_dict:
        # rst += rst_dict[col]
    print(rst_dict) 
    return rst_dict


def check_h5_unv(dt_list):
    h5_path_test ='Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\universe_complete.h5'
    h5_path_s ='S:\\Quant\\backtest\\local_data\\stock_universe\\universe_complete.h5'
    dict_s = {}
    dt_list = [20180803]
    col_list = IO.get_available_cols(alt=h5_path_s)
    print(col_list)
    for date in dt_list:
        for col in col_list:
            df_test = IO.read_data(date, columns = col,alt=h5_path_test)
            df_s = IO.read_data(date, columns = col,alt=h5_path_s)
            df_s.fillna('NaN', inplace = True)
            df_test.fillna('NaN', inplace = True)

            list_d = {}
            list_s = {}
            for index, row in df_s.iterrows():
                list_d[index[1]] = row[col]
            for index, row in df_test.iterrows():
                list_s[index[1]] = row[col]
            c_key_error = 0
            c_value_error = 0
            for stock_code in list_d:
                if not stock_code in list_s:
                    c_key_error = c_key_error + 1
            else:
                if list_d[stock_code] != list_s[stock_code]:
                    print(stock_code, round(list_d[stock_code], 2), list_s[stock_code])
                    c_value_error = c_value_error + 1
                print(col, c_key_error, c_value_error)

def check_universe(date):
    path1 = 'S:\\Quant\\data\\univ\\CHINA_STOCK\\DAILY\\OPTM\\UNIV_CHINA_STOCK_DAILY_OPTM_20181022.h5'
    path2 = 'Z:\\warehouse\\prod\\univ\\CHINA_STOCK\\DAILY\\OPTM\\UNIV_CHINA_STOCK_DAILY_OPTM.h5'
    df1 = IO.read_data(date, alt = path1)
    df2 = IO.read_data(date, alt = path2)
    df1.reset_index('dt', inplace=True)
    df2.reset_index('dt', inplace=True)
    df1.drop(['dt'], axis = 1, inplace=True)
    df2.drop(['dt'], axis = 1, inplace=True)
    stock_list = df1.index.values
    diff = 0
    miss = 0
    for stock in stock_list:
        if not stock in df2.index.values:
            miss += 1
        else:
            rst = df1.loc[stock] == df2.loc[stock]
            rst_sum = rst.sum()
            if rst_sum != 17:
                diff += 1
    return {'diff':diff, 'miss':miss}

def cal_history_diff():
    sdate = 20170101
    edate = 20190108
    sdate,edate,cdate_list = check_update_date(sdate, edate)
    # cdate_list = get_qtr_list(edate, num_qtr = 38)
    # rst_list = []
    # date_list = []
    rst = {}
    rst1 = {}
    rst2 = {}
    for date in cdate_list:
        print(date)
        # rst1[date] = check_universe(date)
        rst[date] = check_MD_daily(date)
        # rst[date] = check_FDD_qtr(date)
    # with open('W:\\guozj\\univ_diff.pickle', 'wb') as file:
        # pickle.dump(rst1, file)
    with open('W:\\guozj\\dividend_diff.pickle', 'wb') as file:
        pickle.dump(rst, file)
    print(rst)


if __name__ == '__main__':
    # cal_history_diff()
    # check_universe()
    date_list = [20170331, 20170630, 20170930, 20171231,20180331, 20180630, 20180930,20181231,20190331] 
    for date in date_list:
        check_FDD_qtr(date)