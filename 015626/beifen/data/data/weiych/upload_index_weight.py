# -*- coding: utf-8 -*-
"""

"""

# -*- coding: utf-8 -*-

import datetime as dt
import pandas as pd
import os
import numpy as np
import scipy.io as sio
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import logging
from multifactor.data.utils import *
from ftplib import FTP  # 加载ftp模块
import zipfile
from multifactor.data.utils import *



def upload_file(ftp, remote_file,local_file):

    if not os.path.isfile(local_file):
        print('%s 不存在' % local_file)
        return

    buf_size = 1024
    file_handler = open(local_file, 'rb')
    ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
    file_handler.close()
    print('上传: %s' % local_file + "成功!")



def ftp_upload(date):

    ftp = FTP()
    ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息
    ftp.connect('168.8.2.68')  # 连接的ftp sever和端口
    ftp.login("xquant", "Xquant-32")  # 连接的用户名，密码

    factor_list = ['HS300', 'ZZ500', 'SH50']
    for factor in factor_list:
        remotepath = os.path.join('/XQuant/015626/index_weight/',factor , date + '.csv')
        localpath = os.path.join(r'Z:\warehouse\prod\LOCAL_DATA\CSV\stock_universe',factor, date + '.csv')

        upload_file(ftp, remotepath, localpath)
    print('upload finish')
    ftp.set_debuglevel(0)  # 关闭调试
    ftp.quit()

def main():
    sdate, edate, _ = check_update_date()

    date = str(edate)

    flag = os.path.join('Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\', date, date + '_INDEX_WEIGHT.success')

    print('check flag')
    checkflag = True
    while checkflag:
        if os.path.exists(flag):
            checkflag = False
    print('finish checking flag..')

    ftp_upload(date)



if __name__ == '__main__':
    main()
