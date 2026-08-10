import datetime as dt
import os
import numpy as np
from ftplib import FTP  # 加载ftp模块
from IndexDividends_weiych2 import IndexDividends
from multifactor.data.utils import *
from multifactor.utility.dt import *

def downloadfile(ftp, remotepath, localpath):
    fp = open(localpath,'wb') #以写模式在本地打开文件
    bufsize = 1024
    ftp.retrbinary('RETR ' + remotepath,fp.write,bufsize)
    # 退出ftp服务器

def downloadcsv(table_name, date):
    localpath = os.path.join('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc',table_name,str(date) + '.csv')
    remotepath = os.path.join('/XQuant/015626/ftp_data/gogoal_htsc', table_name,str(date) + '.csv')
    ftp = FTP()
    ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息
    ftp.connect('168.8.2.68')  # 连接的ftp sever和端口
    ftp.login("xquant", "Xquant-32")
    print(remotepath, localpath)
    downloadfile(ftp, remotepath, localpath)
    print('download finish')
    ftp.set_debuglevel(0)  # 关闭调试
    ftp.quit()


def upload_file(ftp, remote_file,local_file):
    if not os.path.isfile(local_file):
        print('%s 不存在' % local_file)
        return

    buf_size = 1024
    file_handler = open(local_file, 'rb')
    ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
    file_handler.close()
    print('上传: %s' % local_file + "成功!")


def ftp_upload(tommorrow):
    ftp = FTP()
    ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息
    ftp.connect('168.8.2.68')  # 连接的ftp sever和端口
    ftp.login("xquant", "Xquant-32")  # 连接的用户名，密码
    remotepath = os.path.join('/XQuant/015626/ftp_data/IndexDividends', 'IndexDividends_' + tommorrow + '.xlsx')
    localpath = os.path.join(r'A:\weiyc\data\IndexDividends', 'IndexDividends_' + tommorrow + '.xlsx')

    upload_file(ftp, remotepath, localpath)
    print('upload finish')
    ftp.set_debuglevel(0)  # 关闭调试
    ftp.quit()

sdate, edate, _ = check_update_date()
filepath = os.path.join('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\con_forecast_stk', str(sdate) + '.csv')
while(not os.path.exists(filepath)):
    try:
        downloadcsv('con_forecast_stk', sdate)
    except:
        print('download con_stk wrong!')
        time.sleep(100)
print('download csv done!')

id = IndexDividends(sdate)
id.run()

print('IndexDividends down!')

nowtime = dt.datetime.strptime(str(sdate),'%Y%m%d')
tradingDates = get_trading_date_range(nowtime - dt.timedelta(30),(nowtime + dt.timedelta(30)).strftime('%Y%m%d'))
tradingDates = [d.strftime('%Y%m%d') for d in tradingDates]
tommorrow = tradingDates[tradingDates.index(str(sdate)) + 1]

ftp_upload(tommorrow)
print('file upload down!')



