import pandas as pd
import numpy as np
import os
import datetime as dt
from xquant.factordata import FactorData
hfactor = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
from xquant.thirdpartydata.marketdata import MarketData
ma = MarketData()
from xquant.textdata import NewsData
nd = NewsData()
from xquant.xqutils.helper import link
lm = link.LinkMessage()
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from xquant.xqutils.helper import link
def cal_ul_price(pre_close_dataframe):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.1 + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.2 + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
def get_ahead_trading_date(specified_date, ahead_date_length):
    #返回specifiled_date前ahead_date_length的交易日
    from xquant.factordata import FactorData
    s = FactorData()
    return int(s.tradingday(specified_date, -ahead_date_length)[0])
def factor_basic(start_date, end_date, result_path, result_flag):
    ahead_len = 40
    start_date_ = get_ahead_trading_date(start_date, ahead_len)
    ipo_data = IO.read_data([20000101, 20990101],
                                 alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
    ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
    ipo_data = ipo_data.reset_index()
    ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00'])]  # 筛选上交所和深交所股票，不包括科创板
    ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
    ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
    ipo_data['dt'] = ipo_data['list_date']
    ipo_data['is_list_date'] = True
    ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date', 'list_date']]

    md_data = IO.read_data([start_date_, end_date],columns = ['pre_close','open','close','high','low','amt','adjfactor'],
                                alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data = md_data.join(ipo_data)
    md_data['is_list_date'] = md_data['is_list_date'] == True
    md_data['after_list'] = md_data['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
    md_data['in_40_days'] = (md_data['is_list_date'].unstack().rolling(40, 1).sum() == 1).stack()  # 40日以内定义为次新股,不为强势股
    md_data['1_1_ul_price'] = cal_ul_price(md_data[['pre_close']])
    md_data['1_44_ul_price'] = (md_data['pre_close'] * 100 * 1.44 + 0.5).apply(np.floor) / 100  # 首日的涨停价
    md_data['is_one_ul'] = (md_data['is_list_date'] & (md_data['close'] == md_data['1_44_ul_price'])) | (
                md_data['open'] == md_data['close']) & (md_data['high'] == md_data['low']) & (
                                       md_data['close'] == md_data['1_1_ul_price'])  # 首日涨停或正常一字板
    md_data['is_ul'] = (md_data['is_list_date'] & (md_data['close'] == md_data['1_44_ul_price'])) |  (md_data['close'] == md_data['1_1_ul_price'])  # 首日涨停或正常一字板
    md_data.loc[md_data['amt'] == 0, 'is_one_ul'] = np.nan  # 将停牌的日期标记为nan，这样中间停牌的次新股，如果之前没开板，复牌后也算是次新股样本
    md_data.loc[(md_data['after_list'] != True) & np.isnan(md_data['pre_close']), 'is_one_ul'] = np.nan
    md_data['is_one_ul_from_list'] = (md_data['is_one_ul'].unstack().rolling(40, 1).mean() == 1).stack()
    md_data['is_ul_from_list'] = (md_data['is_ul'].unstack().rolling(40, 1).mean() == 1).stack()
    md_data['is_cy_kcb'] =(((md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='30'))&(md_data.reset_index()['dt']>='2020-08-24'))|(md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='68'))).values

    #md_data['sample'] = (md_data['is_one_ul'] == True) & (~(md_data['in_40_days'] & md_data['is_one_ul_from_list']))
    #md_data['sample'] = (md_data['is_ul'] == True) & (~(md_data['in_40_days'] & md_data['is_ul_from_list'])) saturn
    md_data['sample'] = (~(md_data['in_40_days'])&(~md_data['is_cy_kcb']))
    sample_data = md_data[md_data['sample']]
    date_bool = (sample_data.index.get_level_values(0) >= pd.Timestamp(str(start_date))) & (
            sample_data.index.get_level_values(0) <= pd.Timestamp(str(end_date)))
    sample_data = sample_data[date_bool][[]]
    sample_data['Flag_SH_SZ'] = np.array(pd.Series(sample_data.index.get_level_values(1)).apply(lambda x: 1 if x[-2:] == 'SZ' else 0))
    #print('basic is', sample_data['Flag_SH_SZ'])
    print('basic num is',sample_data.shape)
    def data_choose(SD_ini):
        SD_ini = SD_ini.reset_index()
        SD_index = ((SD_ini['dt'] >= pd.Timestamp('20150101')) & (SD_ini['Flag_SH_SZ'] == 0)) | (
                    (SD_ini['dt'] >= pd.Timestamp('20160509')) & (SD_ini['Flag_SH_SZ'] == 1))
        SD = SD_ini[SD_index].set_index(['dt', 'Ticker'])
        return SD
    sample_data = data_choose(sample_data)
    if len(sample_data)==0:
        return pd.DataFrame()
    if result_flag:
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        file_name = '%s%s_%d_%d.h5' % (result_path, 'basic', start_date, end_date)
#        if os.path.exists(file_name):
#            IO.pd_hdf5_writer(sample_data, hdf5=file_name, dataset='basic', override=True)
#        else:
#            IO.pd_hdf5_writer(sample_data, hdf5=file_name, dataset='basic')
    return sample_data

if __name__ == "__main__":
    today = int(dt.datetime.now().strftime('%Y%m%d'))
    #today=20241102
    before_date = hfactor.tradingday(str(today),-60)[0]
    last_daysnum = 10
    last_10 = hfactor.tradingday(today,-last_daysnum)[0]
    future_day = hfactor.tradingday(today,3)[-1]
    
    flag_tradeday = 1
    #nowdate=20240430
    datelist = [int(x) for x in hfactor.tradingday(last_10, future_day)]
    if today not in datelist:
        print('今天是节假日%s'%str(today))
        flag_tradeday = 0
        yesterday = int(hfactor.tradingday(today, -1)[0])
    else:
        print('今天是交易日%s'%str(today))
        yesterday = int(hfactor.tradingday(today, -2)[0])
    year = str(today)[:4]
    if flag_tradeday == 0:
        nowdate = yesterday
    else:
        if dt.datetime.now().hour >= 17:
            nowdate = today
        else:
            nowdate = yesterday
    print('nowdate=%s'%nowdate)

    #if dt.datetime.now().hour >= 17:
    yesterday = int(hfactor.tradingday(nowdate, -2)[0])
    tomorrow = int(hfactor.tradingday(nowdate, 2)[-1])

    begindate, enddate = int(nowdate), int(nowdate)
    basic_path = '/dfs/user/013550/StrongStock_stats/Basic/Basic/'
    basic_file_path = basic_path + 'basic_%d_%d.h5' % (begindate, enddate)
    # basic_file_path = '/data/user/013600/strongStock/basic/basic_20200824_20201112.h5'
    basic_df = factor_basic(begindate, enddate, result_path=basic_path, result_flag=True)
    
    # 发给自己
    lm = link.LinkMessage()
    time_now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if len(basic_df):
        stats_df = basic_df.copy()
        stats_df['datelist'] = [int(x.to_pydatetime().strftime("%Y%m%d")) for x in stats_df.reset_index()['dt'].tolist()]
        stats_df['stockID'] = stats_df.reset_index()['Ticker'].tolist()
        stats_df['flag_fupai'] = 0
        stats_df['flag_fpcz'] = 0
        stats_df[ 'Newstitle_fupai'] = np.nan
        stats_df['Newstitle_fupai_cz'] = np.nan
        for index,row in stats_df.iterrows():
            year = str(row['datelist'])[:4]
            #before_date = hfactor.tradingday(str(row['datelist']),-50)[0]
            #data_info = nd.getNewsInfoByStockCode(row['stockID'][:-3], [year],data_source='TNEWS')
            data_info = nd.getAnnouncement(stockcode=[row['stockID']], start_date=str(before_date), end_date=str(today))#
            #nd.getAnnouncement(start_date=str(before_date), end_date=str(today))
            data_info['entrytime'] = data_info['ENTRYTIME']
            data_info['texttitle'] = data_info['TEXTTITLE']
            data_info['datelist'] = data_info['entrytime'].apply(lambda x: int(x.strftime('%Y%m%d')))
            sel_data_info = data_info.query('datelist>=%s' % str(nowdate))
            # stats_df.loc[index, 'flag_fupai'] = 0
            # stats_df.loc[index, 'flag_fpcz'] = 0
            # stats_df.loc[index, 'Newstitle_fupai'] = []
            # stats_df.loc[index, 'Newstitle_fupai_cz'] = []
            if len(sel_data_info)>0:
                #fp_warning = sel_data_info[data_info['texttitle'].apply(lambda x: (('复牌' in x)&('公告' in x)&('复牌跌停' not in x)&('ST' not in x)&('终止' not in x)&('停牌' not in x)&('停复牌' not in x)&('延期复牌' not in x)&('复牌后' not in x)))]
                fp_warning = sel_data_info[data_info['texttitle'].apply(lambda x: (
                            ('复牌' in x) & ('公告' in x) & ('复牌跌停' not in x) & ('ST' not in x)  & ('停牌' not in x) & ('停复牌' not in x) & ('延期复牌' not in x) & ('复牌后' not in x)))]

                fpcz_warning = sel_data_info[data_info['texttitle'].apply(lambda x: (('重组' in x)&('停牌' in x)))]
                fpcz_t_warning = sel_data_info[data_info['texttitle'].apply(lambda x: (('重组' in x) & ('符合' in x)&('*ST' not in x)&('终止重大资产重组' not in x)&('不构成重大资产重组' not in x)&('是否构成重大资产重组' not in x)))]
                if len(fp_warning)>0:
                    stats_df.loc[index, 'flag_fupai'] = 1
                    Newstitle = []
                    for idx in list(range(len(fp_warning))):
                        print('！！！！！！！！！！！！！！！！！！！！！！复牌：%s %s！！！！！！！！！！！！！！！！！！！！！！！！！'%(row['stockID'], nowdate))
                        print(fp_warning.iloc[idx]['texttitle'])
                        Newstitle = Newstitle + [fp_warning.iloc[idx]['texttitle']]

                    stats_df.loc[index, 'Newstitle_fupai'] = str(Newstitle)

                if len(fpcz_t_warning)>0:
                    if stats_df.loc[index, 'flag_fupai'] == 1:
                        stats_df.loc[index, 'flag_fpcz'] = 1
                    Newstitle1 = []
                    for idx in list(range(len(fpcz_t_warning))):
                        if stats_df.loc[index, 'flag_fupai'] == 1:
                            print('！！！！！！！！！！！！！！！！！！！！！复牌重组：%s %s！！！！！！！！！！！！！！！！！！！！！！' % (row['stockID'], nowdate))
                            print(fpcz_t_warning.iloc[idx]['texttitle'])
                        Newstitle1 = Newstitle1 + [fpcz_t_warning.iloc[idx]['texttitle']]
                    stats_df.loc[index, 'Newstitle_fupai_cz'] = str(Newstitle1)
        fp_df = stats_df.query('flag_fupai==1')
        print('复牌标的', nowdate)
        print(fp_df['Newstitle_fupai'])
        ls_mess = '%s, 复牌标的:%s, \n%s'%(time_now,nowdate,fp_df['Newstitle_fupai_cz'])
        #lm.sendMessage(ls_mess)
        if len(fp_df.query('flag_fpcz==1')):
            print('复牌重组标的', nowdate)
            print(fp_df.query('flag_fpcz==1')['Newstitle_fupai_cz'])
            ls_mess1 = '复牌重组标的:%s, \n%s'%(nowdate,fp_df.query('flag_fpcz==1')['Newstitle_fupai_cz'])
            ls_mes = '%s \n%s '%(ls_mess, ls_mess1)
            lm.sendMessage(ls_mes)
        else:
            lm.sendMessage("%s,没有复牌重组的标的：%s"%(time_now,nowdate))
                #stats_df.loc[index,'flag_fpcz_true'] = (stats_df.loc[index, 'flag_fupai'])&(stats_df.loc[index, 'flag_fpcz'])
