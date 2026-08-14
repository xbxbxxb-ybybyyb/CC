# coding: utf-8
# Author：fengchi863
# Date ：2024/11/11 13:18

import ftplib
import os
import time
import pandas as pd
import datetime
import re
from ftp_code.tradeDate import get_date_range


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

date_list = get_date_range(20240801, 20241130)
ftp1 = ftplib.FTP(ftp_server)
ftp1.login(username, passwd)

for dat in date_list:
    month = str(dat)[:-2]

    tmp_local_dir = local_dir + f'{month}/'
    tmp_remote_dir = remote_dir + f'{month}/'

    ftp1.cwd('/')
    ftp1.cwd(remote_dir)

    while f'{date_list[date_list.index(dat) - 1]}.txt' in ftp1.nlst():
        print(f'{date_list[date_list.index(dat) - 1]}.txt还没有被取出，继续等待')
        time.sleep(30)

    print(f'开始上传{dat}')
    try:
        ftp1.mkd(f'{month}')
    except:
        print('文件夹已存在')

    # ftp_upload_folder(ftp_server, username, passwd, tmp_local_dir + f'{dat}.zip', tmp_remote_dir + f'{dat}.zip')
    local_path = os.path.join(tmp_local_dir, f'{dat}.zip')
    with open(local_path, 'rb') as file:
        ftp1.storbinary(f'STOR {month}/{dat}.zip', file)

    with open(local_dir + f'{dat}.txt', 'a+') as file:
        file.write('11111')

    with open(local_dir + f'{dat}.txt', 'rb') as file:
        ftp1.storbinary(f'STOR {dat}.txt', file)

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