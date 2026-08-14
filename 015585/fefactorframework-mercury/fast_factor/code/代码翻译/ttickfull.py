# 代码拆解 tickfull
x = '930_after_all_all_0_bigger_all_all_upsell10_all_ordervol2svol_nostd_sum'
res = []
x_list = x.split('_')
if x_list[0] == '930' and x_list[1] == 'after':
    y1 = \
'''
tick_df = database['TTickfulladdorder']
dt, ticker = tick_df.index[0]
dt = dt.strftime('%Y%m%d')
zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
tick_df = filter_930(tick_df)
'''
elif x_list[0] == 'tfzt' and x_list[1] == 'after':
    y1 = \
'''
tick_df = database['TTickfulladdorder']
dt, ticker = tick_df.index[0]
dt = dt.strftime('%Y%m%d')
zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
tick_df = filter_930(tick_df)

'''
else:
    y1 = ''
    print('非枚举情况，单独处理')
res.append(y1)

if x_list[2] == 'all':
    y2 = ''
elif x_list[2] == 'amt25':
    y2 = \
'''
tick_df = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),5)]
'''
elif x_list[2] == 'amt75':
    y2 = \
'''
tick_df = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.75),5)]
'''
else:
    y2 = ''
    print('成交活跃枚举值异常，枚举值为{}'.format(x_list[2]))
res.append(y2)

if x_list[3] == 'all':
    y3 = ''
elif x_list[3] == 'up':
    y3 = \
'''
tick_df['tradep'] = tick_df['ValueTrade'] / (tick_df['VolumeTrade']+1e-2)
tick_df = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
'''
elif x_list[3] =='down':
    y3 = \
'''
tick_df['tradep'] = tick_df['ValueTrade'] / (tick_df['VolumeTrade']+1e-2)
tick_df = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
'''
elif x_list[3] == 'up100':
    y3 = \
'''
tick_df['LastPx_100'] = tick_df['LastPx'].rolling(100,1).mean()
tick_df = tick_df[tick_df['LastPx'] > tick_df['LastPx_100']]
'''
elif x_list[3] == 'down100':
    y3 = \
'''
tick_df['LastPx_100'] = tick_df['LastPx'].rolling(100,1).mean()
tick_df = tick_df[tick_df['LastPx'] < tick_df['LastPx_100']]
'''
else:
    y3 = ''
    print('上涨下跌枚举值异常，枚举值为{}'.format(x_list[3]))
res.append(y3)

if x_list[4] == '0':
    y4 = ''
elif x_list[4] == 'p25':
    y4 = \
'''
tick_df = tick_df[tick_df['LastPx'] {} round_(tick_df['LastPx'].quantile(0.25),5)]
'''.format('>' if x_list[5] =='bigger' else '<')
elif x_list[4] == 'p75':
    y4 = \
'''
tick_df = tick_df[tick_df['LastPx'] {} round_(tick_df['LastPx'].quantile(0.75),5)]
'''.format('>' if x_list[5] =='bigger' else '<')
else:
    y4 = ''
    print('市场价格枚举值异常，枚举值为{}'.format(x_list[4]))
res.append(y4)

if x_list[6] == 'all':
    y5 = ''
else:
    y5 = \
'''
tick_df = tick_df[tick_df['OrderType'] == '{}']
'''.format(x_list[6])
res.append(y5)

if x_list[7] == 'all':
    y6 = ''
elif x_list[7] == 'big':
    y6 = \
'''
tick_df = tick_df[(tick_df['OrderQty']*tick_df['OrderPrice'])>=200000]
'''
elif x_list[7] == 'mid':
    y6 = \
'''
tick_df = tick_df[((tick_df['OrderQty']*tick_df['OrderPrice'])<200000) & ((tick_df['OrderQty']*tick_df['OrderPrice'])>=50000)]
'''
elif x_list[7] == 'small':
    y6 = \
'''
tick_df = tick_df[(tick_df['OrderQty']*tick_df['OrderPrice'])<50000]
'''
else:
    y6 = ''
    print('订单大小枚举异常，枚举值为{}'.format(x_list[7]))
res.append(y6)

if x_list[8] == 'all':
    y7 = ''
elif x_list[8] == 'upsell10':
    y7 = \
'''
tick_df = tick_df[tick_df['Sell10Price'] > 0]
tick_df = tick_df[tick_df['OrderPrice'] >= tick_df['Sell10Price']]
'''
elif x_list[8] == 'downbuy10':
    y7 = \
'''
tick_df = tick_df[tick_df['Buy10Price'] > 0]
tick_df = tick_df[tick_df['OrderPrice'] <= tick_df['Buy10Price']]
'''
elif x_list[8] == 'up9':
    y7 = \
'''
if not zcz:
    tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.09).apply(lambda x : round_(x,2))]
else:
    tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.18).apply(lambda x : round_(x,2))]
'''
elif x_list[8] == 'up101':
    y7 = \
'''
tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['LastPx'] * 1.01).apply(lambda x :round_(x,5))]
'''
elif x_list[8] == 'down99':
    y7 = \
'''
tick_df = tick_df[tick_df['OrderPrice'] <= (tick_df['LastPx'] * 0.99).apply(lambda x :round_(x,5))]
'''
else:
    y7 = ''
    print('订单价格枚举值异常，枚举值为{}'.format(x_list[8]))
res.append(y7)

if x_list[9] == 'all':
    y8 = ''
elif x_list[9] == 'h500':
    y8 = \
'''
tick_df = tick_df.head(20) if len(tick_df) > 20 else tick_df
'''
elif x_list[9] == 't500':
    y8 = \
'''
tick_df = tick_df.tail(20) if len(tick_df) > 20 else tick_df
'''
elif x_list[9] == 't100':
    y8 = \
'''
tick_df = tick_df.tail(100) if len(tick_df) > 100 else tick_df
'''
elif x_list[9] == 't1min':
    y8 = \
'''
tick_df['MDTime_delta'] = tick_df['MDTime'].apply(lambda x: inttime2deltamls(x))
tick_df = tick_df[tick_df['MDTime_delta'] >= (tick_df['MDTime_delta'].max() - 60*1000)]
'''
elif x_list[9] == 'half2':
    y8 = \
'''
tick_df = tick_df.tail(int(len(tick_df) / 2)) if len(tick_df)>10 else tick_df
'''
else:
    y8 = ''
res.append(y8)

if x_list[10] == 'orderp2bp':
    y9 = \
'''
tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0.5]
tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['WeightedAvgBidPx']) / tick_df['pre_close']
'''
elif x_list[10] == 'orderp2sp':
    y9 = \
'''
tick_df = tick_df[tick_df['WeightedAvgOfferPx'] > 0.5]
tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['WeightedAvgOfferPx']) / tick_df['pre_close']
'''
elif x_list[10] == 'orderp2lp':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['LastPx']) / tick_df['pre_close']
'''
elif x_list[10] == 'orderp2bp10':
    y9 = \
'''
tick_df = tick_df[tick_df['Buy10Price'] > 0]
tick_df['factor'] = np.sign(tick_df['OrderPrice'] - tick_df['Buy10Price'])
'''
elif x_list[10] == 'ordervol2bvol':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderQty'] / tick_df['TotalBidQty'])
'''
elif x_list[10] == 'ordervol2svol':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderQty'] / tick_df['TotalOfferQty'])
'''
elif x_list[10] == 'orderamt2bamt':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'])
'''
elif x_list[10] == 'orderamt2samt':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx'])
'''
elif x_list[10] == 'orderamt2bsamt':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
                                                                     + tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'])
'''
elif x_list[10] == 'orderamt2trade':
    y9 = \
'''
tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / tick_df['ValueTrade'].sum()
'''
elif x_list[10] == 'orderp2tradep':
    y9 = \
'''
tick_df = tick_df[tick_df['ValueTrade'] > 1]
tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['ValueTrade'] / tick_df['VolumeTrade']) / tick_df['pre_close']
'''
else:
    y9 = ''
    print('因子属性异常，因子属性为{}'.format(x_list[10]))
res.append(y9)

if x_list[12] == 'cv':
    y10 = \
'''
res = tick_df['factor'].std() / tick_df['factor'].mean() if round_(abs(tick_df['factor'].mean()),8) > 1e-4 else np.nan
'''
elif x_list[12] == 'cct':
    y10 = \
'''
res = (tick_df['factor']**2).sum() / (tick_df['factor'].sum())**2 if abs(tick_df['factor'].sum()) > 1e-3 else np.nan
'''
elif x_list[12] == 'change':
    y10 = \
'''
res = tick_df['factor'].head(1).mean() - tick_df['factor'].tail(1).mean() if not tick_df.empty else np.nan
'''
elif x_list[12] == 'tail':
    y10 = \
'''
res = tick_df['factor'].tail(1).mean()
'''
elif x_list[12] == 'm2m':
    y10 = \
'''
res = tick_df['factor'].max() / tick_df['factor'].mean() if round_(tick_df['factor'].mean(),5)>0 else np.nan
'''
else:
    y10 = \
'''
res = tick_df['factor'].{}()
'''.format(x_list[12])
res.append(y10)
for i in res:
    if len(i) > 0:
        print(i)