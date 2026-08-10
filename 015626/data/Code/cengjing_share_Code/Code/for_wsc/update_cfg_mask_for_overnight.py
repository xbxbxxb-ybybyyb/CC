from multifactor.IO import IO
import pandas as pd
import os
import datetime
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool

from multifactor.data.utils import *
import multifactor.utility.dt as udt
import time

import warnings
warnings.filterwarnings('ignore')


def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(year,month,day,hour,minute,0)

def select_index(adf):
    idx = adf.index.get_level_values(0)
    t1 = adf.loc[(idx.hour == 9) & (idx.minute >= 30)]
    t2 = adf.loc[(idx.hour == 10) | (idx.hour == 13)]
    t3 = adf.loc[(idx.hour == 11) & (idx.minute < 30)]
    t4 = adf.loc[(idx.hour == 14) & (idx.minute <= 57)]
    t = t1.append(t2).append(t3).append(t4)
    t = t.sort_index()
    return t

# calculate turnover
def add_turnover(df, stock):
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = IO.read_data([20080710, 21000101],columns = ['CHANGE_DT', 'FLOAT_A_SHR'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareCapitalization/AShareCapitalization.h5')
    ashare = ashare.xs(stock, level = 1).reset_index()
    ashare = ashare.drop('dt', axis = 1)
    temp = df[['CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT'])
    temp2['FLOAT_A_SHR'] = temp2['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= 20100101]
    temp2 = temp2.drop_duplicates(keep = 'last')

    totaldf = pd.merge(df, temp2, on=['CHANGE_DT'], how = 'left')

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)
    totaldf['turnover'] = totaldf.volume / totaldf.float_shares / 100
#     totaldf = totaldf.set_index(['dt','Ticker'])
    totaldf = totaldf.set_index(['dt'])
    totaldf = totaldf.sort_index()

    return totaldf

def add_weight(totaldf, u):
    totaldf = totaldf.reset_index().rename(columns = {'dt':'minute'})
    totaldf['dt'] = totaldf.minute.apply(lambda x:x.date())
    totaldf = totaldf.set_index(['dt','Ticker'])

    u = u.reset_index().rename(columns = {'sp_ticker':'Ticker'}).set_index(['dt','Ticker'])
    df = totaldf.join(u, how = 'left')
    df = df.reset_index()
    df = df.drop('dt', axis = 1)
    df = df.rename(columns = {'minute':'dt'})
    df = df.set_index(['dt','Ticker']).sort_index()
    
    return df
    
def minute_flag_check(date,today):
    path1 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_MINUTE.success'
    path2 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_INDEX_WEIGHT.success'
    path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_spot_minute.success'
    path4 = '/data/user/012245/warehouse/flags/%s/%s_ADJFACTOR_RT.success' % (today, today)
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)


sdate,flag_date,cdate_list = check_update_date()
today_date = datetime.date.today() # 获取今天的日期
ticker = 'IC.CFE'
dayspast_preadj = 30 # 向前前复权多少个自然日
startdate, enddate = 20110101,21000101
pkl_savepath = '/data/user/015626/data/share/LOCAL_DATA/for_wsc/noondata_for_overnight/'
flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(flag_date) + '/'

if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(flag_date) + '_' + '%s_cfg_and_mask_noondata_for_overnight.start' % ticker[:2]
with open(flag_path_start,'w') as file:
    pass 

print('------wait minute flag')
while True:
    if minute_flag_check(sdate, str(today_date).replace('-','')):
        break
    time.sleep(60)
print('flag check finished!')
    


tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
savenamedict = {'IC.CFE':'zz500','IF.CFE':'hs300','IH.CFE':'sh50'}


# 挑选出来成分股股票列表
tickercolumn = tickerdict[ticker]
indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
# 加上今天的数据
today_iw = indexweight.loc[str(flag_date)].reset_index()
today_iw['dt'] = today_date
today_iw[tickercolumn] = np.nan
indexweight = indexweight.append(today_iw.set_index(['dt','Ticker']))

indexweight = indexweight.unstack().shift(1).stack()
universe = indexweight[indexweight[tickercolumn]>0]
universe = universe.reset_index()
stklist = universe.Ticker.unique().tolist()

# 获取历史上每支股票的adjfactor
stkdaily = IO.read_data([startdate, enddate],columns = ['adjfactor'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

# 加上今天的数据
today_stkadj = pd.read_hdf('/data/user/012245/warehouse/prod/market/adjfactor_rt/%s.h5' % str(today_date).replace('-','')).to_frame()
today_stkadj.columns = ['adjfactor']
today_stkadj['dt'] = today_date
stkdaily = stkdaily.append(today_stkadj.reset_index().set_index(['dt','Ticker']))

stkdaily = stkdaily.unstack()
stkdaily = stkdaily.droplevel(0, axis = 1).reset_index()
stkdaily = stkdaily[['dt']+stklist]
stkdaily = stkdaily.fillna(method = 'ffill')
stkdaily = stkdaily.fillna(0).set_index('dt')
full_maskdf = stkdaily != stkdaily.shift(1)
maskdf = (abs(stkdaily / stkdaily.shift(1) - 1) > 0.08) # adjfactor变动要大于0.08，小于的有可能是现金分红
maskdf.iloc[0,:] = True
full_stkdaily = stkdaily[full_maskdf].reset_index()
stkdaily = stkdaily[maskdf].reset_index()

# 获取每支股票adjfactor改变的日期
adj_chgdate_dict = {}
for stock in tqdm(stklist):
    stk_adj_chg_df = stkdaily[~stkdaily[stock].isna()][['dt',stock]]
    adj_chgdate_list = stk_adj_chg_df['dt'].to_list()
    adj_chgdate_dict[stock] = adj_chgdate_list
    
# 获取每天对应的股票名称    
def get_specific_stk(date, stock):
    datelist = adj_chgdate_dict[stock]
    for i in range(len(datelist) - 1):
        if (date >= datelist[i]) & (date < datelist[i+1]):
            return stock + '_v' + str(i)
    return stock + '_v' + str(len(datelist) - 1)

universe['sp_ticker'] = universe.apply(lambda x:get_specific_stk(x['dt'],x['Ticker']), axis = 1)
universe['num'] = universe['sp_ticker'].apply(lambda x:int(x.split('_v')[1]))


sp_start_date = universe.reset_index().groupby(['sp_ticker']).agg({'dt': lambda x:x.head(1)})
sp_end_date = universe.reset_index().groupby(['sp_ticker']).agg({'dt': lambda x:x.tail(1)})
sp_start_date['date'] = sp_start_date.dt.apply(lambda x:x - datetime.timedelta(days = dayspast_preadj))
start_date_dict = sp_start_date[['date']].to_dict()['date']
end_date_dict = sp_end_date.to_dict()['dt']

stock_version_dict = {}
for stock in stklist:
    stock_version_dict[stock] = universe[universe.Ticker == stock].num.unique().tolist()

universe = universe.set_index(['dt','Ticker']).sort_index()

#IO.pd_hdf5_writer(universe, os.path.join(savepath,'daily',savenamedict[ticker]+'_universe.h5'), dataset = 'universe')
# 读取今日股票数据
today_stock_mdata = pd.read_hdf('/data/user/015626/data/share/LOCAL_DATA/for_wsc/%s.h5' % str(today_date).replace('-','')).reset_index(level = 1)
# 针对性的处理股票
def get_sp_stock(stock):
    print(stock)
    stk_adj_chg_df = stkdaily[~stkdaily[stock].isna()][['dt',stock]]
    adj_chgdate_list = stk_adj_chg_df['dt'].to_list()
    adj_chg_list = stk_adj_chg_df[stock].to_list()
    
    full_stk_adj_chg_df = full_stkdaily[~full_stkdaily[stock].isna()][['dt',stock]]
    full_adj_chg_list = full_stk_adj_chg_df[stock].to_list()
    
    if len(adj_chg_list) > 1:
        assert adj_chg_list[1] != 0
    else:
        assert adj_chg_list[0] != 0
    
    minsdata_rootpath = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'
    pklpath = os.path.join(minsdata_rootpath,'UnAdjstedStockMinute_' + stock[:6] + '.pkl')
    if not os.path.exists(pklpath):
        return
    stk_full_mins_data = pd.read_pickle(pklpath, compression='gzip').reset_index()
    stk_full_mins_data = stk_full_mins_data[stk_full_mins_data.dt >= 20190101]
    if len(stk_full_mins_data) == 0:
        return
    stk_full_mins_data['Ticker'] = stk_full_mins_data.Ticker.apply(lambda x:ticker_match(x))
    stk_full_mins_data = stk_full_mins_data.rename(columns = {'dt':'date'})
    stk_full_mins_data['dt'] = stk_full_mins_data.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
    stk_full_mins_data = stk_full_mins_data.drop(['date','minute'], axis = 1)
    stk_full_mins_data = stk_full_mins_data.rename(columns = {'amt':'amount'})
    stk_full_mins_data = stk_full_mins_data.set_index('dt').append(today_stock_mdata[today_stock_mdata.Ticker == stock].sort_index())
    
    stk_full_mins_data = select_index(stk_full_mins_data)

#    stk_full_mins_data = add_turnover(stk_full_mins_data, stock)
    
    idx = stk_full_mins_data.index
    plist = ['open','high','low','close']
    stkdf = pd.DataFrame()
    for i in range(len(adj_chg_list)):
        if i not in stock_version_dict[stock]:
            continue
            
        if len(adj_chg_list) == 1:
            tempdf = stk_full_mins_data.loc[idx >= adj_chgdate_list[i]]
            newticker = stock+'_v'+str(i)
            tempdf['Ticker'] = newticker
            tempdf = tempdf.loc[tempdf.index >= start_date_dict[newticker]]
            tempdf = tempdf.loc[tempdf.index < (end_date_dict[newticker] + datetime.timedelta(days = 1))]
            stkdf = stkdf.append(tempdf)
            break
            
            
        if i == 0:
            tempdf = stk_full_mins_data.loc[(idx >= adj_chgdate_list[i]) & (idx < adj_chgdate_list[i + 1])]
            if len(tempdf) == 0:
                continue
        else:
            tempdf1 = stk_full_mins_data.loc[(idx >= (adj_chgdate_list[i] - datetime.timedelta(days = dayspast_preadj))) & (idx < adj_chgdate_list[i])]
            adj = full_adj_chg_list[full_adj_chg_list.index(adj_chg_list[i]) - 1] / adj_chg_list[i]
            tempdf1[plist] = tempdf1[plist] * adj
            tempdf1['volume'] = tempdf1['volume'] / adj

            if i == (len(adj_chg_list) - 1):
                tempdf2 = stk_full_mins_data.loc[idx >= adj_chgdate_list[i]]
            else:
                tempdf2 = stk_full_mins_data.loc[(idx >= adj_chgdate_list[i]) & (idx < adj_chgdate_list[i + 1])]
            tempdf = tempdf1.append(tempdf2)
        newticker = stock+'_v'+str(i)
        tempdf['Ticker'] = newticker

        tempdf = tempdf.loc[tempdf.index >= start_date_dict[newticker]]
        tempdf = tempdf.loc[tempdf.index < (end_date_dict[newticker] + datetime.timedelta(days = 1))]
        stkdf = stkdf.append(tempdf)

    if len(stkdf) == 0:
        return

    stkdf['PROD_ID'] = stock
    stkdf = stkdf.reset_index().set_index(['dt','Ticker'])

    u = universe.xs(stock, level = 1)[[tickerdict[ticker],'sp_ticker']]
    u = u.rename(columns = {tickerdict[ticker]:'weight'})

    stkdf = add_weight(stkdf, u)

#    IO.pd_hdf5_writer(stkdf, os.path.join(savepath, 'CFG_MINUTE', savenamedict[ticker], stock+'.h5'), dataset = stock)
    return stkdf
        
finaldf = pd.DataFrame()
with Pool(processes = 24) as pool:
    dflist = pool.map(get_sp_stock, stklist)
    finaldf = pd.concat(dflist, axis = 0).sort_index()
    finaldf = finaldf.add_suffix('_' + savenamedict[ticker])
    
    df20 = finaldf.loc[finaldf.index.get_level_values(0) >= pd.to_datetime('20200101')]
#    df20.to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/CFG_DATA/temp_data/'+ticker[:2]+'_STOCKS_MINUTE_DATA_2020.pkl')
    
# 生成mask
df20 = df20.loc[pd.to_datetime('20200101'):].sort_index()
a = df20.copy()
mask_dict_20 = {}
suffix = '_' + savenamedict[ticker]
starttime = int(str(df20.reset_index().iloc[0]['dt'].date()).replace('-',''))
endtime = int(str(df20.reset_index().iloc[-1]['dt'].date() + datetime.timedelta(days = 1)).replace('-',''))
picklesavename = ticker[:2] + '_cfg_data_2020_for_overnight.pkl'

stk_weight = a[['weight' + suffix]].unstack().droplevel(0,axis =1)
stk_close = a[['close' + suffix]].unstack().droplevel(0,axis =1)

true_mask = stk_weight.copy()
true_mask[~true_mask.isna()] = 1

weight_mask = stk_weight.copy()

weight_boolean_mask = (stk_weight > 0)
mask_dict_20['weight_boolean' + suffix] = weight_boolean_mask

weight_rank_mask = 2 * weight_mask.rank(axis=1, pct=True) - 1

import bottleneck as bk
def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

stk_ret = stk_close.pct_change(1, fill_method=None)
stk_volatility_mask = ts_std(stk_ret, 15) * true_mask
mask_dict_20['stk_volatility' + suffix] = stk_volatility_mask

#index_data = IO.read_data([starttime, endtime], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
#index_close = index_data['close_spot'].xs(ticker, level = 1)
#index_ret = index_close.pct_change(1, fill_method=None)
#stk_index_corr_mask = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
#stk_index_corr_mask = stk_index_corr_mask.replace([-np.inf, np.inf], np.nan)
#stk_index_corr_mask = stk_index_corr_mask * true_mask
#mask_dict_20['stk_index_corr' + suffix] = stk_index_corr_mask

import pickle

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
    
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict
    
df20dict = {}
for x in df20.columns:
    if 'PR' in x:       
        continue
    df20dict[x] = df20[[x]].unstack().droplevel(0,axis =1)
    
df20dict.update(mask_dict_20)
df20dict.keys()
shape_standard = df20dict['close'+suffix].shape
#assert np.all([df20dict[key].shape == shape_standard for key in df20dict.keys()]) == True
save_pickle(df20dict, os.path.join(pkl_savepath, picklesavename))


flag_path_success = flag_root + str(flag_date) + '_' + '%s_cfg_and_mask_noondata_for_overnight.success' % ticker[:2]
with open(flag_path_success,'w') as file:
    pass