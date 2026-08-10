### 涨停

eod = IO.read_data([20210101,20240101], alt = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
eod['S_DQ_NEXT_PRECLOSE'] = eod['S_DQ_PRECLOSE'].unstack().shift(-1).stack()
eod['S_DQ_NEXT_OPEN'] = eod['S_DQ_OPEN'].unstack().shift(-1).stack()
df = univ.join(eod[['S_DQ_OPEN','S_DQ_HIGH','S_DQ_LOW','S_DQ_CLOSE','S_DQ_LIMIT','S_DQ_STOPPING','S_DQ_NEXT_PRECLOSE','S_DQ_NEXT_OPEN']], how = 'left')
df.columns = [str.lower(x.split('S_DQ_')[-1]) for x in df.columns]
df['high_to_limit'] = df['high'] == df['limit']
df['close_to_limit'] = df['close'] == df['limit']

_df = df[df.close_to_limit == True]

def get_result_from_para(para):
    date = para[0]
    ticker = para[1]
    next_date = udt.get_trading_day_offset(date, 1)[0].strftime('%Y%m%d')
    minute_df = pd.read_pickle(f'/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/UnAdjstedStockMinute_{ticker[:6]}.pkl', compression='gzip')
    minute_df = minute_df.loc[int(next_date)]

    result = minute_df.set_index('minute')[['close']].T.reset_index(drop = True)

    temp5 = minute_df[(minute_df['minute'] >= 930) & (minute_df['minute'] <= 934)]
    temp30 = minute_df[(minute_df['minute'] >= 930) & (minute_df['minute'] <= 959)]
    temp_noon30 = minute_df[(minute_df['minute'] >= 1330) & (minute_df['minute'] <= 1359)]

    result['vwap_pre5'] = temp5['amt'].sum() / temp5['volume'].sum()
    result['vwap_pre30'] = temp30['amt'].sum() / temp30['volume'].sum()
    result['twap30'] = temp_noon30['close'].mean()
    result['Ticker'] = ticker
    result['dt'] = pd.to_datetime(date)
    result.columns.name = ''
    result = result.set_index(['dt', 'Ticker'])
    return result

_univ = _df.reset_index()
dtlist = [x.strftime('%Y%m%d') for x in _univ.dt.tolist()]
tickerlist = _univ.Ticker.tolist()
paralist = [x for x in zip(dtlist,tickerlist)]

with Pool(24) as pool:
    dflist = pool.map(get_result_from_para, paralist)
rdf = pd.concat(dflist)

_df = _df.join(rdf, how = 'left')

_df['next_open_ratio'] = _df['next_open'] / _df['next_preclose'] - 1
_df['next_open1_ratio'] = _df[930] / _df['next_preclose'] - 1

_df2 = _df[_df['next_open1_ratio'] < -0.03]
print(_df2.shape)
(_df2['vwap_pre5'] / _df2['twap30'] - 1).cumsum().plot()