import os
import ftplib
from zipfile import ZipFile
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt

def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        print('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        print('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        print('Right on time: '+str(current_date))
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print('update for one day: '+str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate


def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    print('-'*20+'\ndata used: %d - %d '%(sdate_prev,edate))
    print('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    print('-'*20)
    return sdate_prev,edate,cdate_list

def ftp_reader(ftp_obj, remote_file, local_file):
    remote_file_dir = os.path.dirname(remote_file)
    remote_file = os.path.basename(remote_file)
    if remote_file_dir:
        ftp_obj.cwd(remote_file_dir)
    with open(local_file, 'wb') as fout:
        def callback(data):
            fout.write(data)
        ftp_obj.retrbinary('RETR %s' % remote_file, callback)


if __name__ == '__main__':
    ftp = ftplib.FTP('183.195.154.145')
    ftp.login('csiht', '35708572')
    # check_date = datetime.datetime.now().date().strftime('%Y%m%d')
    _,check_date,_ = check_update_date()
    print(check_date)
    for idx in ['000300', '000905', '000016']:
        try:
            csv_path = r'Z:\warehouse\prod\LOCAL_DATA\INDEX_BACKUP\csv_backup\%s' % idx
            stash_path = r'Z:\warehouse\prod\LOCAL_DATA\INDEX_BACKUP\excel_raw\%s' % idx
            local_file = os.path.join(stash_path, '%s.zip' % check_date)
            ftp_reader(ftp, '/idxdata/data/asharedata/%s/weight_for_next_trading_day/%sweightnextday%s.zip' % (idx, idx, check_date),
                       local_file)
            with ZipFile(local_file, 'r') as zipObj:
                zipObj.extractall(stash_path)
            os.remove(local_file)
            data = pd.read_excel(os.path.join(stash_path, '%sweightnextday%s.xls' % (idx, check_date)),
                                 dtype={'成分券代码\nConstituent Code': str})
            data['Ticker'] = data['成分券代码\nConstituent Code'] + \
                             data['交易所\nExchange'].apply(lambda x: {'Shenzhen': '.SZ', 'Shanghai': '.SH'}[x])
            data = data[['Ticker', '权重(%)\nWeight(%)']]
            weight_col = {'000300': 'HS300', '000905': 'ZZ500', '000016': 'SH50'}[idx]
            data.columns = ['Ticker', weight_col]
            data = data.set_index('Ticker')
            data[weight_col] = data[weight_col]
            data.to_csv(os.path.join(csv_path, str(check_date) + '.csv'))
        except Exception as _exp:
            print('%s raised: %s' % (idx, _exp))
    ftp.close()


