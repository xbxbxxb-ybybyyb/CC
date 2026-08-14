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
from ProdWork.CommonTools import number2stockcode
from LucienUtil import IO


def deal_o45(df, md_data, date, num):
    o45_df = df.rename(columns={'成交价格': '成交均价', '业务日期': '发生日期'})
    o45_df = o45_df[~o45_df['发生日期'].isna()]
    o45_df['序号'] = [num + x for x in list(range(1, len(o45_df) + 1))]
    o45_df['dt'] = [pd.Timestamp(str(x)) for x in o45_df['发生日期'].tolist()]
    o45_df['Ticker'] = o45_df['证券代码'].apply(number2stockcode)
    o45_df.set_index(['dt', 'Ticker'], inplace=True)
    o45_df['前日持仓'] = 0
    if list(o45_df['发生日期'].unique())[0] == '2021-12-03':
        o45_df['持仓'] = o45_df['成交数量']
    else:
        last_cc = pd.read_excel('/data/group/800463/position/O45_组合证券_%s.xlsx'%str(date))
        last_cc = last_cc[~last_cc['业务日期'].isna()]
        if last_cc.shape[0]>0:
            last_cc['dt'] = [pd.Timestamp(str(x)) for x in last_cc['业务日期'].tolist()]
            last_cc['Ticker'] = last_cc['证券代码'].apply(number2stockcode)
            last_cc.set_index(['dt', 'Ticker'], inplace=True)
            sel_cc = list(set(last_cc.index.tolist())&set(o45_df.index.tolist()))
            if len(sel_cc)>0:
                o45_df.loc[sel_cc,'前日持仓'] = last_cc.loc[sel_cc,'当前数量']

    o45_df['持仓'] = o45_df.apply(lambda x: x['前日持仓'] + x['成交数量'] if x['委托方向'] == '买入' else x['前日持仓'] - x['成交数量'], axis = 1)
    o45_df['涨跌幅(%)'] = md_data.loc[o45_df.index,'pct_chg']
    o45_df = o45_df.reset_index()
    o45_df.drop(columns = ['dt','Ticker','前日持仓'], inplace = True)
    return o45_df

'''
def ftp_download(file_remote, file_local, show = True):
    #以二进制形式下载文件
    bufsize = 8192  # 设置缓冲器大小
    fp = open(file_local, 'wb')
    f.retrbinary('RETR %s' % file_remote, fp.write, bufsize)
    fp.close()
    if show: print(file_remote, 'to%s,下载成功'%file_local)

def ftp_upload(file_remote, file_local):
    #以二进制形式上传文件
    bufsize = 8192  # 设置缓冲器大小
    fp = open(file_local, 'rb')
    f.storbinary('STOR ' + file_remote, fp, bufsize)
    fp.close()
    print(file_local, 'from%s,上传成功'%file_remote)
'''

if __name__ == "__main__":
    #nowdate='20211126'
    nowdate = dt.datetime.now().strftime('%Y%m%d')
    #nowdate = '20230313'
    nowdate_h = pd.Timestamp(nowdate).strftime('%Y-%m-%d')
    print('nowdate=%s' % str(nowdate))
    host = '168.8.2.68'
    username = 'xquant'
    password = 'Xquant-32'
    f = ftplib.FTP(host)
    f.login(username, password)
    f.encoding = 'GB2312'
    IO_mother_dir = '/data/group/800080/warehouse_event'
    MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % nowdate

    #################################### 复制实盘参数 ####################################
    from shutil import copyfile
    try:
        copyfile('/data/group/800463/param/param/param-%s-prod-O45.xlsx' % nowdate,
                 '/data/group/800463/日内强势股/实盘测试参数/param-%s-prod.xlsx'% nowdate)
        print('from %s to /data/group/800463/日内强势股/实盘测试参数/param-%s-prod.xlsx 上传成功' % ('/data/group/800463/param/param/param-%s-prod.xlsx' % nowdate, nowdate))
    except:
        message = '早盘参数尚未生成？？？？'
        lm.sendMessage(message)
    # """
    #################################### 复制实盘和仿真log ####################################
    '''while (os.path.exists('/data/group/800463/StrategyLog/prd/StrongStrategy-%s.log.gz'%nowdate_h) == False): # 金工团队文件夹
        print('等待实盘日志中')
        time.sleep(60)'''
    time.sleep(60)
    
    #(os.path.exists('/data/group/800463/StrategyLog/sim/StrongStrategy-%s.log.gz'%nowdate_h) == False) or
    while not os.path.exists('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat.log.gz' % nowdate_h):# or (os.path.exists('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat_lite.log.gz'%nowdate_h) == False)
        print('等待仿真日志中')    # TODO：谢总的定时任务生成这个文件，16:00点生成，实盘和仿真的
        time.sleep(60)
    time.sleep(60)
    copyfile('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat.log.gz'%nowdate_h,'/data/group/800463/日内强势股/log/StrongStrategy-%s-uat.log.gz'%nowdate_h)
    #copyfile('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat_other.log.gz'%nowdate_h,'/data/group/800463/日内强势股/log/StrongStrategy-%s-uat_other.log.gz'%nowdate_h)
    print('from %s to /data/group/800463/日内强势股/log/StrongStrategy-%s-uat.log.gz 上传成功'%('/data/group/800463/StrategyLog/sim/StrongStrategy-%s.log.gz'%nowdate_h,nowdate_h))
    # while (os.path.exists('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-SZEX_udp.log.gz'%nowdate_h) == False):
    #     print('等在生产UDP深圳日志中')
    #     time.sleep(60)
    # copyfile('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-SZEX_udp.log.gz'%nowdate_h,
    #          '/data/group/800463/日内强势股/log/StrongStrategy-%s-SZEX_udp.log.gz' % nowdate_h)


    #copyfile('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat_lite.log.gz'%nowdate_h,'/data/group/800463/日内强势股/log/StrongStrategy-%s-uat_lite.log.gz' % nowdate_h)
    copyfile('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat_50_51.log.gz' % nowdate_h,
             '/data/group/800463/日内强势股/log/StrongStrategy-%s-uat_50_51.log.gz' % nowdate_h)
    copyfile('/data/group/800463/xiely/日内强势股/log/StrongStrategy-%s-uat_49_53.log.gz' % nowdate_h,
             '/data/group/800463/日内强势股/log/StrongStrategy-%s-uat_49_53.log.gz' % nowdate_h)
    # """
#################################### 下载上传成交回报 ####################################
    try:

        '''ftp_download(f,'XQuant/013600/event_trade/综合信息查询_成交回报_537_547_%s.xls'%nowdate,
                   '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_537_547_%s.xls'%nowdate)
        ftp_download(f, 'XQuant/013600/event_trade/O45_成交流水_%s.xlsx' % nowdate,
                     '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)'''

        if os.path.exists('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_537_547_%s.xls'%nowdate) and os.path.exists('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate):
            o32_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_537_547_%s.xls'%'20220811')#.set_index(['序号'])
            o45_dfraw = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)#.rename(columns = {'业务日期':'发生日期'})#.set_index(['序号'])
            #if os.path.exists('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_%s.xls'%nowdate):
            '''ftp_filelist = f.nlst('XQuant/013600/event_trade/')
            time.sleep(20)
            for tmp_file in ftp_filelist:
                f.delete('XQuant/013600/event_trade/'+tmp_file)
                print('has delected ftpfile %s'%'XQuant/013600/event_trade/'+tmp_file)'''
            while not os.path.exists(MD_data_prod_dir + '%s_MD.success' % nowdate):
                print('等待MD或RDF或RISK或5分钟数据中')
                time.sleep(60)
            md_data = IO.read_data([nowdate, nowdate],
                                   columns=['pct_chg'],
                                   alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
            if len(o45_dfraw)>0:
                o45_df = deal_o45(o45_dfraw,md_data,nowdate,len(o32_df))
            else: o45_df = pd.DataFrame()
            trade_df = pd.concat([o32_df,o45_df])
            #trade_df = trade_df[~trade_df['发生日期'].isna()]
            trade_df = trade_df[trade_df['发生日期'] == nowdate_h]
            trade_df = trade_df[o32_df.columns.tolist()]
            trade_df.set_index(['序号'],inplace=True)
            trade_df['证券代码'] = trade_df['证券代码'].apply(lambda x: str(int(x)).zfill(6))
            print(trade_df.isna().sum().sort_values())

            trade_df.to_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_%s.xls'%nowdate)

    except:
        message = '成交回报尚未生成'
        lm.sendMessage(message)
