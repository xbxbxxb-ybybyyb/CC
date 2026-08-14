import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
from xquant.xqutils.helper import link
lm = link.LinkMessage()
import os
import time
import warnings
warnings.filterwarnings('ignore')
# 上传文件至ftp
import ftplib
import datetime as dt
from ProdWork.CommonTools import excel_saver, ftp_download, ftp_upload, number2stockcode

"""
读取ftp上的成交回报，每日下午16:00开始读取，如果没有，则等待反复进行读取，直到成交回报存在
远程ftp存在以后，下载到ftp对应的文件夹
"""

if __name__ == "__main__":
    nowdate = dt.datetime.now().strftime('%Y%m%d')

    nowdate_h = pd.Timestamp(nowdate).strftime('%Y-%m-%d')
    # nowdate = '20230922'
    # nowdate_h = '2023-03-13'
    print('nowdate=%s' % str(nowdate))
    host = '168.8.2.68'
    username = 'xquant'
    password = 'Xquant-32'
    f = ftplib.FTP(host)  # 实例化FTP对象
    f.login(username, password)  # 登录
    ftp_foldpath = 'XQuant/013600/event_trade/'
    f.encoding = "gbk"
    ftp_filelist = f.nlst(ftp_foldpath)
    print(ftp_filelist)
    o32_filename = '综合信息查询_成交回报_537_547_%s.xls'%nowdate
    o45_filename = 'O45_成交流水_%s.xlsx' % nowdate
    print(o32_filename, o45_filename)
    notready = True
    endtime = 200000
    while notready:
        now_time = dt.datetime.now()
        now_time_int = int(now_time.strftime('%H%M%S'))
        now_time_str = now_time.strftime('%H:%M:%S')

        ftp_filelist = f.nlst(ftp_foldpath)
        print(now_time_str, ftp_filelist)

        notready = ((o32_filename in ftp_filelist and o45_filename in ftp_filelist) == False)
        if not notready:
            now_time = dt.datetime.now().strftime('%H:%M:%S')
            print('tradefile is ready', now_time)

            ftp_download(f, ftp_foldpath + o32_filename, '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_537_547_%s.xls' % nowdate)
            ftp_download(f, ftp_foldpath + o45_filename, '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)
            time.sleep(10)
            o45_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)
            print('o45成交记录：',o45_df.shape[1])
            if o45_df.shape[1] != 48:
                message = '成交回报格式错误，需重新上传！！！！！！！！！！'
                lm.sendMessage(message)
            for tmp_file in ftp_filelist:
                f.delete('XQuant/013600/event_trade/' + tmp_file)
                print('has delected ftpfile %s' % 'XQuant/013600/event_trade/' + tmp_file)
            break
        else:
            if now_time_int <= endtime:
                time.sleep(5)
            else:
                message = '成交回报尚未生成'
                lm.sendMessage(message)
                break

