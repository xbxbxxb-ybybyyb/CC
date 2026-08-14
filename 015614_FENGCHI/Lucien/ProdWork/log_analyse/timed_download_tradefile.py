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
import shutil
import datetime as dt
from ProdWork.CommonTools import excel_saver, ftp_download, ftp_upload, number2stockcode

"""
读取ftp上的成交回报，每日下午16:00开始读取，如果没有，则等待反复进行读取，直到成交回报存在
远程ftp存在以后，下载到ftp对应的文件夹
"""

if __name__ == "__main__":
    nowdate = dt.datetime.now().strftime('%Y%m%d')

    nowdate_h = pd.Timestamp(nowdate).strftime('%Y-%m-%d')
    # nowdate = '20250715'
    print('nowdate=%s' % str(nowdate))
    o32_filename = '综合信息查询_成交回报_537_547_%s.xls' % nowdate
    o45_filename = 'O45_成交流水_%s.xlsx' % nowdate
    print(o32_filename, o45_filename)
    notready = True
    endtime = 200000
    while notready:
        now_time = dt.datetime.now()
        now_time_int = int(now_time.strftime('%H%M%S'))
        now_time_str = now_time.strftime('%H:%M:%S')
        dsc_path = '/data/group/800463/xiely/save-file/forFc/daily_O45_upload/'
        ftp_filelist = os.listdir(dsc_path)
        notready = ((o45_filename in ftp_filelist) == False)
        if not notready:
            now_time = dt.datetime.now().strftime('%H:%M:%S')
            print('tradefile is ready', now_time)

            # shutil.copyfile(dsc_path + o32_filename, '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_537_547_%s.xls' % nowdate)
            shutil.copyfile(dsc_path + o45_filename, '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)
            time.sleep(10)
            o45_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)
            print('o45成交记录：',o45_df.shape[1])
            if o45_df.shape[1] != 47:   # 20240708变成47列
                message = '成交回报格式错误，需重新上传！！！！！！！！！！'
                lm.sendMessage(message)
            break
        else:
            if now_time_int <= endtime:
                time.sleep(5)
            else:
                message = '成交回报尚未生成'
                lm.sendMessage(message)
                break

