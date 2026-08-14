# coding: utf-8
# Author：fengchi863
# Date ：2022/11/1 8:57

"""
准备仿真数据，从远程服务器下载到本地目录（暂时搁置）
"""
import ftplib
import os
import pandas as pd

ssh_ftp = ftplib.FTP() #登录ftp
ssh_ftp.connect(host='168.9.64.62', port=30175, timeout=10)
ssh_ftp.login(user='appadmin',
           passwd='ZiR3Cwiq',
           acct=10)
# 设置FTP当前操作的路径
ssh_ftp.cwd('data/user/015614/daily_trade_prepare')
file_list = ssh_ftp.nlst()

for idx in range(len(file_list)):
    bufsize = 1024
    filename = file_list[idx]
    if filename == 'daily-zuhe-fz-SZ':
        file_handler = open('daily_trade_prepare/' + filename,'wb').write # 以写模式在本地打开文件
        ssh_ftp.retrbinary('RETR %s' % os.path.basename(filename),
                       file_handler,bufsize) # 接收服务器上文件并写入本地文件
print('下载已完成...')