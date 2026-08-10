sell_price = pd.read_pickle('/data/user/015626/data/share/LOCAL_DATA/arrow/sell_price/sell_price_20240207.pkl')

df = pd.read_pickle('/data/user/000072/share/for_wyc/arrow_sell/sell_price_20240411.pkl')
md = IO.read_data([20160104, 20240411], columns = ['adjfactor'])

df = df.join(md, how = 'left')

dfu = df.unstack()

df['vwapPM_nextday_adj'] = (dfu['vwapPM'].shift(-1) * dfu['adjfactor'].shift(-1) / dfu['adjfactor']).stack()
df['vwap_1300_1430_nextday_adj'] = (dfu['vwap_1300_1430'].shift(-1) * dfu['adjfactor'].shift(-1) / dfu['adjfactor']).stack()

temp = pd.concat([df['vwap_1300_1430_nextday_adj'].reindex(sell_price.index),sell_price['vwap_1300_1430_nextday_adj']], axis = 1).dropna()
temp.columns = ['new','old']

temp[abs(temp['new'] - temp['old']) > 0.00001]

df.to_pickle('/data/user/015626/data/share/LOCAL_DATA/arrow/sell_price/sell_price_20240411.pkl')