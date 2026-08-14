# coding: utf-8
# Author：fengchi863
# Date ：2024/11/11 13:18

import ftplib
import os
import time
import pandas as pd
import datetime


def ftp_upload_folder(ftp_server, username, password, local_dir, remote_dir):
    ftp = ftplib.FTP(ftp_server)
    ftp.login(username, password)

    for dirname, subdirs, files in os.walk(local_dir):
        remote_dir = remote_dir + dirname[len(local_dir):]
        try:
            ftp.mkd(remote_dir)
        except Exception:
            pass
        for file in files:
            print(file)
            local_path = os.path.join(dirname, file)
            remote_path = os.path.join(remote_dir, file)
            with open(local_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_path}', file)
    ftp.quit()


ftp_server = '168.8.2.68'
username = 'xquant'
passwd = 'Xquant-32'
local_dir = 'D:\data/Tick/'
remote_dir = 'Xquant/015613/'

# month_list = [201606, 201607, 201608, 201609, 201610,
#               201611, 201612,
#               201701, 201702, 201703, 201704, 201705, 201706, 201707, 201708, 201709, 201710]
# month_list = [201711, 201712,
#               201801, 201802, 201803, 201804, 201805, 201806, 201807, 201808, 201809, 201810, 201811, 201812]
# month_list = [201901, 201902, 201903, 201904, 201905, 201906, 201907, 201908]
# month_list = [201909, 201910, 201911, 201912, 202001]
# month_list = [202002, 202003, 202004, 202005, 202006, 202007, 202008, 202009, 202010]
# month_list = [202101, 202102, 202103, 202104, 202105, 202106, 202107]
# month_list = [202108, 202109, 202110, 202111, 202112,
#               202201, ]
# month_list = [202202, 202203, 202204, 202205, 202206, ]
# month_list = [202011, 202012, 202207, 202208, 202209, 202210, 202211, 202212]
# month_list = [202207, 202208, 202209, 202210, 202211, 202212]
month_list = [202301, 202302]


for month in month_list:
    tmp_local_dir = local_dir + f'{month}/'
    tmp_remote_dir = remote_dir + f'{month}/'

    ftp1 = ftplib.FTP(ftp_server)
    ftp1.login(username, passwd)
    ftp1.cwd(remote_dir)

    while f'{month_list[month_list.index(month) - 1]}.txt' in ftp1.nlst():
        print(f'{month_list[month_list.index(month) - 1]}.txt还没有被取出，继续等待')
        time.sleep(30)

    print(f'开始上传{month}')
    ftp_upload_folder(ftp_server, username, passwd, tmp_local_dir, tmp_remote_dir)

    with open(local_dir + f'{month}.txt', 'a+') as file:
        file.write('11111')

    with open(local_dir + f'{month}.txt', 'rb') as file:
        ftp1.storbinary(f'STOR {month}.txt', file)

# local_ftp = ftplib.FTP(host='168.8.2.68', \
#           user='xquant', \
#           passwd='Xquant-32', \
#           acct=10, timeout=10) #登录ftp
# local_ftp.encoding = 'utf-8'
## 设置FTP当前操作的路径
# local_ftp.cwd('XQuant/015613/Tick/')
## index_ftp.dir() #显示目录下文件信息
## file_list = local_ftp.nlst()
#
# bufsize = 2048
# file_handler = open(outFullName, 'rb')
# local_ftp.storbinary('STOR %s' % os.path.basename(outFullName), file_handler, bufsize)
# local_ftp.close()
# print('上传成功：%s' % outFullName)
# print('ftp已关闭')