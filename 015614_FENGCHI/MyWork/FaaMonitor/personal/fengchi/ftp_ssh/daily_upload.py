# coding: utf-8
# Author：fengchi863
# Date ：2021/7/1 14:31

import ftplib
import os
import pandas as pd
from FaaMonitor.dataApi import stockList

os.chdir('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh')

local_ftp = ftplib.FTP(host='168.8.2.60', \
           user='zsd', \
           passwd='zsd', \
           acct=10, timeout=10) #登录ftp
# 设置FTP当前操作的路径
local_ftp.cwd('lucien/daily_trade_prepare')
file_list = local_ftp.nlst()

for idx in range(len(file_list)):
    bufsize = 1024
    filename = file_list[idx]
    file = open('daily_trade_prepare/' + filename, 'wb')
    file_handler = file.write  # 以写模式在本地打开文件
    local_ftp.retrbinary('RETR %s' % os.path.basename(filename),
                   file_handler, bufsize)  # 接收服务器上文件并写入本地文件
    file.close()
print('下载已完成...')

print('生成股票列表')
df = pd.read_excel('daily_trade_prepare/daily_trade_prepare.xlsx', sheet_name='交易准备')
buy_list = df['买入股票代码'].dropna().tolist()
sell_list = df['卖出股票代码'].dropna().tolist()
all_list = list(set(set(buy_list).union(set(sell_list))))
all_list = list(map(lambda x: stockList.trans_int2windcode(x), all_list))
pd.to_pickle(all_list, '/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                       'daily_trade_prepare/generate_t0_param/stk_list.pkl')
print('给T0生成成功')
local_ftp.close()
