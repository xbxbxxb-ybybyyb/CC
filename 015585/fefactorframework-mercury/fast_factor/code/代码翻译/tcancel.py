# 代码拆解 tcancel
x = '930_after_all_all_0_bigger_all_xyx1_nostd_med'
x = x.replace('price_v','pricev')
x = x.replace('corr_pv','corrpv')
res = []
x_list = x.split('_')
if x_list[0] == '930' and x_list[1] == 'after':
    y1 = \
'''
cancel_df = database['TCancelprice']
dt, ticker = cancel_df.index[0]
dt = dt.strftime('%Y%m%d')
zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
bj = ticker[-2:] == 'BJ'
cancel_df = filter_930(cancel_df)
'''
else:
    y1 = ''
    print('非枚举情况，单独处理')
res.append(y1)

if x_list[2] == 'all':
    y2 = ''
elif x_list[2] == 'buy':
    y2 = \
'''
cancel_df = cancel_df[cancel_df['OrderBSFlag'] == 1]
'''
elif x_list[2] == 'sell':
    y2 = \
'''
cancel_df = cancel_df[cancel_df['OrderBSFlag'] == 2]
'''
else:
    y2 = ''
    print('买卖标记枚举值异常，枚举值为{}'.format(x_list[2]))
res.append(y2)

if x_list[3] == 'all':
    y3 = ''
elif x_list[3] == 'big':
    y3 = \
'''
cancel_df['OrderAmt'] = (cancel_df['OrderQty'] * cancel_df['OrderPrice']).apply(lambda x : round_(x,5))
cancel_df = cancel_df[cancel_df['OrderAmt'] > 200000]
'''
elif x_list[3] == 'small':
    y3 = \
'''
cancel_df['OrderAmt'] = (cancel_df['OrderQty'] * cancel_df['OrderPrice']).apply(lambda x : round_(x,5))
cancel_df = cancel_df[cancel_df['OrderAmt'] < 50000]
'''
else:
    y3 = ''
    print('订单大小枚举值异常，枚举值为{}'.format(x_list[3]))
res.append(y3)

if x_list[4] == '0':
    y4 = ''
elif x_list[4] == 'zt':
    y4 = \
'''
if zcz:
    p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
elif bj:
    p_zt = np.floor(pre_close * 100 * 1.3 + 0.5) / 100
else:
    p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
cancel_df = cancel_df[cancel_df['OrderPrice'] {} p_zt]
'''.format('>=' if x_list[5] =='bigger' else '<')

elif x_list[4] == '9':
    y4 = \
'''
if zcz:
    p = round_(pre_close * (1 + 0.09 * 2),3)
elif bj:
    p = round_(pre_close * (1 + 0.09 * 3),3)
else:
    p = round_(pre_close * 1.09,3)
cancel_df = cancel_df[cancel_df['OrderPrice'] {} p]
'''.format('>' if x_list[5] =='bigger' else '<')

elif x_list[4] == '95':
    y4 = \
'''
if zcz:
    p = round_(pre_close * (1 + 0.095 * 2),3)
elif bj:
    p = round_(pre_close * (1 + 0.095 * 3),3)
else:
    p = round_(pre_close * 1.095,3)
cancel_df = cancel_df[cancel_df['OrderPrice'] {} p]
'''.format('>' if x_list[5] =='bigger' else '<')

elif x_list[4] == '98':
    y4 = \
'''
if zcz:
    p = round_(pre_close * (1 + 0.098 * 2),3)
elif bj:
    p = round_(pre_close * (1 + 0.098 * 3),3)
else:
    p = round_(pre_close * 1.098,3)
cancel_df = cancel_df[cancel_df['OrderPrice'] {} p]
'''.format('>' if x_list[5] =='bigger' else '<')

else:
    y4 = ''
    print('市场价格枚举值异常，枚举值为{}'.format(x_list[4]))
res.append(y4)

if x_list[6] == 'all':
    y5 = ''
elif x_list[6] == 'h500':
    y5 = \
'''
cancel_df = cancel_df.head(500) if len(cancel_df) > 500 else cancel_df
'''
elif x_list[6] == 't500':
    y5 = \
'''
cancel_df = cancel_df.tail(500) if len(cancel_df) > 500 else cancel_df
'''
elif x_list[6] == 't100':
    y5 = \
'''
cancel_df = cancel_df.tail(100) if len(cancel_df) > 100 else cancel_df
'''
elif x_list[6] == 'half1':
    y5 = \
'''
cancel_df = cancel_df.head(int(len(cancel_df) / 2)) if len(cancel_df)>10 else cancel_df
'''
elif x_list[6] == 'half2':
    y5 = \
'''
cancel_df = cancel_df.tail(int(len(cancel_df) / 2)) if len(cancel_df)>10 else cancel_df
'''
elif x_list[6] == 't1min':
    y5 = \
'''
cancel_df = cancel_df[cancel_df['MDTime_delta'] >= (cancel_df['MDTime_delta'].max() - 60*1000)]
'''
else:
    y5 = ''
res.append(y5)
# 属性
if x_list[7] == 'amt':
    y6 = \
'''
cancel_df['factor'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
'''
elif x_list[7] == 'length':
    y6 = \
'''
res = len(cancel_df)
'''
elif x_list[7] == 'corrpv':
    y6 = \
'''
res = pd.concat([cancel_df['OrderPrice'],cancel_df['OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
'''
elif x_list[7] == 'pricev':
    y6 = \
'''
pre_close = cancel_df['pre_close'].max()
p = (cancel_df['OrderPrice'] * cancel_df['OrderQty']).sum() / cancel_df['OrderQty'].sum() if cancel_df['OrderQty'].sum() > 10 else np.nan
res = p / pre_close - 1
if bj:
    res = res/3
elif zcz:
    res = res/2
'''

elif x_list[7] == 't':
    y6 = \
'''
cancel_df['factor'] = cancel_df['MDTime_delta']
'''

elif x_list[7] == 'index':
    y6 = \
'''
cancel_df['factor'] = cancel_df['OrderIndex']
'''

elif x_list[7] == 'buynumratio':
    y6 = \
'''
res = len(cancel_df[cancel_df['OrderBSFlag']==1]) / (len(cancel_df)+1)
'''

elif x_list[7] == 'buyamtratio':
    y6 = \
'''
cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
res = cancel_df[cancel_df['OrderBSFlag']==1]['OrderAmt'].sum() / (cancel_df['OrderAmt'].sum()+1)
'''

elif x_list[7] == 'bigratio':
    y6 = \
'''
cancel_df['OrderAmt'] = (cancel_df['OrderPrice'] * cancel_df['OrderQty']).apply(lambda x : round_(x,2))
res = cancel_df[cancel_df['OrderAmt'] >= 200000]['OrderAmt'].sum() / (cancel_df['OrderAmt'].sum() + 1)
'''

elif x_list[7] == 'price':
    y6 = \
'''
cancel_df['factor'] = cancel_df['OrderPrice']/cancel_df['pre_close']
'''

elif x_list[7] == 'price1':
    y6 = \
'''
cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
cancel_df['OrderAmtsum'] = cancel_df['OrderAmt'].cumsum()
cancel_df['OrderQtysum'] = cancel_df['OrderQty'].cumsum()
cancel_df['vwap'] = cancel_df['OrderAmtsum'] / cancel_df['OrderQtysum']
if zcz:
    cancel_df['factor'] = ((cancel_df['OrderPrice']-1)/2+1) / ((cancel_df['vwap']-1)/2+1)
elif bj:
    cancel_df['factor'] = ((cancel_df['OrderPrice'] - 1) / 3 + 1) / ((cancel_df['vwap'] - 1) / 3 + 1)
else:
    cancel_df['factor'] = cancel_df['OrderPrice'] / cancel_df['vwap']
'''

else:
    y6 = ''
    print('因子属性异常，因子属性为{}'.format(x_list[7]))
res.append(y6)

if x_list[8] == 'nostd':
    y7 = ''
elif x_list[8] == '2mv':
    y7 = \
'''
mv = re_close * ff_shares
if mv > 10:
    cancel_df['factor'] = cancel_df['factor'] / mv
else:
    cancel_df['factor'] = np.nan
'''

elif x_list[8] == '2ttl':
    y7 = \
'''
tran_ttl = (cancel_df_ori['OrderQty'] * cancel_df_ori['OrderPrice']).sum()
if tran_ttl > 0:
    cancel_df['factor'] = cancel_df['factor'] / tran_ttl
else:
    cancel_df['factor'] = np.nan
'''
res.append(y7)


if x_list[9] == 'cv':
    y8 = \
'''
res = cancel_df['factor'].std() / cancel_df['factor'].mean() if round_(abs(cancel_df['factor'].mean()),8) > 1e-4 else np.nan
'''
elif x_list[9] == 'cct':
    y8 = \
'''
res = (cancel_df['factor']**2).sum() / (cancel_df['factor'].sum())**2 if abs(cancel_df['factor'].sum()) > 1e-3 else np.nan
'''
elif x_list[9] == 'change':
    y8 = \
'''
res = cancel_df['factor'].head(1).mean() - cancel_df['factor'].tail(1).mean() if not cancel_df.empty else np.nan
'''
elif x_list[9] == 'tail':
    y8 = \
'''
res = cancel_df['factor'].tail(1).mean()
'''
elif x_list[9] == 'm2m':
    y8 = \
'''
res = cancel_df['factor'].max() / cancel_df['factor'].mean() if round_(cancel_df['factor'].mean(),5)>0 else np.nan
'''
elif x_list[9] == 'nocalc':
    y8 = ''
else:
    y8 = \
'''
res = cancel_df['factor'].{}()
'''.format(x_list[9])
res.append(y8)
for i in res:
    if len(i) > 0:
        print(i)