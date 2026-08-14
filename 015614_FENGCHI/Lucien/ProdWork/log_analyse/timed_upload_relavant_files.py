import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from xquant.xqutils.helper import link
lm = link.LinkMessage()
import os
import time
import warnings
warnings.filterwarnings('ignore')
import ftplib
import datetime as dt
from ProdWork.CommonTools import number2stockcode
from xquant.factordata import FactorData
s = FactorData()


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
        if os.path.exists('/data/group/800463/position/O45_组合证券_%s.xlsx'%str(date)):
            last_cc = pd.read_excel('/data/group/800463/position/O45_组合证券_%s.xlsx' % str(date))
        else:
            last_cc = pd.read_excel('/data/group/800463/position/O45_组合证券_%s_origin.xlsx' % str(date))
        last_cc = last_cc[~last_cc['业务日期'].isna()]
        if last_cc.shape[0]>0:
            last_cc['dt'] = [pd.Timestamp(str(x)) for x in last_cc['业务日期'].tolist()]
            last_cc['Ticker'] = last_cc['证券代码'].apply(number2stockcode)
            last_cc.set_index(['dt', 'Ticker'], inplace=True)
            sel_cc = list(set(last_cc.index.tolist())&set(o45_df.index.tolist()))
            if len(sel_cc)>0:
                o45_df.loc[sel_cc,'前日持仓'] = last_cc.loc[sel_cc,'当前数量']

    o45_df['持仓'] = o45_df.apply(lambda x: x['前日持仓'] + x['成交数量'] if x['委托方向'] == '买入' else x['前日持仓'] - x['成交数量'], axis = 1)
    o45_df['涨跌幅(%)'] = md_data.loc[o45_df.index, 'pct_chg']
    o45_df = o45_df.reset_index()
    o45_df.drop(columns = ['dt','Ticker','前日持仓'], inplace = True)
    return o45_df

def deal_o45_bjs(df, md_data, date, num, nowdate_h):
    o45_df = df.rename(columns={'成交价格': '成交均价', '成交日期': '发生日期'})
    o45_df['发生日期'] = nowdate_h
    o45_df = o45_df[~o45_df['发生日期'].isna()]
    o45_df['序号'] = [num + x for x in list(range(1, len(o45_df) + 1))]
    o45_df['dt'] = [pd.Timestamp(str(x)) for x in o45_df['发生日期'].tolist()]
    o45_df['Ticker'] = o45_df['证券代码'].apply(number2stockcode)   # 北交所没有0开头，这里不用改
    o45_df.set_index(['dt', 'Ticker'], inplace=True)
    o45_df['前日持仓'] = 0

    if os.path.exists('/data/group/800463/position/O45_组合证券_%s_bjs.xlsx'%str(date)):
        last_cc = pd.read_excel('/data/group/800463/position/O45_组合证券_%s_bjs.xlsx' % str(date))
        last_cc = last_cc.iloc[:-1] # 最后一行是空的，合计行
        # last_cc['dt'] = [pd.Timestamp(str(x)) for x in last_cc['持仓日期'].tolist()]
        last_cc['dt'] = [pd.Timestamp(str(x)) for x in last_cc['业务日期'].tolist()]
        last_cc['Ticker'] = last_cc['证券代码'].apply(number2stockcode)
        last_cc.set_index(['dt', 'Ticker'], inplace=True)
        sel_cc = list(set(last_cc.index.tolist())&set(o45_df.index.tolist()))
        if len(sel_cc) > 0:
            o45_df.loc[sel_cc,'前日持仓'] = last_cc.loc[sel_cc,'当前数量']
    else:
        o45_df['前日持仓'] = 0

    o45_df['持仓'] = o45_df.apply(lambda x: x['前日持仓'] + x['成交数量'] if x['委托方向'] == '买入' else x['前日持仓'] - x['成交数量'], axis = 1)
    o45_df['涨跌幅(%)'] = md_data.loc[o45_df.index, 'pct_chg']
    o45_df = o45_df.reset_index()
    o45_df.drop(columns = ['dt','Ticker','前日持仓'], inplace = True)
    return o45_df

if __name__ == "__main__":
    nowdate = dt.datetime.now().strftime('%Y%m%d')
    # nowdate = '20250715'
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

    while True:
        if os.path.exists('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate):
            o32_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_537_547_%s.xls'%'20220811')
            o45_dfraw = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s.xls' % nowdate)

            # 更换更快的方式
            while True:
                md_data = s.get_factor_value('WIND_AShareEODPrices',
                            factors=['S_INFO_WINDCODE', 'S_DQ_PCTCHANGE'],
                            TRADE_DT=nowdate).rename(columns={'S_INFO_WINDCODE':'证券代码', 'S_DQ_PCTCHANGE':'pct_chg'})
                if len(md_data) > 0: # 当日有数据
                    md_data['dt'] = pd.to_datetime(nowdate)
                    md_data['Ticker'] = md_data['证券代码']
                    md_data = md_data.set_index(['dt', 'Ticker'])
                    break
                else:
                    print(f'{nowdate}_WIND数据未完备')
                    time.sleep(60)

            if len(o45_dfraw) > 0:
                o45_df = deal_o45(o45_dfraw, md_data, nowdate, len(o32_df))
            else:
                o45_df = pd.DataFrame()

            trade_df = pd.concat([o32_df, o45_df])
            # trade_df = trade_df[~trade_df['发生日期'].isna()]
            trade_df = trade_df[trade_df['发生日期'] == nowdate_h]
            trade_df = trade_df[o32_df.columns.tolist()]
            trade_df.set_index(['序号'], inplace=True)
            trade_df['证券代码'] = trade_df['证券代码'].apply(lambda x: str(int(x)).zfill(6))
            print(trade_df.isna().sum().sort_values())
            from dataApi.sendInfo import send_message
            send_message('成交回报已生成')
            # trade_df.to_excel(f'/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_{nowdate}_bak.xls')

            # NOTE: 20240927 by fenc：针对添加上海3个组合，深圳3个组合 进行修改
            # NOTE：前提要保证：只有其中一个组合进行了正常买入，所以剔除掉与正常买入的票相重复的组合的买入，靠排序取最大值进行判断的
            group_buy_trade_df = trade_df.query('委托方向=="买入"').groupby('证券代码').apply(lambda x: x.sort_values('成交数量', ascending=False)).drop('证券代码', axis=1)
            group_buy_trade_df = group_buy_trade_df.groupby('证券代码').first().reset_index()

            group_sell_trade_df = trade_df.query('委托方向=="卖出"').groupby('证券代码').apply(lambda x: x.sort_values('成交数量', ascending=False)).drop('证券代码', axis=1)
            group_sell_trade_df = group_sell_trade_df.groupby('证券代码').first().reset_index()
            group_trade_df = pd.concat([group_buy_trade_df, group_sell_trade_df], axis=0).reset_index(drop=True)
            # group_trade_df.to_excel(f'/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_{nowdate}.xls')

            break
    else:
        message = '成交回报尚未生成'
        lm.sendMessage(message)
        time.sleep(60)

    # 默认有了非北交所的记录，北交所的就一定有了，如果北交所的生成的晚，这个循环就进不去
    if os.path.exists('/data/group/800463/xiely/save-file/forFc/daily_O45_upload/O45_成交流水_%s_bjs.xlsx' % nowdate):
        o45_bjs = pd.read_excel('/data/group/800463/xiely/save-file/forFc/daily_O45_upload/O45_成交流水_%s_bjs.xlsx' % nowdate).iloc[:-1]

        # 更换更快的方式
        while True:
            md_data = s.get_factor_value('WIND_AShareEODPrices',
                                         factors=['S_INFO_WINDCODE', 'S_DQ_PCTCHANGE'],
                                         TRADE_DT=nowdate).rename(columns={'S_INFO_WINDCODE': '证券代码', 'S_DQ_PCTCHANGE': 'pct_chg'})
            if len(md_data) > 0:  # 当日有数据
                md_data['dt'] = pd.to_datetime(nowdate)
                md_data['Ticker'] = md_data['证券代码']
                md_data = md_data.set_index(['dt', 'Ticker'])
                break
            else:
                print(f'{nowdate}_WIND数据未完备')
                time.sleep(60)

        if len(o45_bjs) > 0:
            o45_df_bjs = deal_o45(o45_bjs, md_data, nowdate, len(o45_bjs))
        else:
            o45_df_bjs = pd.DataFrame()

        # o45_df_bjs = o45_df_bjs[['证券代码', '委托方向', '交易账户', '成交金额', '成交数量', '成交均价', '证券名称', '涨跌幅(%)']]
        o45_df_bjs['发生日期'] = nowdate_h
        o45_df_bjs = o45_df_bjs.rename({'交易账户': '组合名称'}, axis=1)
        trade_df = pd.concat([o32_df, o45_df, o45_df_bjs])
        # trade_df = trade_df[~trade_df['发生日期'].isna()]
        trade_df = trade_df[trade_df['发生日期'] == nowdate_h]
        trade_df = trade_df[o32_df.columns.tolist()]
        trade_df['序号'] = np.arange(len(trade_df))
        trade_df.set_index(['序号'], inplace=True)
        trade_df['证券代码'] = trade_df['证券代码'].apply(lambda x: str(int(x)).zfill(6))
        print(trade_df.isna().sum().sort_values())
        group_trade_df = pd.concat([group_trade_df, o45_df_bjs])

    group_trade_df = group_trade_df.reset_index(drop=True)

    trade_df.to_excel(f'/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_{nowdate}_bak.xls')
    group_trade_df.to_excel(f'/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_{nowdate}.xls')

    from dataApi.sendInfo import send_message
    send_message('成交回报已生成')
