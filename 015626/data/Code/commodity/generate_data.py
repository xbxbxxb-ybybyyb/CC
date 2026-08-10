with open('/dfs/user/015626/JupyterNotebooks/utils/imports.txt', 'r') as file:
    code = file.read()
    exec(code)
plt.rcParams['figure.figsize'] = [20, 5]
# import mplfinance as mpf
# from xdb.stockdata import StockData
import json

multiplier_dict = pd.read_csv('/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/INFO/multiplier.csv', index_col=0).to_dict()['multiplier']
make0nan_columns = ['open','high','low','close','twap','vwap','BidP0','AskP0','Buy1Price_mean','Sell1Price_mean']
sum_list = ['buy_volume_vm', 'sell_volume_vm', 'buy_volume_mm', 'sell_volume_mm', 'buy_small_volume_vm', 'buy_mid_volume_vm', 'buy_big_volume_vm', 'buy_small_volume_mm', 'buy_mid_volume_mm', 'buy_big_volume_mm', 'sell_small_volume_vm', 'sell_mid_volume_vm', 'sell_big_volume_vm', 'sell_small_volume_mm', 'sell_mid_volume_mm', 'sell_big_volume_mm']
count_list = ['buy_count_vm','sell_count_vm','buy_count_mm','sell_count_mm','deal_0_count','deal_small_count','deal_mid_count','deal_big_count','buy_small_count_vm', 'buy_mid_count_vm', 'buy_big_count_vm', 'buy_small_count_mm', 'buy_mid_count_mm', 'buy_big_count_mm', 'sell_small_count_vm', 'sell_mid_count_vm', 'sell_big_count_vm', 'sell_small_count_mm', 'sell_mid_count_mm', 'sell_big_count_mm']         
ffill_columns = ['TradingDate','open','high','low','close','twap','vwap','BidP0','BidV0','AskP0','AskV0','Buy1Price_mean','Sell1Price_mean','HTSCSecurityID','Ticker']
ffill2_columns = ['position']
fill0_columns = ['PxStd', 'amount', 'OBI', 'Ask1AmtMean', 'Sell1OrderQty_mean', 'BidAskSpreadMean', 'Bid1AmtMean', 'PxVolCorr', 'volume', 'AbsPxPath', 'VolStd', 'Buy1OrderQty_mean']
fill0_columns += sum_list
fill0_columns += count_list

rule_dict = {x:'last'  for x in ['open', 'high', 'low', 'close', 'twap', 'HTSCSecurityID', 'Bid1AmtMean',
            'Ask1AmtMean', 'volume', 'amount', 'AbsPxPath', 'PxStd', 'VolStd',
            'OBI', 'BidAskSpreadMean', 'BidP0', 'BidV0', 'AskP0', 'AskV0',
            'Buy1Price_mean', 'Buy1OrderQty_mean', 'Sell1Price_mean',
            'Sell1OrderQty_mean', 'PxVolCorr','TradingDate','position']+sum_list+count_list}
rule_dict.update({'open':'first','high':'max','low':'min','volume':'sum','amount':'sum'})


def get_minute_data(path):
    try:
        tick = pd.read_csv(path,  parse_dates=['dt'], index_col=['dt'])
        tick['TradingDate'] = tick['TradingDate'].astype('str')
        ticker = path.split('/')[-2]
        tday = path.split('/')[-1].split('.')[0]
        tick['freq_index'] = [x.floor(freq) for x in tick.index]
        if str.upper(freq) == '1H':
            tick.loc[tick['freq_index'] == pd.to_datetime(tday + '130000'), 'freq_index'] = pd.to_datetime(tday + '110000')

        tick = tick[tick['TotalVolumeTrade'].diff() >= 0]

        tick['volume'] = tick['TotalVolumeTrade'].fillna(method = 'ffill').diff().fillna(tick['TotalVolumeTrade'])
        tick['amount'] = tick['TotalValueTrade'].fillna(method = 'ffill').diff().fillna(tick['TotalValueTrade'])
        if tick['volume'].between_time('2100','0229').sum() > 0:
            tick = pd.DataFrame(index = [tick.index[0].replace(hour = 19)]).append(tick)
        else:
            tick = pd.DataFrame(index = [tick.index[0].replace(hour = 7)]).append(tick)
        tick = tick.append(pd.DataFrame(index = [tick.index[-1].replace(hour = 16)]))
        tick.index.name = 'dt'
        tick = tick.sort_index().reset_index()

        if ticker.endswith('CZC'):
            tick['amount'] = tick['amount'] * multiplier_dict.get(ticker, 1)

        fill_na_columns = ['Buy1Price','Sell1Price','LastPx']
        tick[fill_na_columns] =  tick[fill_na_columns].replace(0,np.nan)

        tick['minute'] = tick.dt.map(lambda x: x.replace(second=0, microsecond = 0))
        tick = tick.set_index('dt')
        tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
        tick['pricediff'] = abs(tick.LastPx.diff())
        tick[['Buy1Price','Buy1OrderQty']] = tick[['Buy1Price','Buy1OrderQty']].astype('float64')
        tick['Bid1Amt'] = tick.Buy1Price * tick.Buy1OrderQty * multiplier_dict.get(ticker, 1)
        tick['Ask1Amt'] = tick.Sell1Price * tick.Sell1OrderQty * multiplier_dict.get(ticker, 1)
        tick['VolStd'] = tick['volume']
        tick['BidAskSpreadMean'] = tick['Sell1Price'] - tick['Buy1Price']
        tick['mid_price'] = tick[['Buy1Price', 'Sell1Price']].mean(axis = 1)
        tick['tick_vwap'] = (tick['amount'] / tick['volume'] / multiplier_dict.get(ticker, 1)).replace([np.inf, -np.inf, 0], np.nan)
        for x in ['buy_count_vm', 'sell_count_vm', 'buy_count_mm', 'sell_count_mm']:
            tick[x] = np.nan
        tick.loc[tick['tick_vwap'] > tick['mid_price'].shift(), 'buy_count_vm'] = 1
        tick.loc[tick['tick_vwap'] < tick['mid_price'].shift(), 'sell_count_vm'] = 1
        tick.loc[tick['mid_price'] > tick['mid_price'].shift(), 'buy_count_mm'] = 1
        tick.loc[tick['mid_price'] < tick['mid_price'].shift(), 'sell_count_mm'] = 1
        tick['buy_volume_vm'] = tick['volume'] * tick['buy_count_vm']
        tick['sell_volume_vm'] = tick['volume'] * tick['sell_count_vm']
        tick['buy_volume_mm'] = tick['volume'] * tick['buy_count_mm']
        tick['sell_volume_mm'] = tick['volume'] * tick['sell_count_mm']

        # 区分大小单
        ptdays = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(udt.get_trading_day_offset(tday, -5)[0], udt.get_trading_day_offset(tday, -1)[0])]
        ptick_list = []
        for p in ptdays:
            new_path = os.path.join(path.split(tday)[0], f'{p}.csv')
            if os.path.exists(new_path):
                ptick = pd.read_csv(new_path)['TotalVolumeTrade'].diff()
                ptick_list.append(ptick)
        if len(ptick_list) > 0:
            ptick = pd.concat(ptick_list)
        else:
            ptick = tick['TotalVolumeTrade'].diff()
        small_t = ptick[ptick>0].quantile(0.5)
        big_t = ptick[ptick>0].quantile(0.9)
        tick.loc[tick['volume'] == 0, 'deal_0_count'] = 1
        tick.loc[(tick['volume'] > 0) & (tick['volume'] <= small_t), 'deal_small_count'] = 1
        tick.loc[(tick['volume'] > small_t) & (tick['volume'] < big_t), 'deal_mid_count'] = 1
        tick.loc[tick['volume'] >= big_t, 'deal_big_count'] = 1

        for direction in ['buy', 'sell']:
            for pp in ['vm', 'mm']:
                for kind in ['small', 'mid', 'big']:
                    tick[f'{direction}_{kind}_volume_{pp}'] = tick[f'{direction}_volume_{pp}'] * tick[f'deal_{kind}_count']
                    tick[f'{direction}_{kind}_count_{pp}'] = tick[f'{direction}_count_{pp}'] * tick[f'deal_{kind}_count']


        agg_dict_sum = {x:'sum' for x in sum_list}
        agg_dict_count = {x:'count' for x in count_list}

        for x in ['open','high','low','close','twap']:
            tick[x] = tick['LastPx']
        for x in ['Buy1Price','Buy1OrderQty','Sell1Price','Sell1OrderQty']:
            tick['%s_mean' % x] = tick[x]

        aggdict_ohlc = {'open':'first','high':'max','low':'min','close':'last','twap':'mean','OpenInterest':'last'}

        pvcorrdf = tick.groupby('freq_index').apply(lambda x: x['LastPx'].corr(x['volume'])).dropna().to_frame(name = 'PxVolCorr')
        aggdict = {'HTSCSecurityID':'last','Bid1Amt':'mean','Ask1Amt':'mean','volume':'sum','amount':'sum','pricediff':'sum','LastPx':'std','VolStd':'std','OBI':'mean','BidAskSpreadMean':'mean'}

        aggdict2 = {'Buy1Price':'last','Buy1OrderQty':'last', 'Sell1Price':'last','Sell1OrderQty':'last','TradingDate':'last'}
        agg_dict_v3 = {'Buy1Price_mean':'mean','Buy1OrderQty_mean':'mean','Sell1Price_mean':'mean','Sell1OrderQty_mean':'mean','HTSCSecurityID':'last'}

        df1amt = tick.groupby('freq_index').agg({**aggdict_ohlc, **aggdict, **aggdict2, **agg_dict_v3, **agg_dict_sum, **agg_dict_count})

        renamedict1 = {'OpenInterest':'position','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd','Buy1Price':'BidP0','Buy1OrderQty':'BidV0', 'Sell1Price':'AskP0','Sell1OrderQty':'AskV0'}
        df1amt = df1amt.rename(columns = {**renamedict1})

        tickdf = df1amt.join(pvcorrdf)

        morning_auction = tickdf.between_time('075800','090000')
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
            night_start_date = str(night_auction.index[-1].date()).replace('-', '')
            night_index = pd.date_range(f'{night_start_date} 21:00:00',f'{night_end_date} {night_end_time}', freq=freq).to_list()
            day_index = night_index + day_index
            night_auction = night_auction.groupby(night_auction.index.date).agg(rule_dict)
            night_auction.index = [pd.to_datetime(str(x) + ' 210000') for x in night_auction.index]
            tickdf_daily = pd.concat([tickdf_daily,night_auction,tickdf.between_time('210000',night_end_time).iloc[1:]])

        tickdf_daily = tickdf_daily.reindex(day_index)
        tickdf_daily.loc[tickdf_daily.amount < 0, 'amount'] = 0
        tickdf_daily.loc[tickdf_daily.volume < 0, 'volume'] = 0
        tickdf_daily['vwap'] = tickdf_daily['amount'] / tickdf_daily['volume'] / multiplier_dict.get(ticker, 1)
        tickdf_daily.loc[abs(tickdf_daily['vwap'] / tickdf_daily['twap'] - 1) > 0.3,'vwap'] = tickdf_daily['twap']
        tickdf_daily['Ticker'] = ticker
        tickdf_daily = tickdf_daily.sort_index().replace([np.inf,-np.inf],np.nan)
        tickdf_daily[make0nan_columns] = tickdf_daily[make0nan_columns].replace([0],np.nan)
        tickdf_daily[ffill_columns] = tickdf_daily[ffill_columns].fillna(method = 'ffill')
        tickdf_daily[ffill2_columns] = tickdf_daily[ffill2_columns].fillna(method = 'ffill')
        tickdf_daily['TradingDate'] = tday
        tickdf_daily[fill0_columns] = tickdf_daily[fill0_columns].fillna(value = 0)
        tickdf_daily[['BidV0','AskV0']] = tickdf_daily[['BidV0','AskV0']].fillna(value = 0)
        tickdf_daily['Ticker'] = ticker
        tickdf_daily['HTSCSecurityID'] = tick['HTSCSecurityID'].dropna().iloc[0]
        # tickdf_daily[['HTSCSecurityID','Ticker']] = tickdf_daily[['HTSCSecurityID','Ticker']].fillna(method = 'bfill')
        tickdf_daily[ffill_columns] = tickdf_daily[ffill_columns].fillna(value = tick['PreClosePx'].dropna().iloc[0])
        tickdf_daily.index.name = 'dt'
        return tickdf_daily.reset_index().set_index(['dt','Ticker'])
    except Exception as e:
        print(path, e)

#for freq in ['1h','30min', '15min', '5min', '1min', '30s', '15s']:
for freq in ['1min']:
    _,_,cdate_list = check_update_date(20240130, 20250402)
    pkl_sdate = 20230101
    pkl_edate = 20241231
    
    freq = str.upper(freq)

    save_rootpath = f'/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/{freq}/'
    pkl_save_path = os.path.join(save_rootpath, f'{pkl_sdate}_{pkl_edate}')
    simple_pkl_save_path = os.path.join(save_rootpath, f'{pkl_sdate}_{pkl_edate}_simple')
    os.makedirs(os.path.join(save_rootpath, 'H5'), exist_ok=True)
    os.makedirs(pkl_save_path, exist_ok=True)
    os.makedirs(simple_pkl_save_path, exist_ok=True)

    path_list = []
    for date in cdate_list:
        path_list += glob.glob(f'/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/TICK/MAIN/*/{date}.csv')
    with Pool(24) as pool:
        rlist = pool.map(get_minute_data, path_list)
    df_main = pd.concat(rlist).sort_index()
    
    df_main['flag'] = df_main[['open','high','low','close','twap','vwap','BidP0','AskP0','Buy1Price_mean','Sell1Price_mean']].min(axis = 1)
    df_main = df_main[df_main.flag != 0].drop(['flag'], axis = 1)
    df_main = df_main.reset_index().drop_duplicates(subset = ['dt','Ticker'], keep = 'first').set_index(['dt','Ticker'])
    df_main_h5_path = os.path.join(save_rootpath, f'H5/MAIN_CHINA_COMMODITY_{freq}.h5')
    if os.path.exists(df_main_h5_path):
        IO.pd_hdf5_writer(df_main, df_main_h5_path, dataset=f'MAIN_CHINA_COMMODITY_{freq}', data_columns=['dt','Ticker'], append = True)
    else:
        IO.pd_hdf5_writer(df_main, df_main_h5_path, dataset=f'MAIN_CHINA_COMMODITY_{freq}', data_columns=['dt','Ticker'])
#    del(df_main)

    path_list = []
    for date in cdate_list:
        path_list += glob.glob(f'/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/TICK/SECONDMAIN/*/{date}.csv')
    with Pool(24) as pool:
        rlist = pool.map(get_minute_data, path_list)
    df_secondmain = pd.concat(rlist).sort_index()

    df_secondmain['flag'] = df_secondmain[['open','high','low','close','twap','vwap','BidP0','AskP0','Buy1Price_mean','Sell1Price_mean']].min(axis = 1)
    df_secondmain = df_secondmain[df_secondmain.flag != 0]
    df_secondmain = df_secondmain.reset_index().drop_duplicates(subset = ['dt','Ticker'], keep = 'first').set_index(['dt','Ticker'])
    df_secondmain_h5_path = os.path.join(save_rootpath, f'H5/SECONDMAIN_CHINA_COMMODITY_{freq}.h5')
    if os.path.exists(df_secondmain_h5_path):
        IO.pd_hdf5_writer(df_secondmain, df_secondmain_h5_path, dataset=f'SECONDMAIN_CHINA_COMMODITY_{freq}', data_columns=['dt','Ticker'], append = True)
    else:
        IO.pd_hdf5_writer(df_secondmain, df_secondmain_h5_path, dataset=f'SECONDMAIN_CHINA_COMMODITY_{freq}', data_columns=['dt','Ticker'])

#    df_main = pd.read_hdf(df_main_h5_path)

    df_main['contract_kind'] = 'main'
    df_secondmain['contract_kind'] = 'second_main'

    df_secondmain = df_secondmain.reindex(df_main.index & df_secondmain.index)

    df_all = df_main.reset_index().append(df_secondmain.reset_index()).rename(columns = {'Ticker':'prod_id','HTSCSecurityID':'Ticker'}).set_index(['dt','Ticker']).sort_index()
    
    del(df_main)
    del(df_secondmain)
    
    df_all_h5_path = os.path.join(save_rootpath, f'H5/MD_CHINA_COMMODITY_{freq}.h5')
    if os.path.exists(df_all_h5_path):
        IO.pd_hdf5_writer(df_all, df_all_h5_path, dataset=f'MD_CHINA_COMMODITY_{freq}', data_columns=['dt','Ticker'], append = True)
    else:
        IO.pd_hdf5_writer(df_all, df_all_h5_path, dataset=f'MD_CHINA_COMMODITY_{freq}', data_columns=['dt','Ticker'])
    
 
    df_all = IO.read_data([pkl_sdate, pkl_edate],alt= df_all_h5_path)

    prod_id_list = df_all.prod_id.unique().tolist()

    def handel_prod_id(prod_id):
#        if os.path.exists(os.path.join(save_rootpath, f'INSAMPLE/{prod_id}.pkl')):
#            return
        print(prod_id)

        df_prod = df_all[df_all.prod_id == prod_id].drop(['prod_id', 'flag'], axis = 1).unstack()

        df_prod_dict = {}
        for x in df_prod.columns.get_level_values(0).unique():
            if x == 'contract_kind':
                df_prod_dict['main_mask'] = df_prod['contract_kind'] == 'main'
                df_prod_dict['second_main_mask'] = df_prod['contract_kind'] == 'second_main'
            else:
                df_prod_dict[x] = df_prod[x]

        import pickle
        def save_pickle(save_dict,save_path):
            with open(save_path, 'wb') as input:
                pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
            return 
            
        vm_list = ['buy_big_count', 'buy_big_volume', 'buy_count', 'buy_mid_count', 'buy_mid_volume', 'buy_small_count', 'buy_small_volume', 'buy_volume', 'sell_big_count', 'sell_big_volume', 'sell_count', 'sell_mid_count', 'sell_mid_volume', 'sell_small_count', 'sell_small_volume', 'sell_volume']
        normal_list = ['AbsPxPath', 'Ask1AmtMean', 'AskP0', 'AskV0', 'Bid1AmtMean', 'BidAskSpreadMean', 'BidP0', 'BidV0', 'Buy1OrderQty_mean', 'Buy1Price_mean', 'OBI', 'PxStd', 'PxVolCorr', 'Sell1OrderQty_mean', 'Sell1Price_mean', 'TradingDate', 'VolStd', 'amount', 'close', 'main_mask', 'second_main_mask', 'deal_0_count', 'deal_big_count', 'deal_mid_count', 'deal_small_count', 'high', 'low', 'open', 'position', 'twap', 'volume', 'vwap']
        simple_list = ['high', 'low', 'open', 'position', 'twap', 'volume', 'vwap', 'amount', 'close', 'main_mask','second_main_mask']

        new_df = {}
        simple_df = {}
        
        for k in vm_list:
            newk = k + '_mm' if '.CZC' in prod_id else k + '_vm'
            new_df[k] = df_prod_dict[newk]
        for k in normal_list:
            new_df[k] = df_prod_dict[k]
        for k in simple_list:
            simple_df[k] = df_prod_dict[k]
        assert len(new_df.keys()) == 48

        save_pickle(new_df, os.path.join(pkl_save_path, f'{prod_id}.pkl'))
        save_pickle(simple_df, os.path.join(simple_pkl_save_path, f'{prod_id}.pkl'))


    with Pool(2) as pool:
        pool.map(handel_prod_id, prod_id_list)
    send_link(f'{freq}_1')

'''
import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
    
last_dict = {'5MIN':['1MIN', '30S']}
path_mapping = {'5MIN':'MINUTE_5', '1MIN':'1MIN', '30S':'30S'}
suffix_mapping = {'5MIN':'_last_5min', '1MIN':'_last_1min', '30S':'_last_30s'}
root_path = '/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/'


for k in last_dict:
    base_path = os.path.join(root_path, path_mapping[k], 'INSAMPLE')
    kind_list = [x[:-4] for x in os.listdir(base_path) if 'last' not in x]

    def get_kind(kind):
        
        try:
            if os.path.exists(os.path.join(base_path, f'{kind}_last_1min.pkl')) and os.path.exists(os.path.join(base_path, f'{kind}_last_30s.pkl')):
                return
            
            print(kind, '!!!')
            kdf = pd.read_pickle(os.path.join(base_path, f'{kind}.pkl'))
            sindex = kdf['close'].index
            for v in last_dict[k]:
                if os.path.exists(os.path.join(base_path, f'{kind}{suffix_mapping[v]}.pkl')):
                    continue
                v_base_path = os.path.join(root_path, path_mapping[v], 'INSAMPLE')
                vdf = pd.read_pickle(os.path.join(v_base_path, f'{kind}.pkl'))
                shift_num = int(1 - pd.to_timedelta(k) / pd.to_timedelta(v))
                print(k, v, kind, shift_num)
                new_dict = {}
                for col in vdf.keys():
                    new_dict[f'{col}{suffix_mapping[v]}'] = vdf[col].shift(shift_num).reindex(sindex)
                save_pickle(new_dict, os.path.join(base_path, f'{kind}{suffix_mapping[v]}.pkl'))
        except Exception as e:
            print(k, v, kind, shift_num, e)
            send_link('wrong')

    with Pool(1) as pool:
        pool.map(get_kind, kind_list)
'''

'''
如下是去除mm vm后缀的字段
import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

vm_list = ['buy_big_count', 'buy_big_volume', 'buy_count', 'buy_mid_count', 'buy_mid_volume', 'buy_small_count', 'buy_small_volume', 'buy_volume', 'sell_big_count', 'sell_big_volume', 'sell_count', 'sell_mid_count', 'sell_mid_volume', 'sell_small_count', 'sell_small_volume', 'sell_volume']
normal_list = ['AbsPxPath', 'Ask1AmtMean', 'AskP0', 'AskV0', 'Bid1AmtMean', 'BidAskSpreadMean', 'BidP0', 'BidV0', 'Buy1OrderQty_mean', 'Buy1Price_mean', 'OBI', 'PxStd', 'PxVolCorr', 'Sell1OrderQty_mean', 'Sell1Price_mean', 'TradingDate', 'VolStd', 'amount', 'close', 'main_mask', 'second_main_mask', 'deal_0_count', 'deal_big_count', 'deal_mid_count', 'deal_small_count', 'high', 'low', 'open', 'position', 'twap', 'volume', 'vwap']
simple_list = ['high', 'low', 'open', 'position', 'twap', 'volume', 'vwap', 'amount', 'close', 'main_mask','second_main_mask']
# for k in df.keys():
#     if k.endswith('_vm'):
#         vm_list.append(k[:-3])
#     if not k.endswith('_vm') and not k.endswith('_mm'):
#         normal_list.append(k)
new_df = {}
simple_df = {}
for freq in ['1MIN', '5MIN', '15MIN', '30MIN', '30S']:
    root_path = f'/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/{freq}/INSAMPLE_old/'
    save_path = f'/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/{freq}/INSAMPLE/'
    save_simple_path = f'/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/{freq}/INSAMPLE_simple/'
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(save_simple_path, exist_ok=True)
    for ticker in os.listdir(root_path):
        if 'last' in ticker:
            continue
        print(freq, ticker)
        df = pd.read_pickle(f'{root_path}{ticker}')
        for k in vm_list:
            newk = k + '_mm' if '.CZC' in ticker else k + '_vm'
#             print(k, newk)
            new_df[k] = df[newk]
        for k in normal_list:
            new_df[k] = df[k]
        for k in simple_list:
            simple_df[k] = df[k]
        assert len(new_df.keys()) == 48
        save_pickle(new_df, f'{save_path}{ticker}')
        save_pickle(simple_df, f'{save_simple_path}{ticker}')
 '''