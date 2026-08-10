# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 21:41:50 2019

@author: 013601

比对xquant每天切片的数据与本地数据的区别
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

def get_latest_csv(source_path):
    # accept xls, xlsx
    file_list = os.listdir(source_path)
    file_list.sort()
    return file_list[-1]


def upload_file(ftp, remote_file,local_file):

    if not os.path.isfile(local_file):
        print('%s 不存在' % local_file)
        return

    buf_size = 1024
    file_handler = open(local_file, 'rb')
    ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
    file_handler.close()
    print('上传: %s' % local_file + "成功!")



def ftp_upload():

    ftp = FTP()
    ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息
    ftp.connect('168.8.2.68')  # 连接的ftp sever和端口
    ftp.login("xquant", "Xquant-32")  # 连接的用户名，密码

    base_path = r'Z:\warehouse\prod\LOCAL_DATA\CSV\stock_universe\HTSC'
    blacklist_path = os.path.join(base_path, 'blacklist')
    blacklist_exchange_path = os.path.join(base_path, 'blacklist_exchange')
    blacklist_ziying_path = os.path.join(base_path, 'blacklist_ziying')
    blacklist_group_path = 'A:\\chenyx\\blacklist_group\\blacklist_group_daily\\'
    whitelist_path = 'A:\\wangwd\\data_file_for_ALPHA\\white_list\\'

    ftp_base_path = '/XQuant/015626/ftp_data/UNIV/HTSC/'
    ftp_blacklist_path = os.path.join(ftp_base_path, 'blacklist')
    ftp_blacklist_exchange_path = os.path.join(ftp_base_path, 'blacklist_exchange')
    ftp_blacklist_ziying_path = os.path.join(ftp_base_path, 'blacklist_ziying')
    ftp_blacklist_group_path = os.path.join(ftp_base_path, 'chenyx/blacklist_group/blacklist_group_daily/')
    ftp_whitelist_path = os.path.join(ftp_base_path, 'wangwd/data_file_for_ALPHA/white_list/')

    path_dict = {blacklist_path:ftp_blacklist_path, blacklist_exchange_path:ftp_blacklist_exchange_path,
                 blacklist_ziying_path:ftp_blacklist_ziying_path, blacklist_group_path:ftp_blacklist_group_path,
                 whitelist_path:ftp_whitelist_path}
    file = os.path.join(base_path, 'ftp_path.txt')
    if os.path.exists(file):
        os.remove(file)
    for path in path_dict.keys():
        latestcsv = get_latest_csv(path)
        remotepath = os.path.join(path_dict[path], latestcsv)
        localpath = os.path.join(path, latestcsv)

        with open(file, 'a+') as f:
            f.write(remotepath + '&' + localpath + '\n')  # 加\n换行显示
        upload_file(ftp, remotepath, localpath)
    upload_file(ftp, os.path.join(ftp_base_path, 'ftp_path.txt'), file)
    print('upload finish')
    ftp.set_debuglevel(0)  # 关闭调试
    ftp.quit()

def main():

    ftp_upload()



if __name__ == '__main__':
    main()
