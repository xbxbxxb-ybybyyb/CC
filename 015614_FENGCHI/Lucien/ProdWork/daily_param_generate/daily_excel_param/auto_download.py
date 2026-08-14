# -*- coding: utf-8 -*-
# @Time    : 2021/5/24 20:39
# @Author  : wangweidi
import ftplib
import datetime as dt
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
import time
s = FactorData()


def ftp_download(file_remote, file_local, show=True):
    '''以二进制形式下载文件'''
    bufsize = 8192  # 设置缓冲器大小
    fp = open(file_local, 'wb')
    f.retrbinary('RETR %s' % file_remote, fp.write, bufsize)
    fp.close()
    if show: print(file_remote, '下载成功')


def ftp_upload(file_remote, file_local):
    '''以二进制形式上传文件'''
    bufsize = 8192  # 设置缓冲器大小
    fp = open(file_local, 'rb')
    f.storbinary('STOR ' + file_remote, fp, bufsize)
    fp.close()
    print(file_local, '上传成功')
    
def file_exist(f, file_name):
    file_list = f.nlst('')
    if file_name in file_list:
        print(file_name, 'exist')
        return True
    else:
        print(file_name, 'not exist')
        return False

def ftp_delete(file_name):
    try:
        f.delete(file_name)
    except:
        print('delete fail')
    
today = dt.datetime.now().strftime('%Y%m%d')
hour = int(dt.datetime.now().strftime("%H"))

host = '168.8.2.68'
username = 'xquant'
password = 'Xquant-32'

# ------------------------------------------------------------------------------
f = ftplib.FTP(host)  # 实例化FTP对象
f.login(username, password)  # 登录
f.encoding = 'GB2312'
i = 0
while True:
    str = ''
    file_name = '股票池-%s.xls' % (today)
    f.cwd('~/Xquant/013600/white_list/')
    if file_exist(f, file_name):
        time.sleep(2)
        ftp_download(file_name, '/data/group/800463/stock_list/white_list/%s' % (file_name[4:]))
    else:
        str += '股票池未到;'


    file_name = '综合信息查询_组合证券_537_%s.xls' % (today)
    f.cwd('~/Xquant/013600/event_position/')
    if file_exist(f, file_name):
        time.sleep(2)
        ftp_download(file_name, '/data/group/800463/position/%s' % (file_name))
    else:
        str += 'O32综合信息查询未到;'

    file_name = 'O45_组合证券_%s.xlsx' % (today)
    f.cwd('~/Xquant/013600/event_position/')
    if file_exist(f, file_name):
        time.sleep(2)
        ftp_download(file_name, '/data/group/800463/position/%s' % (file_name))
        ftp_delete(file_name)
    else:
        str += 'O45综合信息查询未到;'

    if str=='':
        str = '持仓文件与股票池文件均到齐'
        lm = link.LinkMessage()
        lm.sendMessage(str)
        
    if str=='持仓文件与股票池文件均到齐':
        break
    else:
        time.sleep(10)
        if i%10==0:
            lm = link.LinkMessage()
            lm.sendMessage(str)
        i = i+1