from xquant.compute.aimr import AIMR
param=AIMR.getParam()
print(param)
prod_id = param

import subprocess
package_name = "/data/user/019073/marketdata/installer_and_demo/xdb-2.0.0-cp38-cp38-linux_x86_64.whl"  # 要安装的包名
subprocess.check_call(["pip", "install", package_name])

with open('/dfs/user/015626/JupyterNotebooks/utils/imports.txt', 'r') as file:
    code = file.read()
    exec(code)
from xdb.futuredata import FutureData

def rm_minimum(data, x=np.nan):
    data[abs(data) < 1e-8] = x
    return data

def get_freq_to_min(freq):
    if freq.lower().endswith('min'):
        return int(freq.lower().replace('min', ''))
    elif freq.lower().endswith('h'):
        return int(freq.lower().replace('h', '')) * 60
    elif freq.lower().endswith('s'):
        return int(freq.lower().replace('s', '')) / 60

# 高端乘数
ccp = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/WIND_CFuturesContPro.csv')
ccp = ccp[['S_INFO_CEMULTIPLIER','S_INFO_DMEAN',  'S_INFO_PUNIT',  'S_INFO_WINDCODE']]
ccp = ccp.rename(columns = {'S_INFO_WINDCODE':'Ticker'})
ccp['multiplier'] = ccp['S_INFO_CEMULTIPLIER'].fillna(ccp['S_INFO_PUNIT'])
ccp = ccp.set_index('Ticker')
multiplier_dict = ccp['multiplier'].to_dict()

make0nan_columns = ['open','high','low','close','twap','vwap','Buy1Price_mean','Sell1Price_mean']
ffill_columns = ['open','high','low','close','twap','vwap','Buy1Price_mean','Sell1Price_mean','HTSCSecurityID','Ticker', 'tday', 'oi']
ffill_px_columns = ['open','high','low','close','twap','vwap','Buy1Price_mean','Sell1Price_mean']
fill0_columns = ['amount', 'OBI', 'Sell1OrderQty_mean', 'BidAskSpreadMean','PxVolCorr', 'PxVolCorr_n_4','volume', 'AbsPxPath',  'Buy1OrderQty_mean','first_10_volume', 'first_10_ret',
        'last_n_4_volume', 'last_n_4_ret','last_n_20_volume', 'last_n_20_ret', 'buy_active', 'sell_active', 'last_to_mid', 
        'last_to_weighted_mid', 'idmin', 'idmax', 'volume_after_min', 'volume_after_max', 
        'buy_big_volume', 'buy_big_count', 'sell_big_volume', 'sell_big_count', 'buy_super_volume', 
        'buy_super_count', 'sell_super_volume', 'sell_super_count', 'buy_small_volume', 'buy_small_count', 'sell_small_volume', 'sell_small_count',
        'buy_gigantic_volume', 'buy_gigantic_count', 'sell_gigantic_volume', 'sell_gigantic_count',
        'buy_big_volume_n_4', 'buy_big_count_n_4', 'sell_big_volume_n_4', 'sell_big_count_n_4', 
        'buy_big_volume_n_20', 'buy_big_count_n_20', 'sell_big_volume_n_20', 'sell_big_count_n_20', 
        'buy_super_volume_n_20', 'buy_super_count_n_20', 'sell_super_volume_n_20', 'sell_super_count_n_20', 'buy_small_volume_n_20', 'buy_small_count_n_20', 'sell_small_volume_n_20', 'sell_small_count_n_20',
        'buy_active_n_20', 'sell_active_n_20', 'last_to_mid_n_20', 'PxVolCorr_n_20', 
        'buy_gigantic_volume_n_20', 'buy_gigantic_count_n_20', 'sell_gigantic_volume_n_20', 'sell_gigantic_count_n_20','buy_gigantic_volume_n_4', 
                 'buy_gigantic_count_n_4', 'sell_super_count_n_4', 'sell_super_volume_n_4', 'buy_super_count_n_4', 'buy_super_volume_n_4', 
                 'sell_gigantic_volume_n_4', 'sell_gigantic_count_n_4', 'sell_small_count_n_4', 'sell_small_volume_n_4', 'sell_active_n_4', 
                 'last_to_mid_n_4', 'buy_small_count_n_4', 'buy_small_volume_n_4', 'buy_active_n_4' ]
rule_dict = {x:'last'  for x in ['open', 'high', 'low', 'close', 'twap', 'HTSCSecurityID',
        'volume', 'amount', 'AbsPxPath', 
       'OBI', 'BidAskSpreadMean',
       'Buy1Price_mean', 'Buy1OrderQty_mean', 'Sell1Price_mean',
       'Sell1OrderQty_mean', 'PxVolCorr', 'tday', 'oi',
         'buy_active', 'sell_active', 
        'first_10_volume', 'first_10_ret',
         'last_n_4_volume', 'last_n_4_ret', 'last_n_20_volume', 'last_n_20_ret', 'last_to_mid', 'last_to_weighted_mid', 'idmin', 'idmax', 
                                 'volume_after_min', 'volume_after_max', 
                                 'buy_big_volume', 'buy_big_count', 'sell_big_volume', 'sell_big_count', 
                                 'buy_super_volume', 'buy_super_count', 'sell_super_volume', 'sell_super_count',
                                 'buy_small_volume', 'buy_small_count', 'sell_small_volume', 'sell_small_count',
                                 'buy_gigantic_volume', 'buy_gigantic_count', 'sell_gigantic_volume', 'sell_gigantic_count',
                                 'buy_big_volume_n_4', 'buy_big_count_n_4', 'sell_big_volume_n_4', 'sell_big_count_n_4', 
                                 'buy_super_volume_n_4', 'buy_super_count_n_4', 'sell_super_volume_n_4', 'sell_super_count_n_4', 
                                 'buy_small_volume_n_4', 'buy_small_count_n_4', 'sell_small_volume_n_4', 'sell_small_count_n_4', 
                                 'buy_active_n_4', 'sell_active_n_4', 'last_to_mid_n_4', 'PxVolCorr_n_4',                      
                                 'buy_gigantic_volume_n_4', 'buy_gigantic_count_n_4', 'sell_gigantic_volume_n_4', 'sell_gigantic_count_n_4',
                                 'buy_big_volume_n_20', 'buy_big_count_n_20', 'sell_big_volume_n_20', 'sell_big_count_n_20', 
                                 'buy_super_volume_n_20', 'buy_super_count_n_20', 'sell_super_volume_n_20', 'sell_super_count_n_20', 'buy_small_volume_n_20', 'buy_small_count_n_20', 'sell_small_volume_n_20', 'sell_small_count_n_20',
                                 'buy_active_n_20', 'sell_active_n_20', 'last_to_mid_n_20', 'PxVolCorr_n_20', 
                                 'buy_gigantic_volume_n_20', 'buy_gigantic_count_n_20', 'sell_gigantic_volume_n_20', 'sell_gigantic_count_n_20' ]                   
            }
rule_dict.update({'open':'first','high':'max','low':'min','volume':'sum','amount':'sum'})
as_fl_list = ['PreOpenInterest', 'PreClosePx', 'PreSettlePrice', 'OpenPx', 'HighPx', 'LowPx', 'LastPx',
       'TotalVolumeTrade', 'TotalValueTrade', 'OpenInterest', 'ClosePx', 'Buy1Price', 'Buy1OrderQty', 'Sell1Price', 'Sell1OrderQty']

columns_mapping = {'symbol':'HTSCSecurityID', 'md_date':'MDDate', 'md_time':'MDTime', 'ask_p0':'Sell1Price', 'ask_qty0':'Sell1OrderQty', 'bid_p0':'Buy1Price', 'bid_qty0':'Buy1OrderQty', 'pre_close_px':'PreClosePx', 'open':'OpenPx', 'close':'ClosePx', 'last':'LastPx', 'high':'HighPx', 'low':'LowPx', 'pre_open_interest':'PreOpenInterest', 'pre_settle_price':'PreSettlePrice', 'open_interest':'OpenInterest',
       'settle_price':'SettlePrice', 'total_volume':'TotalVolumeTrade', 'total_amount':'TotalValueTrade'}
    
import re

def format_string(s):
    # 正则表达式：允许前缀和后缀为任意长度的字母
    match = re.fullmatch(r'([A-Za-z]+)(\d{3,4})\.([A-Za-z]+)', s)
    if not match:
        return s  # 如果格式不匹配，返回原字符串
    prefix, digits, suffix = match.groups()
    # 保留数字的后三位
    formatted_digits = digits[-3:]
    return f"{prefix}{formatted_digits}.{suffix}"
    
# date = '20170626'
# ticker =  "TA709.ZCE"
def get_minute_data(para):
    try:
        date = para[0]
        ticker = para[1].replace('CZC', 'ZCE').replace('CFE', 'CF')
        if ticker.endswith('ZCE'):
            ticker = format_string(ticker)
        if os.path.exists(os.path.join(csv_rootpath, f'{date}_{ticker}.csv')):
            return
        fd = FutureData()
        tick = fd.get_tickex(date, ticker)
        del(fd)
        if tick is None or len(tick) == 0:
#            print(para, 'no tick!')
            return
        if ticker.endswith('CF'):
            if ticker[:2] in ['IC', 'IM']:
                multiplier = 200
            elif ticker[:2] in ['IF', 'IH']:
                multiplier = 300
            elif ticker[:2] in ['TF', 'TL']:
                multiplier = 10000
            elif ticker[:2] in ['TS']:
                multiplier = 20000
            elif ticker[:1] in ['T']:
                multiplier = 10000
        else:
            multiplier = multiplier_dict.get(ticker)
        if multiplier is None:
            multiplier = multiplier_dict.get(ticker.replace('ZCE', 'CZC'))
        assert multiplier is not None, f'{ticker} no multiplier'
        tick = tick.rename(columns = columns_mapping)
        tick['TradingDate'] = date
        
        tick['volume'] = tick['TotalVolumeTrade'].fillna(method = 'ffill').diff().fillna(tick['TotalVolumeTrade'])
        tick['amount'] = tick['TotalValueTrade'].fillna(method = 'ffill').diff().fillna(tick['TotalValueTrade'])
        
        tick = tick[(tick.TotalVolumeTrade != 0) & (tick.TotalValueTrade != 0) & (tick['LastPx'] < tick['PreSettlePrice'] * 1.3) & (tick['LastPx'] > tick['PreSettlePrice'] * 0.7) & \
            (tick['HighPx'] < tick['PreSettlePrice'] * 1.3) & (tick['HighPx'] > tick['PreSettlePrice'] * 0.7) & \
            (tick['LowPx']  < tick['PreSettlePrice'] * 1.3) & (tick['LowPx']  > tick['PreSettlePrice'] * 0.7) & \
            (tick['LowPx']  <= tick['HighPx']) & (tick['LowPx']  >= tick['HighPx'] / 1.6) & (tick.OpenPx !=0)]  
        
        if len(tick) == 0:
#            print(para, 'no tick after select')
            return
            
        openpx = tick['OpenPx'].mode()[0]
        preclosepx = tick['PreClosePx'].mode()[0]
        PreOpenInterest = tick['PreOpenInterest'].mode()[0]
        tick = tick[(tick['OpenPx'] == openpx) & (tick['PreClosePx'] == preclosepx) & (tick['PreOpenInterest'] == PreOpenInterest)]
        if ticker.endswith('CZC') or ticker.endswith('ZCE'):
            tick['amount'] = tick['amount'] * multiplier
        tick_vwap = tick['amount'] / tick['volume'] / multiplier
        
        if 'CZC' in ticker or 'ZCE' in ticker:
            if (tick_vwap.iloc[:100].mean() / tick['LastPx'].iloc[:100].mean()) > (multiplier / 2):
                tick['amount'] = tick['amount'] / multiplier
                tick_vwap = tick['amount'] / tick['volume'] / multiplier
        
        
        def getdt(a, b):
            strdate = str(a) + ' ' + str(b).zfill(9)
            return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
        tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        # 规整时间
        tick = tick.set_index(['dt'])
        if tick['volume'].between_time('2100','0229').sum() > 0:
            tick = pd.concat([pd.DataFrame(index = [tick.index[0].replace(hour = 19)]), tick])
        else:
            tick = pd.concat([pd.DataFrame(index = [tick.index[0].replace(hour = 7)]), tick])
            
        tick = pd.concat([tick, pd.DataFrame(index = [tick.index[-1].replace(hour = 16)])])
        tick.index.name = 'dt'
        tick = tick.sort_index()
        
        if str.upper(freq) == '1H':
            temp = tick.loc[f'{date} 113000':f'{date} 135959']
            tick = tick.drop(temp.index)
            temp2 = temp.loc[f'{date} 133000':f'{date} 135959']
            temp2.index = temp2.index.map(lambda x: x.replace(hour=11))
            tick = pd.concat([tick, temp2]).sort_index()
        
        tick = tick.reset_index()
        
        fill_na_columns = ['Buy1Price','Sell1Price','LastPx']
        tick[fill_na_columns] =  tick[fill_na_columns].replace(0,np.nan)
        
        tick['Sell1Price'] = tick['Sell1Price'].astype(float)
        tick['Buy1Price'] = tick['Buy1Price'].astype(float)
        tick[['Sell1Price', 'Buy1Price']] = tick[['Sell1Price', 'Buy1Price']].replace(0, np.nan)
        
        tick.loc[(tick['Buy1Price'] > tick['Sell1Price']) & (~np.isnan(tick['Sell1Price'])), 'Buy1Price'] = np.nan
        tick['pd'] = tick['OpenInterest'].diff()
        
        med = tick['LastPx'].copy()
        tick['Sell1Price'][tick['Sell1Price'] > (med * 1.1)] = np.nan
        tick['Sell1Price'][tick['Sell1Price'] < (med / 1.1)] = np.nan
        tick['Buy1Price'][tick['Buy1Price'] > (med * 1.1)] = np.nan
        tick['Buy1Price'][tick['Buy1Price'] < (med / 1.1)] = np.nan
        
        midprice = tick[['Sell1Price', 'Buy1Price']].mean(axis = 1).fillna(method = 'ffill')
        tick_vwap = (tick['amount'] / tick['volume'].replace(0, np.nan) / multiplier).fillna(method = 'ffill')
        
        mean_mid =  midprice.mean()
        mean_vwap = tick_vwap.mean()
        
        if (np.isnan(mean_vwap)) & (np.isnan(mean_mid)):
            tick_vwap = tick['LastPx'].copy()
            midprice = tick['LastPx'].copy()
        elif (np.isnan(mean_vwap)) & (~np.isnan(mean_mid)):
            tick_vwap = midprice.copy()
        elif (~np.isnan(mean_vwap)) & (np.isnan(mean_mid)):
            midprice = tick_vwap.copy()
        if not (ticker.endswith('CZC') or ticker.endswith('ZCE')):
            assert abs(tick_vwap.mean() / midprice.mean() - 1) < 0.2,  f'{para} vwap/mid has problem'

        
        if ticker.endswith('CZC') or ticker.endswith('ZCE'):
            # Lee-Ready
            tick['zbuy'] = ((tick['LastPx'] > midprice.shift(1)) | ((tick['LastPx'] == midprice.shift(1)) &  (midprice > midprice.shift()))) * tick['volume']
            tick['zsell'] = ((tick['LastPx'] < midprice.shift(1)) | ((tick['LastPx'] == midprice.shift(1)) &  (midprice < midprice.shift()))) * tick['volume']
        else:
            # self-made
            tick['zbuy'] = ((tick_vwap > midprice.shift(1)) | ((tick_vwap == midprice.shift()) & (midprice > midprice.shift()))) * tick['volume']
            tick['zsell'] = ((tick_vwap < midprice.shift(1)) | ((tick_vwap == midprice.shift()) & (midprice < midprice.shift()))) * tick['volume']     
        
        tick['minute'] = tick.dt.map(lambda x: x.replace(second=0, microsecond = 0))
        tick = tick.set_index('dt')
        tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
        tick['pricediff'] = abs(tick.LastPx.diff())
        tick[['Buy1Price','Buy1OrderQty']] = tick[['Buy1Price','Buy1OrderQty']].astype('float64')
        
        tick['BidAskSpreadMean'] = tick['Sell1Price'] - tick['Buy1Price']
        tick['BidAskSpreadMean'][tick['BidAskSpreadMean'] == tick['Sell1Price']] = np.nan
        tick['BidAskSpreadMean'][tick['BidAskSpreadMean'] == -tick['Buy1Price']] = np.nan
        for x in ['open','high','low','close','twap']:
            tick[x] = tick['LastPx']
        for x in ['Buy1Price','Buy1OrderQty','Sell1Price','Sell1OrderQty']:
            tick['%s_mean' % x] = tick[x]
        
        aggdict_ohlc = {'open':'first','high':'max','low':'min','close':'last','twap':'mean'}
        
        tick['n_min'] = tick.index.floor(freq)
        
        tick['is_first_10s'] = (tick.index - tick['n_min']) <= pd.Timedelta('10s')
        
        zbuy = tick.groupby('n_min')['zbuy'].sum()
        zsell = tick.groupby('n_min')['zsell'].sum()
        #trade_will.name = 'trade_will'
        zbuy.name = 'buy_active'
        zsell.name = 'sell_active'
        
        # 区分大小单
        fd = FutureData()
        ptdays = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(udt.get_trading_day_offset(date, -5)[0], udt.get_trading_day_offset(date, -1)[0])]
        ptick_list = []
        for p in ptdays:
            ptick = fd.get_tickex(p, ticker).rename(columns = columns_mapping)['TotalVolumeTrade'].diff()
            if len(ptick) > 0:
                ptick_list.append(ptick)
        del(fd)
        if len(ptick_list) > 0:
            gigantic_t = np.nanmean([x.quantile(0.95) for x in ptick_list])
            super_t = np.nanmean([x.quantile(0.9) for x in ptick_list])
            big_t = np.nanmean([x.quantile(0.8) for x in ptick_list])
            small_t = np.nanmean([x[x > 0].quantile(0.5) for x in ptick_list])
        else:
            ptick = tick['TotalVolumeTrade'].diff()
            gigantic_t = ptick.quantile(0.95)
            super_t = ptick.quantile(0.9)
            big_t = ptick.quantile(0.8)
            di_order = ptick[ptick>0]
            small_t = di_order.quantile(0.5)
        
        _zbuy_temp = tick[(tick['zbuy'] > big_t) & (tick['zbuy'] <= super_t)].groupby('n_min')
        _zsell_temp = tick[(tick['zsell'] > big_t) & (tick['zsell'] <= super_t)].groupby('n_min')
        big_buy = _zbuy_temp['zbuy'].sum()
        big_sell = _zsell_temp['zsell'].sum()
        big_buy_count = _zbuy_temp['zbuy'].count()
        big_sell_count = _zsell_temp['zsell'].count()
        big_sell.name = 'sell_big_volume'
        big_sell_count.name = 'sell_big_count'
        big_buy.name = 'buy_big_volume'
        big_buy_count.name = 'buy_big_count'
        
        _zbuy_temp = tick[(tick['zbuy'] > super_t) & (tick['zbuy'] <= gigantic_t)].groupby('n_min')
        _zsell_temp = tick[(tick['zsell'] > super_t) & (tick['zsell'] <= gigantic_t)].groupby('n_min')
        super_buy = _zbuy_temp['zbuy'].sum()
        super_sell = _zsell_temp['zsell'].sum()
        super_buy_count = _zbuy_temp['zbuy'].count()
        super_sell_count = _zsell_temp['zsell'].count()
        super_sell.name = 'sell_super_volume'
        super_sell_count.name = 'sell_super_count'
        super_buy.name = 'buy_super_volume'
        super_buy_count.name = 'buy_super_count'
        
        _zbuy_temp = tick[(tick['zbuy'] > gigantic_t)].groupby('n_min')
        _zsell_temp = tick[(tick['zsell'] > gigantic_t)].groupby('n_min')
        gigantic_buy = _zbuy_temp['zbuy'].sum()
        gigantic_sell = _zsell_temp['zsell'].sum()
        gigantic_buy_count = _zbuy_temp['zbuy'].count()
        gigantic_sell_count = _zsell_temp['zsell'].count()
        gigantic_sell.name = 'sell_gigantic_volume'
        gigantic_sell_count.name = 'sell_gigantic_count'
        gigantic_buy.name = 'buy_gigantic_volume'
        gigantic_buy_count.name = 'buy_gigantic_count'
        
        _zbuy_temp = tick[tick['zbuy'] <= small_t].groupby('n_min')
        _zsell_temp = tick[tick['zsell'] <= small_t].groupby('n_min')
        small_buy = _zbuy_temp['zbuy'].sum()
        small_sell = _zsell_temp['zsell'].sum()
        small_buy_count = _zbuy_temp['zbuy'].count()
        small_sell_count = _zsell_temp['zsell'].count()
        small_sell.name = 'sell_small_volume'
        small_sell_count.name = 'sell_small_count'
        small_buy.name = 'buy_small_volume'
        small_buy_count.name = 'buy_small_count'
        
        try:
            pvcorrdf = tick[['n_min','LastPx','volume']].groupby('n_min').corr().xs('LastPx', level = 1)[['volume']]
            pvcorrdf.columns = ['PxVolCorr']
        except:
            pvcorrdf = pd.DataFrame(columns = ['PxVolCorr'])
        
        # 计算每个n分钟时间段内前10秒的成交量平均值
        group_10s = tick[tick['is_first_10s']].groupby('n_min')
        first_10s_volume_mean = group_10s['volume'].sum()
        first_10s_ret = group_10s['LastPx'].last() - group_10s['LastPx'].first()
        first_10s_volume_mean.name = 'first_10_volume'
        first_10s_ret.name = 'first_10_ret'
        df_temp1 = pd.concat([first_10s_volume_mean,  first_10s_ret], axis = 1)
        
        tick['midprice'] = pd.concat([tick['Sell1Price'], tick['Buy1Price']], axis = 1).mean(axis = 1)
        tick['weighted_mid'] = ((tick['Sell1Price'] * tick['Sell1OrderQty']) + (tick['Buy1Price'] * tick['Buy1OrderQty'])) / rm_minimum(tick['Sell1OrderQty'] + tick['Buy1OrderQty'])
        
        tick['last_to_mid'] = (tick['LastPx'] - tick['midprice'])
        tick['last_to_weighted_mid'] = tick['LastPx'] - tick['weighted_mid']
        tick['last_to_mid'][tick['last_to_mid']>(tick['LastPx']*0.02)]= np.nan
        tick['last_to_weighted_mid'][tick['last_to_weighted_mid']>(tick['LastPx']*0.02)]= np.nan
        # 计算每个n分钟内的总成交量
        total_volume = tick.groupby('n_min')['volume'].sum()
        total_volume.name = 'total_volume'
        
        freq_to_min = get_freq_to_min(freq)
        # 计算每个n分钟内最后n/4时间内的成交量
        # 0.75分钟 = 45秒
        tick['is_last_n_4'] = (tick.index - tick['n_min']) >= pd.Timedelta(f'{freq_to_min * 3 / 4}min')
        # 确保每个n分钟的第一条记录不会被错误地算到前一个n分钟的最后n/4时间段内
        # tick['is_first_in_n_min'] = tick['n_min'] != tick['n_min'].shift(1)
        
        # 计算每个n分钟内最后n/4时间内的成交量
        group_temp = tick[tick['is_last_n_4']].groupby('n_min')
        last_n_4_volume =group_temp['volume'].sum()
        last_n_4_volume.name = 'last_n_4_volume'
        last_n_4_ret = group_temp['LastPx'].last() - group_temp['LastPx'].first()
        last_n_4_ret.name = 'last_n_4_ret'
        
        zbuy_n_4 = group_temp['zbuy'].sum()
        zsell_n_4 = group_temp['zsell'].sum()
        #trade_will.name = 'trade_will'
        zbuy_n_4.name = 'buy_active_n_4'
        zsell_n_4.name = 'sell_active_n_4'
        
        last_to_mid_n_4 = group_temp['last_to_mid'].mean()
        last_to_mid_n_4.name = 'last_to_mid_n_4'
        
        _zbuy_temp2 = tick[(tick['zbuy'] > big_t) & (tick['zbuy'] <= super_t) & (tick['is_last_n_4'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > big_t) & (tick['zsell'] <= super_t) & (tick['is_last_n_4'])].groupby('n_min')
        big_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        big_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        
        big_buy_count_n_4 = _zbuy_temp2['zbuy'].count()
        big_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        big_sell_n_4.name = 'sell_big_volume_n_4'
        big_sell_count_n_4.name = 'sell_big_count_n_4'
        
        big_buy_n_4.name = 'buy_big_volume_n_4'
        big_buy_count_n_4.name = 'buy_big_count_n_4'
        
        del _zbuy_temp2
        del _zsell_temp2
        _zbuy_temp2 = tick[(tick['zbuy'] > super_t) & (tick['zbuy'] <= gigantic_t) & (tick['is_last_n_4'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > super_t) & (tick['zsell'] <= gigantic_t) & (tick['is_last_n_4'])].groupby('n_min')
        
        super_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        super_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        super_buy_count_n_4 =  _zbuy_temp2['zbuy'].count()
        super_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        super_sell_n_4.name = 'sell_super_volume_n_4'
        super_sell_count_n_4.name = 'sell_super_count_n_4'
        
        super_buy_n_4.name = 'buy_super_volume_n_4'
        super_buy_count_n_4.name = 'buy_super_count_n_4'
        
        del _zbuy_temp2
        del _zsell_temp2
        
        _zbuy_temp2 = tick[(tick['zbuy'] > gigantic_t) & (tick['is_last_n_4'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > gigantic_t) & (tick['is_last_n_4'])].groupby('n_min')
        
        gigantic_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        gigantic_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        gigantic_buy_count_n_4 =  _zbuy_temp2['zbuy'].count()
        gigantic_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        gigantic_sell_n_4.name = 'sell_gigantic_volume_n_4'
        gigantic_sell_count_n_4.name = 'sell_gigantic_count_n_4'
        
        gigantic_buy_n_4.name = 'buy_gigantic_volume_n_4'
        gigantic_buy_count_n_4.name = 'buy_gigantic_count_n_4'
        
        del _zbuy_temp2
        del _zsell_temp2
        
        _zbuy_temp2 = tick[(tick['zbuy'] <= small_t) & (tick['is_last_n_4'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] <= small_t) & (tick['is_last_n_4'])].groupby('n_min')
        small_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        small_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        
        small_buy_count_n_4 = _zbuy_temp2['zbuy'].count()
        small_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        small_sell_n_4.name = 'sell_small_volume_n_4'
        small_sell_count_n_4.name = 'sell_small_count_n_4'
        
        small_buy_n_4.name = 'buy_small_volume_n_4'
        small_buy_count_n_4.name = 'buy_small_count_n_4'
        
        try:
            pvcorrdf_n_4 = tick[(tick['is_last_n_4'])][['n_min','LastPx','volume']].groupby('n_min').corr().xs('LastPx', level = 1)[['volume']]
            pvcorrdf_n_4.columns = ['PxVolCorr_n_4']
        except:
            pvcorrdf_n_4 = pd.DataFrame(columns = ['PxVolCorr_n_4'])
        
        df_temp1 = pd.concat([df_temp1, last_n_4_volume, last_n_4_ret], axis = 1)
        
        tick['is_last_n_20'] = (tick.index - tick['n_min']) >= pd.Timedelta(f'{freq_to_min * 19 / 20}min')
        # 确保每个n分钟的第一条记录不会被错误地算到前一个n分钟的最后n/4时间段内
        # tick['is_first_in_n_min'] = tick['n_min'] != tick['n_min'].shift(1)
        
        # 计算每个n分钟内最后n/4时间内的成交量
        group_temp10 = tick[(tick['is_last_n_20'])].groupby('n_min')
        last_n_20_volume = group_temp10['volume'].sum()
        last_n_20_ret = group_temp10['LastPx'].last() - group_temp10['LastPx'].first()
        
        last_n_20_volume.name = 'last_n_20_volume'
        last_n_20_ret.name = 'last_n_20_ret'
        
        df_temp1 = pd.concat([df_temp1, last_n_20_volume, last_n_20_ret], axis = 1)
        
        zbuy_n_20 = group_temp10['zbuy'].sum()
        zsell_n_20 = group_temp10['zsell'].sum()
        #trade_will.name = 'trade_will'
        zbuy_n_20.name = 'buy_active_n_20'
        zsell_n_20.name = 'sell_active_n_20'
        
        last_to_mid_n_20 = group_temp10['last_to_mid'].mean()
        last_to_mid_n_20.name = 'last_to_mid_n_20'
        
        _zbuy_temp2 = tick[(tick['zbuy'] > big_t) & (tick['zbuy'] <= super_t) & (tick['is_last_n_20'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > big_t) & (tick['zsell'] <= super_t) & (tick['is_last_n_20'])].groupby('n_min')
        big_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        big_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        big_buy_count_n_20 = _zbuy_temp2['zbuy'].count()
        big_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        big_sell_n_20.name = 'sell_big_volume_n_20'
        big_sell_count_n_20.name = 'sell_big_count_n_20'
        
        big_buy_n_20.name = 'buy_big_volume_n_20'
        big_buy_count_n_20.name = 'buy_big_count_n_20'
        
        del _zbuy_temp2
        del _zsell_temp2
        _zbuy_temp2 = tick[(tick['zbuy'] > super_t) & (tick['zbuy'] <= gigantic_t) & (tick['is_last_n_20'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > super_t) & (tick['zsell'] <= gigantic_t) & (tick['is_last_n_20'])].groupby('n_min')
        
        super_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        super_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        super_buy_count_n_20 =  _zbuy_temp2['zbuy'].count()
        super_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        super_sell_n_20.name = 'sell_super_volume_n_20'
        super_sell_count_n_20.name = 'sell_super_count_n_20'
        
        super_buy_n_20.name = 'buy_super_volume_n_20'
        super_buy_count_n_20.name = 'buy_super_count_n_20'
        
        del _zbuy_temp2
        del _zsell_temp2
        
        _zbuy_temp2 = tick[(tick['zbuy'] > gigantic_t) & (tick['is_last_n_20'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > gigantic_t) & (tick['is_last_n_20'])].groupby('n_min')
        
        gigantic_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        gigantic_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        gigantic_buy_count_n_20 =  _zbuy_temp2['zbuy'].count()
        gigantic_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        gigantic_sell_n_20.name = 'sell_gigantic_volume_n_20'
        gigantic_sell_count_n_20.name = 'sell_gigantic_count_n_20'
        
        gigantic_buy_n_20.name = 'buy_gigantic_volume_n_20'
        gigantic_buy_count_n_20.name = 'buy_gigantic_count_n_20'
        
        _zbuy_temp2 = tick[(tick['zbuy'] <= small_t) & (tick['is_last_n_20'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] <= small_t) & (tick['is_last_n_20'])].groupby('n_min')
        small_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        small_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        small_buy_count_n_20 = _zbuy_temp2['zbuy'].count()
        small_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        small_sell_n_20.name = 'sell_small_volume_n_20'
        small_sell_count_n_20.name = 'sell_small_count_n_20'
        
        small_buy_n_20.name = 'buy_small_volume_n_20'
        small_buy_count_n_20.name = 'buy_small_count_n_20'
        
        try:
            pvcorrdf_n_20 = tick[(tick['is_last_n_20'])][['n_min','LastPx','volume']].groupby('n_min').corr().xs('LastPx', level = 1)[['volume']]
            pvcorrdf_n_20.columns = ['PxVolCorr_n_20']
        except:
            pvcorrdf_n_20 = pd.DataFrame(columns = ['PxVolCorr_n_20'])
        
        grouped3 = tick.groupby('n_min')
        last_to_mid = grouped3['last_to_mid'].mean()
        last_to_weighted_mid = grouped3['last_to_weighted_mid'].mean()
        
        last_to_mid.name = 'last_to_mid'
        last_to_weighted_mid.name = 'last_to_weighted_mid'
        
        temp_idxmin = (grouped3['LastPx'].idxmin() - grouped3['LastPx'].first().index)#.to_frame()
        idmin = temp_idxmin.apply(lambda x: x.total_seconds())
        temp_idxmax = (grouped3['LastPx'].idxmax() - grouped3['LastPx'].first().index)#.to_frame()
        idmax = temp_idxmax.apply(lambda x: x.total_seconds())
        
        result_idmin = []
        result_idmax = []
        for group_time, group_data in grouped3:
            result_idmax.append([group_time, (((group_data.index >= grouped3['LastPx'].idxmax().loc[group_time]).astype(int)) * group_data['volume']).sum()])
            result_idmin.append([group_time, (((group_data.index >= grouped3['LastPx'].idxmin().loc[group_time]).astype(int)) * group_data['volume']).sum()])
        idmin_volume = pd.DataFrame(result_idmin).set_index(0).iloc[:, 0]
        idmin_volume.index.name = 'dt'
        
        idmax_volume = pd.DataFrame(result_idmax).set_index(0).iloc[:, 0]
        idmax_volume.index.name = 'dt'
        
        idmin.name = 'idmin'
        idmax.name = 'idmax'
        idmin_volume.name = 'volume_after_min'
        idmax_volume.name = 'volume_after_max'
        
        df_temp1 = pd.concat([df_temp1, zbuy, zsell, last_to_mid, last_to_weighted_mid, idmin, idmin_volume, idmax, idmax_volume, big_buy, big_sell, big_buy_count, big_sell_count, super_buy, super_sell, super_buy_count, super_sell_count, small_buy, small_sell, small_buy_count, small_sell_count], axis = 1)
        df_temp1 = pd.concat([df_temp1, gigantic_buy, gigantic_sell, gigantic_buy_count, gigantic_sell_count], axis = 1)
        df_temp1 = pd.concat([df_temp1, big_buy_n_4, big_sell_n_4, big_buy_count_n_4, big_sell_count_n_4, super_buy_n_4, super_sell_n_4, super_buy_count_n_4, super_sell_count_n_4, small_buy_n_4, small_sell_n_4, small_buy_count_n_4, small_sell_count_n_4, zbuy_n_4, zsell_n_4, last_to_mid_n_4, pvcorrdf_n_4], axis = 1)
        df_temp1 = pd.concat([df_temp1, gigantic_buy_n_4, gigantic_sell_n_4, gigantic_buy_count_n_4, gigantic_sell_count_n_4], axis = 1)
        df_temp1 = pd.concat([df_temp1, big_buy_n_20, big_sell_n_20, big_buy_count_n_20, big_sell_count_n_20, super_buy_n_20, super_sell_n_20, super_buy_count_n_20, super_sell_count_n_20, small_buy_n_20, small_sell_n_20, small_buy_count_n_20, small_sell_count_n_20, zbuy_n_20, zsell_n_20, last_to_mid_n_20, pvcorrdf_n_20], axis = 1)
        df_temp1 = pd.concat([df_temp1, gigantic_buy_n_20, gigantic_sell_n_20, gigantic_buy_count_n_20, gigantic_sell_count_n_20], axis = 1)
        aggdict = {'HTSCSecurityID':'last', 'volume':'sum','amount':'sum','pricediff':'sum','OBI':'mean','BidAskSpreadMean':'mean'}
        
        agg_dict_v3 = {'Buy1Price_mean':'mean','Buy1OrderQty_mean':'mean','Sell1Price_mean':'mean','Sell1OrderQty_mean':'mean','HTSCSecurityID':'last', 'OpenInterest':'last'}
        agg_dict_v4 = {'TradingDate':'last'}
        
        df1amt = tick.resample(freq).agg({**aggdict_ohlc, **aggdict, **agg_dict_v3, **agg_dict_v4})
        
        renamedict1 = {'pricediff':'AbsPxPath', 'OpenInterest':'oi', 'TradingDate':'tday'}
        df1amt = df1amt.rename(columns = {**renamedict1})
        
        tickdf = df1amt.join(pvcorrdf).join(df_temp1)
        
        
        tday = date
        tickdf = tickdf.dropna(subset = ['HTSCSecurityID'])
        morning_auction = tickdf.between_time('075800','090000')
        if len(morning_auction) > 0:
            morning_auction = morning_auction.loc[str(date)]
            morning_auction = morning_auction.groupby(morning_auction.index.date).agg(rule_dict)
            morning_auction.index = [pd.to_datetime(str(x) + ' 090000') for x in morning_auction.index]
            day_index = pd.date_range(f'{tday} 09:00:00',f'{tday} 11:29:59', freq=freq).to_list() + pd.date_range(f'{tday} 13:30:00',f'{tday} 14:59:59', freq=freq).to_list()
            if str.upper(freq) == '1H':
                day_index = pd.date_range(f'{tday} 09:00:00',f'{tday} 11:29:59', freq=freq).to_list() + pd.date_range(f'{tday} 14:00:00',f'{tday} 14:59:59', freq=freq).to_list()
            if tickdf.between_time('1016','1028')['volume'].sum() > 0:
                tickdf_daily = pd.concat([tickdf.between_time('090000','112959').iloc[1:],tickdf.between_time('133000','145959'),morning_auction])
            else:
                tickdf_daily = pd.concat([tickdf.between_time('090000','101459').iloc[1:],tickdf.between_time('103000','112959'),tickdf.between_time('133000','145959'),morning_auction])
                day_index = [timestamp for timestamp in day_index if not (pd.Timestamp(f'{tday} 10:15:00') <= timestamp <= pd.Timestamp(f'{tday} 10:29:59'))]
        else:
            day_index = pd.date_range(f'{tday} 09:00:00',f'{tday} 11:29:59', freq=freq).to_list() + pd.date_range(f'{tday} 13:30:00',f'{tday} 14:59:59', freq=freq).to_list()
            if str.upper(freq) == '1H':
                day_index = pd.date_range(f'{tday} 09:00:00',f'{tday} 11:29:59', freq=freq).to_list() + pd.date_range(f'{tday} 14:00:00',f'{tday} 14:59:59', freq=freq).to_list()
            if tickdf.between_time('1016','1028')['volume'].sum() > 0:
                tickdf_daily = pd.concat([tickdf.between_time('090000','112959'),tickdf.between_time('133000','145959')])
            else:
                tickdf_daily = pd.concat([tickdf.between_time('090000','101459'),tickdf.between_time('103000','112959'),tickdf.between_time('133000','145959')])
                day_index = [timestamp for timestamp in day_index if not (pd.Timestamp(f'{tday} 10:15:00') <= timestamp <= pd.Timestamp(f'{tday} 10:29:59'))]  

        night_end_time = None
        if tick.between_time('0202','0230').volume.sum() > 0:
            night_end_time = '022959'
            night_end_date = str(tick.between_time('0202','0230').index[-1].date()).replace('-', '')
        elif tick.between_time('0132','0159').volume.sum() > 0:
            night_end_time = '015959'
            night_end_date = str(tick.between_time('0132','0159').index[-1].date()).replace('-', '')
        elif tick.between_time('0102','0129').volume.sum() > 0:
            night_end_time = '012959'
            night_end_date = str(tick.between_time('0102','0129').index[-1].date()).replace('-', '')
        elif tick.between_time('0032','0059').volume.sum() > 0:
            night_end_time = '005959'
            night_end_date = str(tick.between_time('0032','0059').index[-1].date()).replace('-', '')
        elif tick.between_time('0002','0029').volume.sum() > 0:
            night_end_time = '002959'
            night_end_date = str(tick.between_time('0002','0029').index[-1].date()).replace('-', '')
        elif tick.between_time('2332','2359').volume.sum() > 0:
            night_end_time = '235959'
            night_end_date = str(tick.between_time('2332','2359').index[-1].date()).replace('-', '')
        elif tick.between_time('2302','2329').volume.sum() > 0:
            night_end_time = '232959'
            night_end_date = str(tick.between_time('2302','2329').index[-1].date()).replace('-', '')
        elif tick.between_time('2102','2259').volume.sum() > 0:
            night_end_time = '225959'
            night_end_date = str(tick.between_time('2102','2259').index[-1].date()).replace('-', '')
        
        if night_end_time is not None:
            night_auction = tickdf.between_time('195800','210000')
            if len(night_auction) > 0:
                night_start_date = str(night_auction.index[0].date()).replace('-', '')
                night_auction = night_auction.loc[night_start_date]
                night_index = pd.date_range(f'{night_start_date} 21:00:00',f'{night_end_date} {night_end_time}', freq=freq).to_list()
                day_index = night_index + day_index
                night_auction = night_auction.groupby(night_auction.index.date).agg(rule_dict)
                night_auction.index = [pd.to_datetime(str(x) + ' 210000') for x in night_auction.index]
                tickdf_daily = pd.concat([tickdf_daily,night_auction,tickdf.between_time('210000',night_end_time).iloc[1:]])
            else:
                if len(tickdf.between_time('195800','235900')) > 0:
                    night_start_date = str(tickdf.between_time('195800','235900').index[0].date()).replace('-', '')
                else:
                    night_start_date = udt.get_trading_day_offset(date, -1)[0].strftime('%Y%m%d')
                night_index = pd.date_range(f'{night_start_date} 21:00:00',f'{night_end_date} {night_end_time}', freq=freq).to_list()
                day_index = night_index + day_index
                tickdf_daily = pd.concat([tickdf_daily,tickdf.between_time('210000',night_end_time)])
               
        tickdf_daily = tickdf_daily.reindex(day_index)
        tickdf_daily.loc[tickdf_daily.amount < 0, 'amount'] = 0
        tickdf_daily.loc[tickdf_daily.volume < 0, 'volume'] = 0
        tickdf_daily['vwap'] = tickdf_daily['amount'] / tickdf_daily['volume'] / multiplier
        tickdf_daily.loc[abs(tickdf_daily['vwap'] / tickdf_daily['twap'] - 1) > 0.3,'vwap'] = tickdf_daily['twap']
        tickdf_daily['Ticker'] = ticker
        tickdf_daily = tickdf_daily.sort_index().replace([np.inf,-np.inf],np.nan)
        tickdf_daily[make0nan_columns] = tickdf_daily[make0nan_columns].replace([0],np.nan)
        tickdf_daily[ffill_columns] = tickdf_daily[ffill_columns].fillna(method = 'ffill')
        # tickdf_daily[ffill2_columns] = tickdf_daily[ffill2_columns].fillna(method = 'ffill')
        tickdf_daily['tday'] = int(date)
        tickdf_daily[fill0_columns] = tickdf_daily[fill0_columns].fillna(value = 0)
        tickdf_daily['Ticker'] = ticker
        tickdf_daily['HTSCSecurityID'] = tick['HTSCSecurityID'].dropna().iloc[0]
        # tickdf_daily[['HTSCSecurityID','Ticker']] = tickdf_daily[['HTSCSecurityID','Ticker']].fillna(method = 'bfill')
        tickdf_daily[ffill_px_columns] = tickdf_daily[ffill_px_columns].fillna(value = tick['PreClosePx'].dropna().iloc[0])
        tickdf_daily['oi'] = tickdf_daily['oi'].fillna(value = PreOpenInterest)
        tickdf_daily.index.name = 'dt'
        tickdf_daily.to_csv(os.path.join(csv_rootpath, f'{date}_{ticker}.csv'))
        return tickdf_daily
    except Exception as e:
        print(para, e)
        
#freq = '1min'
for freq in ['1min', '3min', '5min', '15min']:
    start_date, end_date = 20160101, 20250904

    #dailym = IO.read_data([start_date, end_date],columns = ['contract', 'volume'], alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY_NO_DAYS.h5')
    #dailys = IO.read_data([start_date, end_date],columns = ['contract', 'volume'], alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_SECONDMAIN_CHINA_COMMODITY_DAILY_NO_DAYS.h5')
    #daily = pd.concat([dailym, dailys]).sort_index()
    #daily = daily[daily['volume'] > 0].reset_index()
    #daily['dt'] = daily['dt'].apply(lambda x:x.strftime('%Y%m%d'))
    #paradf = daily[daily['Ticker'] == prod_id]
    #para_list = list(zip(paradf['dt'], paradf['contract']))

    daily = IO.read_data([start_date, end_date], columns = ['prod_id', 'volume', 'oi'], alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_CHINA_FUTURE_DAILY.h5')
    daily = daily[daily['prod_id'] == prod_id].reset_index()
    daily['dt'] = daily['dt'].apply(lambda x:x.strftime('%Y%m%d'))
    volume_select = daily.groupby(['dt']).apply(lambda x: x.sort_values('volume', ascending=False).head(4)).reset_index(drop=True)
    oi_select = daily.groupby(['dt']).apply(lambda x: x.sort_values('oi', ascending=False).head(4)).reset_index(drop=True)
    p1 = list(zip(volume_select['dt'], volume_select['Ticker']))
    p2 = list(zip(oi_select['dt'], oi_select['Ticker']))
    para_list = sorted(list(set(p1 + p2)))


    csv_rootpath = f'/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/{freq.upper()}/PER_TICKER/CSV/{prod_id}'
    os.makedirs(csv_rootpath, exist_ok = True)


    with Pool(24) as pool:
        rlist = pool.map(get_minute_data, para_list)
#df = pd.concat(rlist).set_index('Ticker', append = True).sort_index()

#os.makedirs(f'/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/{freq.upper()}/PER_TICKER/', exist_ok = True)
#IO.pd_hdf5_writer(df, f'/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/{freq.upper()}/PER_TICKER/{prod_id}.h5', dataset = prod_id, data_columns=['dt', 'Ticker'])