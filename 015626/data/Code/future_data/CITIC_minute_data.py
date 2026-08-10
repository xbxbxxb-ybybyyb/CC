import pandas as pd
from multifactor.IO import IO
from multifactor.utility.dt import *
import datetime
import os
from tqdm import tqdm

def ticker_match(ticker_num): 
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker
    
df = pd.read_csv('/data/user/015626/data/share/LOCAL_DATA/CSV/WIND/AIndexMembersCITICS3.csv')
df['S_CON_INDATE'] = df['S_CON_INDATE'].astype('int')
df['S_CON_OUTDATE'].fillna(50000000, inplace=True)
df['S_CON_OUTDATE'] = df['S_CON_OUTDATE'].astype('int')
# 每个3级行业初始点位
pointdict = {k:{'open':1000,'high':1000,'low':1000,'close':1000,'vwap':1000} for k in df.S_INFO_WINDCODE.unique().tolist()}

# 返回每天存在的3级行业，及其对应的成分股list
def get_CITIC_info(date):
    df = pd.read_csv('/data/user/015626/data/share/LOCAL_DATA/CSV/WIND/AIndexMembersCITICS3.csv')
    df['S_CON_INDATE'] = df['S_CON_INDATE'].astype('int')
    df['S_CON_OUTDATE'].fillna(50000000, inplace=True)
    df['S_CON_OUTDATE'] = df['S_CON_OUTDATE'].astype('int')
    df = df[(df.S_CON_INDATE <= date) & (df.S_CON_OUTDATE > date)]
    a = {k:list(v.S_CON_WINDCODE) for k, v in df.groupby('S_INFO_WINDCODE')}
    return a
    
minute_stock_per_date_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/'
# 返回每天 一个股票list 的价格每分钟变化量（不是累计值），以及成交量成交额
def retrieve_stock_minute(date, tickerlist, datelist):
#     print('retrieving stock minute data ', date)
    dindex = datelist.index(date)
    if dindex == 0:
        file_path = os.path.join(minute_stock_per_date_path, str(date) + '.pkl')
        spot_data = pd.read_pickle(file_path, compression='gzip')
    else:
        date1 = datelist[dindex - 1]
        collector = list()
        for ts in [date1, date]:
#             print('processing %s' % ts)
            file_path = os.path.join(minute_stock_per_date_path, str(ts) + '.pkl')
            collector.append(pd.read_pickle(file_path, compression='gzip'))
        spot_data = pd.concat(collector, axis=0)
    
    spot_data = spot_data.reset_index()
    spot_data['Ticker'] = spot_data['Ticker'].apply(ticker_match)
    spot_data = spot_data[spot_data.Ticker.isin(tickerlist)]
    
    spot_data['dt'] = spot_data['dt'] * 1E6 + spot_data['minute'] * 100
    spot_data['dt'] = pd.to_datetime(spot_data['dt'].astype('int'), format='%Y%m%d%H%M%S')
    
    spot_data = spot_data.set_index(['dt', 'Ticker'])
    spot_data['midprice'] = spot_data[['open', 'high', 'low', 'close']].mean(axis=1)
    spot_data['vwap'] = spot_data['midprice'].where(spot_data['volume'] == 0, other=spot_data['amt'] / spot_data['volume'])
    spot_data = spot_data.drop(['midprice', 'minute'], axis=1)
    spot_data = spot_data.sort_index()
    
    temp = spot_data[['open','high','low','close','vwap']].unstack()
    temp = temp / temp.shift(1) - 1
    pricedf = pd.DataFrame(index = temp.index)
    for column in ['open','high','low','close','vwap']:
        pdf = temp[column].mean(axis = 1).to_frame()
        pdf.columns = [column]
        pricedf = pricedf.join(pdf)
    
    vatemp = spot_data[['volume','amt']].unstack()
    vadf = pd.DataFrame(index = vatemp.index)
    for column in ['volume','amt']:
        vdf = vatemp[column].sum(axis = 1).to_frame()
        vdf.columns = [column]
        vadf = vadf.join(vdf)
    
    c = pricedf.join(vadf)
    idx = c.index
    return c.loc[idx.date == datetime.date(date//10000,date%10000//100,date%100)]
    
csvpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_INDEX/CITIC3/'
# 生成结果 每天存储一个csv dt为分钟index， Ticker为3级子行业
def get_CITIC3_minute_data(sd,ed):
    datelist = [int(x.strftime('%Y%m%d')) for x in get_trading_date_range(sd,ed)]
    for i in tqdm(range(len(datelist))):
        
        totaldf = pd.DataFrame()
        date = datelist[i]
 
        c_ticker = get_CITIC_info(date)
        for industry in c_ticker.keys():
           
            mdf = retrieve_stock_minute(date, c_ticker[industry], datelist)
            if i == 0:
                mdf = mdf.fillna(0)
            for column in ['open','high','low','close','vwap']:
                mdf[column] = (mdf[[column]] + 1).cumprod() * pointdict[industry][column]
                pointdict[industry][column] = mdf.iloc[-1][column] #更新每天的初始点位
                
                mdf['Ticker'] = industry
            totaldf = totaldf.append(mdf)
        totaldf = totaldf.reset_index().set_index(['dt','Ticker'])
        totaldf = totaldf.sort_index()
        totaldf.to_csv(os.path.join(csvpath, str(date) + '.csv'))
        
get_CITIC3_minute_data(20180101, 20200717)