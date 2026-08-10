import pandas as pd
import datetime
import numpy as np
from multifactor.IO import IO
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import datetime
from xquant.thirdpartydata.marketdata import MarketData
from multiprocessing.pool import Pool
import os
import glob
from scipy.stats import norm
import math

# If an update is all that needed, then set this variable as False
full_history_construction = False

underlying = '510050.SH'
underlying_name = '华夏上证50ETF'

date_list_all = [date_temp]

# Full History Range
sd = '20180101'
endd = '20210406'

# For daily updates
date_temp = '20210407' 

# 10年期国债收益率读取路径
read_csv_path = '/data/user/016700/rates.csv'



###################### Don't change anything below this line ######################
df2 = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/ChinaOptionDescription/ChinaOptionDescription.h5')
df = df2[df2['S_INFO_NAME'].str.contains(underlying_name)].reset_index()
df['S_INFO_MATURITYDATE'] = df['S_INFO_MATURITYDATE'].astype(float).astype(int).astype(str)
df['S_INFO_MATURITYDATE'] = pd.to_datetime(df['S_INFO_MATURITYDATE'], format='%Y-%m-%d')


def get_trading_date_range(start_date,end_date,dfreq=DFreq.DAILY,dtype=DType.STOCK,mkttype=MktType.CHINA,dsource=DSource.HTSC,alt=None):
    pd_trading_dates=IO.read_data([start_date,end_date],dfreq=dfreq,dtype=dtype,mkttype=mkttype,dsource=dsource,ftype=FType.CALENDAR,alt=alt)
    return pd_trading_dates.index.get_level_values('dt').tolist()

if full_history_construction == True:
    tradingday_list = get_trading_date_range(int(sd), int(endd))
    dftemp = pd.DataFrame()
    dftemp['dt'] = tradingday_list
    dftemp = dftemp.set_index('dt')
    date1 = dftemp.index
    date_list_all = [item[:4]+item[5:7]+item[8:10] for item in list(date1.astype(str))]
else:
    date_list_all = [date_temp]
    

def get_dt(a, b):
    a = a.astype(int)
    b = b.astype(int)
    hour_temp = (b/10000000).astype(int)
    hour = hour_temp.copy().astype(str)
    hour.loc[hour_temp<10] = '0' + hour.loc[hour_temp<10]

    minute_temp = (b/100000-hour_temp*100).astype(int)
    minute = minute_temp.copy().astype(str)
    minute.loc[minute_temp<10] = '0' + minute.loc[minute_temp<10]

    second_temp = (b/1000-hour_temp*10000-minute_temp*100).astype(int)
    second = second_temp.copy().astype(str)
    second.loc[second_temp<10] = '0' + second.loc[second_temp<10]

    m_second_temp = (b%1000).astype(int)
    m_second = m_second_temp.copy().astype(str)
    m_second.loc[m_second_temp<100] = '0' + m_second.loc[m_second_temp<100]
    m_second.loc[m_second_temp<10] = '0' + m_second.loc[m_second_temp<10]

    year_temp = (a/10000).astype(int)
    year = year_temp.astype(str)
    month_temp = ((a - year_temp*10000)/100).astype(int)
    month = month_temp.astype(str)
    month.loc[month_temp<10] = '0' + month.loc[month_temp<10]

    date_temp = (a%100).astype(int)
    date = date_temp.astype(str)
    date.loc[date_temp<10] = '0' + date.loc[date_temp<10]
    result = year + '-' + month + '-' + date + ' ' + hour+':'+minute+':'+second+'.'+m_second
    return pd.to_datetime(result, format='%Y-%m-%d %H:%M:%S.%f')


ma = MarketData()

temp_location = df['S_INFO_NAME'][0].find('认')

def select_dates(df):
    idx = df.index
    t = idx[((idx.hour == 9) & (idx.minute >= 30)) | (idx.hour == 10) | ((idx.hour ==11) & (idx.minute < 30))| (idx.hour == 13) | ((idx.hour == 14) & (idx.minute <= 59))]
    t = list(t.sort_values())
    return df.loc[t] 

def prepare_dates(date_temp, df = df):
    base = pd.Timestamp('%s 09:30:00.000'%date_temp)
    numdays = 500
    date_list = [base + datetime.timedelta(seconds=x*60) for x in range(numdays)]
    date_list1 = [item for item in date_list if (item < pd.Timestamp('%s 15:00:00.000'%date_temp)) & (~((item >= pd.Timestamp('%s 11:30:00.000'%date_temp)) & (item < pd.Timestamp('%s 13:00:00.000'%date_temp))))]
    pd_date = pd.DataFrame()
    pd_date['dt'] = date_list1
    pd_date = pd_date.set_index('dt')

    date_temp_dt = pd.to_datetime(date_temp, format='%Y-%m-%d')

    traded_contract_info = df[(df['dt']<=date_temp_dt)&((date_temp_dt + datetime.timedelta(days = 7))<=df['S_INFO_MATURITYDATE'])]

    temp_name = traded_contract_info['S_INFO_NAME'].unique()

    SE_holder = []
    for i, item in enumerate(temp_name):
        traded_contract_info1 = traded_contract_info.loc[traded_contract_info['S_INFO_NAME'] == item]

        if '沽' in item:
            cp = 'Put'
        else:
            cp = 'Call'
                
        SE_holder.append([cp, item[temp_location-4:temp_location], float(item[temp_location+2:]), traded_contract_info1['S_INFO_MATURITYDATE'].iloc[0], traded_contract_info1['Ticker'].iloc[0], traded_contract_info1['Ticker'].iloc[0]])
    
    return SE_holder, pd_date

def construct_data(item1, underlying, pd_date, date_temp):
    #print(item1)
    df_temp = ma.getMDSecurityTickDataFrame(item1[-1],"%s092500"%date_temp,"%s150000"%date_temp,0)
    df_temp['dt'] = get_dt(df_temp['MDDate'], df_temp['MDTime'])
    df_temp = df_temp.set_index('dt')
    df_temp = df_temp.loc[:, ['OpenPx', 'HighPx',
           'LowPx', 'LastPx', 'TotalVolumeTrade', 'TotalValueTrade',
           'OpenInterest']]
    df_temp['UnderlyingTicker'] = underlying
    df_temp['CallPut'] = item1[0]
    df_temp['Ticker'] = item1[-1]
    volume = df_temp['TotalVolumeTrade'].diff().resample('T').sum()
    amount = df_temp['TotalValueTrade'].diff().resample('T').sum()
    position = df_temp['OpenInterest'].resample('T').last()

    df_temp = df_temp.loc[(df_temp['OpenPx']!=0) & (df_temp['LastPx']!=0) & (df_temp['HighPx']!=0) & (df_temp['LowPx']!=0)]

    high_temp = df_temp['LastPx'].resample('T').max()
    low_temp = df_temp['LastPx'].resample('T').min()
    open_temp = df_temp['LastPx'].resample('T').first()
    close_temp = df_temp['LastPx'].resample('T').last()
    twap = df_temp['LastPx'].resample('T').mean()
    Ticker = df_temp['Ticker'].resample('T').last()

    df_temp_minute = pd.concat([open_temp, close_temp, high_temp, low_temp, twap, volume, amount, position, Ticker], axis = 1)
    
    df_temp_minute['underlyingticker'] = underlying
    df_temp_minute['callput'] = item1[0]
    df_temp_minute['maturitydate'] = item1[3]
    df_temp_minute.columns = ['open', 'close','high','low', 'twap','volume','amount','position', 'Ticker', 'underlyingticker', 'callput', 'maturitydate']
    df_temp_minute = df_temp_minute.loc[~df_temp_minute['close'].isna()]
    #if df_temp_minute['amount'].iloc[0] == 0:
    #    df_temp_minute['amount'].iloc[0] = df_temp['TotalValueTrade'].iloc[0]
    #if df_temp_minute['volume'].iloc[0] == 0:
    #    df_temp_minute['volume'].iloc[0] = df_temp['TotalVolumeTrade'].iloc[0]
    #df_temp_minute = df_temp_minute.loc[~((df_temp_minute.index.minute==30) & (df_temp_minute.index.hour==11))]
    df_minute = pd.concat([pd_date, df_temp_minute], axis = 1)
    df_minute = select_dates(df_minute)
    df_minute = df_minute.where(~df_minute.isnull().all(axis=1), df_minute.fillna(method='ffill'))
    filename = '/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_OPTION/TICK/%s/%s/%s/%s/%s.csv'%(underlying, item1[1], str(item1[2]), item1[-1]+'-'+item1[0], date_temp)
    filename2 = '/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_OPTION/MINUTE/%s/%s/%s/%s/%s.csv'%(underlying, item1[1], str(item1[2]), item1[-1]+'-'+item1[0], date_temp)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not os.path.exists(os.path.dirname(filename2)):
        os.makedirs(os.path.dirname(filename2), exist_ok=True)
    df_temp.to_csv(filename)
    df_minute.to_csv(filename2)

    
def calc(date_temp, underlying = underlying, df = df):
    print(date_temp)
    SE_holder, pd_date = prepare_dates(date_temp, df)
    
    for item1 in SE_holder:
        construct_data(item1, underlying, pd_date, date_temp)
    return 0



with Pool(24) as pool:
    hahahaha = pool.map(calc, date_list_all)
    
    
# Daily updated data for:
#    1. Index Data
#    2. ETF Data
#    3. Treasury Data
# is needed
    
def get_spot_data(underlying):
    index_data = IO.read_data([20161201, 20210331], dtype = DType.INDEX)
    ETF = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUND/MINUTE/MD_CHINA_ETF_MINUTE_59.h5')
    try:
        SPOT = index_data.xs(underlying, level = 1)
        spot_open = SPOT['open']
    except:
        SPOT = ETF.xs(underlying, level = 1)
        spot_open = SPOT['open']
        spot_open = spot_open.groupby(spot_open.index.date).first()
        spot_open.index = pd.to_datetime(spot_open.index)

    return SPOT, spot_open

SPOT, spot_open = get_spot_data(underlying)

data_treasury = pd.read_csv(read_csv_path, encoding="gbk", index_col = 0)
data_treasury.index.name = 'dt'
data_treasury.index = pd.to_datetime(data_treasury.index, format='%Y-%m-%d')
data_treasury.index = data_treasury.index + datetime.timedelta(minutes = 570)

R = data_treasury['r'].shift(1).iloc[1:]

data_spot_r = pd.concat([SPOT, R], axis = 1).loc[SPOT.index]
data_spot_r['r'] = data_spot_r['r'].fillna(method = 'ffill')

def construct_dict(pathlist, everyday, temp_dict = {}, strike_holder = [],  underlying = underlying, etf_open = spot_open):
    
    atm_temp = 1000
    min_diff = 1000
    expir_temp = 1000

    for paths in pathlist:

        spl = paths.split('/')
        expir = spl[11]
        strike = spl[12]
        
        #print(everyday, len(glob.glob('/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_OPTION/MINUTE/510050.SH/%s/*/*/%s.csv'%(everyday[2:6], everyday))))
          
        if len(glob.glob('/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_OPTION/MINUTE/%s/%s/*/*/%s.csv'%(underlying, everyday[2:6], everyday)))>0:

            if expir == everyday[2:6]:

                difff = np.abs(float(strike) - etf_open.loc[everyday])
                if  difff < min_diff:
                    min_diff = difff
                    atm_temp = strike
                    expir_temp = expir
        else:

            if (expir[-2:] != '01' and (int(expir)-int(everyday[2:6]) == 1)) or (expir[-2:] == '01' and (int(expir)-int(everyday[2:6]) == 89)):
                difff = np.abs(float(strike) - etf_open.loc[everyday])
                if  difff < min_diff:
                    min_diff = difff
                    atm_temp = strike
                    expir_temp = expir
                    
        if expir in list(temp_dict.keys()):
            if strike in list(temp_dict[expir].keys()):
                temp_dict[expir][strike].append(paths)
            else:
                temp_dict[expir][strike] = [paths]
        else:
            temp_dict[expir] = {}
            temp_dict[expir][strike] = [paths]
    holder = [0.0]*2
    for item in temp_dict[expir_temp][atm_temp]:
        temp_df = pd.read_csv(item, index_col = 0)
        if '-Call' in item:
            temp_df['strike'] = atm_temp
            holder[0] = temp_df
        else:
            temp_df['strike'] = atm_temp
            holder[1] = temp_df
    #parity = (holder[1]-holder[0])
    #print(parity)
    return holder

def construct_parity(everyday):
    print(everyday)
    pathlist = glob.glob('/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_OPTION/MINUTE/%s/*/*/*/%s.csv'%(underlying, everyday))
    holder = construct_dict(pathlist, everyday)
    return holder

if full_history_construction == True:
    ############ History ############
    with Pool(24) as pool:
        minute_parity_holder = pool.map(construct_parity, date_list_all) 
else:
    with Pool(24) as pool:
        minute_parity_holder = pool.map(construct_parity, [date_temp])

def option_minute_data(minute_parity_holder):
    price_call_atm = [item[0] for item in minute_parity_holder]
    price_put_atm = [item[1] for item in minute_parity_holder]
    price_call_atm = pd.concat(price_call_atm).sort_index()
    price_put_atm = pd.concat(price_put_atm).sort_index()
    #price_call_atm.columns = ['Call_Twap', 'maturitydate', 'Strike']
    #price_put_atm.columns = ['Put_Twap', 'maturitydate', 'Strike']
    price_put_atm['vwap'] = price_put_atm['amount']/price_put_atm['volume']/10000
    price_call_atm['vwap'] = price_call_atm['amount']/price_call_atm['volume']/10000

    price_call_atm.index = pd.to_datetime(price_call_atm.index, format='%Y-%m-%d %H:%M:%S')
    price_put_atm.index = pd.to_datetime(price_put_atm.index, format='%Y-%m-%d %H:%M:%S')

    for_put = pd.concat([data_spot_r['amount']/data_spot_r['volume'], price_put_atm.loc[:, ['twap', 'maturitydate', 'strike']], data_spot_r['r']/100], axis = 1).loc[price_put_atm.index]
    for_call = pd.concat([data_spot_r['amount']/data_spot_r['volume'], price_call_atm.loc[:, ['twap', 'maturitydate', 'strike']], data_spot_r['r']/100], axis = 1).loc[price_call_atm.index]
    for_put = select_dates(for_put)
    for_call = select_dates(for_call)

    for_put.columns = ['spot','twap', 'maturitydate', 'Strike', 'r']
    for_call.columns = ['spot','twap', 'maturitydate', 'Strike', 'r']

    for_put['maturitydate'] = pd.to_datetime(for_put['maturitydate'], format='%Y-%m-%d %H:%M:%S')+ datetime.timedelta(minutes = 16*60)
    for_call['maturitydate'] = pd.to_datetime(for_call['maturitydate'], format='%Y-%m-%d %H:%M:%S')+ datetime.timedelta(minutes = 16*60)

    for_put['t'] = (for_put['maturitydate'] -for_put.index).dt.total_seconds()/3600/24/240
    for_call['t'] = (for_call['maturitydate'] -for_call.index).dt.total_seconds()/3600/24/240
    return price_call_atm, price_put_atm, for_call, for_put

price_call_atm, price_put_atm, for_call, for_put = option_minute_data(minute_parity_holder)


def implied_volatility_call(date, df = for_call):
    P = float(df.loc[date, 'twap'])
    S = float(df.loc[date, 'spot'])
    E = float(df.loc[date, 'Strike'])
    T = float(df.loc[date, 't'])
    r = float(df.loc[date, 'r'])
    sigma = 0.01
    
    while np.min(sigma) < 1:
        d_1 = float(float((np.log(S/E)+(r+(sigma**2)/2)*T))/float((sigma*(np.sqrt(T)))))
        d_2 = float(d_1-sigma*np.sqrt(T))
        P_implied = float(S*norm.cdf(d_1) - E*np.exp(-r*T)*norm.cdf(d_2))
        if np.max(P-(P_implied)) < 0.0005:
            delta = norm.cdf(d_1)
            nn = np.exp(-d_1*d_1/2)/np.sqrt(2*math.pi)
            gamma = nn*float(1/(S*float((sigma*(np.sqrt(T))))))
            theta = 1/240*(-((S*sigma/(2*np.sqrt(T)))*nn) - r*E*np.exp(-r*T)*norm.cdf(d_2))
            vega = nn * S * np.sqrt(T)/100
            rho = E*np.exp(-r*T)*norm.cdf(d_2)/100
            return [date, sigma, delta, gamma, theta, vega, rho]
        sigma +=0.0005
    #print([date, np.nan])
    return [date, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]


def implied_volatility_put(date, df = for_put):
    P = float(df.loc[date, 'twap'])
    S = float(df.loc[date, 'spot'])
    E = float(df.loc[date, 'Strike'])
    T = float(df.loc[date, 't'])
    r = float(df.loc[date, 'r'])
    sigma = 0.01
    while np.min(sigma) < 1:
        d_1 = float(float((math.log(S/E)+(r+(sigma**2)/2)*T))/float((sigma*(math.sqrt(T)))))
        d_2 = float(float((math.log(S/E)+(r-(sigma**2)/2)*T))/float((sigma*(math.sqrt(T)))))
        P_implied = float(-S*norm.cdf(-d_1) + E*math.exp(-r*T)*norm.cdf(-d_2))
        if np.max(P-(P_implied)) < 0.0005:
            delta = norm.cdf(d_1)-1
            nn = np.exp(-d_1*d_1/2)/np.sqrt(2*math.pi)
            gamma = nn*float(1/(S*float((sigma*(np.sqrt(T))))))
            theta = 1/240*(-((S*sigma/(2*np.sqrt(T)))*nn) + r*E*np.exp(-r*T)*norm.cdf(-d_2))
            vega = nn * S * np.sqrt(T)/100
            rho = -E*np.exp(-r*T)*norm.cdf(-d_2)/100
            return [date, sigma, delta, gamma, theta, vega, rho]
        sigma +=0.0005
    #print([date, np.nan])
    return [date, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]

 

def option_greeks_final(for_call = for_call, for_put = for_put):
    day_list_call = list(for_call.index)
    day_list_put = list(for_put.index)
    with Pool(24) as pool:
        hholder_call = pool.map(implied_volatility_call, day_list_call) 
    with Pool(24) as pool:
        hholder_put = pool.map(implied_volatility_put, day_list_put)
    
    call_greeks = pd.DataFrame(hholder_call, columns = ['dt', 'sigma', 'delta', 'gamma', 'theta', 'vega', 'rho'])

    put_greeks = pd.DataFrame(hholder_put, columns = ['dt', 'sigma', 'delta', 'gamma', 'theta', 'vega', 'rho'])
    
    call_greeks = call_greeks.set_index('dt')
    put_greeks = put_greeks.set_index('dt')
    
    return call_greeks, put_greeks

def atm_final(call_greeks, put_greeks, price_call_atm, price_put_atm):
    call_data_temp = pd.concat([price_call_atm, call_greeks], axis = 1).sort_index()
    call_data_temp.set_index('Ticker', append = True, inplace = True)
    put_data_temp = pd.concat([price_put_atm, put_greeks], axis = 1).sort_index()
    put_data_temp.set_index('Ticker', append = True, inplace = True)
    return pd.concat([call_data_temp, put_data_temp]).sort_index()



call_greeks, put_greeks = option_greeks_final()
atm_temp = atm_final(call_greeks, put_greeks, price_call_atm, price_put_atm)
atm_temp.to_hdf('/data/user')