# coding: utf-8
# Author：fengchi863
# Date ：2024/7/19 13:27

"""
先从ftp下载到本地
再上传到sftp
"""

import ftplib
import os
import pandas as pd
import datetime
import paramiko

local_index_ftp = ftplib.FTP(host='168.8.2.68', \
           user='zsd', \
           passwd='zsd', \
           acct=10, timeout=10) #登录ftp
# 设置FTP当前操作的路径
local_index_ftp.cwd('weight_of_index/zz500')
# index_ftp.dir() #显示目录下文件信息
file_list = local_index_ftp.nlst()
the_latest_file = file_list[-1]
the_latest_date = the_latest_file[-12:-4]