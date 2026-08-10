# 同花顺20220208及以前的数据时间戳打在左边，20220209及以后时间戳打在右边，在这里先处理左边的。
ths = pd.read_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/000832.CSI.csv', index_col=0, parse_dates=True)
ths.index.name = 'dt'
ths = ths.rename(columns = {'amt':'amount'})
ths = ths.loc[:'20220208']

temp = ths.between_time('1129','1130')

opendf = temp.groupby(temp.index.date)['open'].first()
close = temp.groupby(temp.index.date)['close'].last()
high = temp.groupby(temp.index.date)['high'].max()
low = temp.groupby(temp.index.date)['low'].min()
amount = temp.groupby(temp.index.date)['amount'].sum()
volume = temp.groupby(temp.index.date)['volume'].sum()
ths1129 = pd.concat([opendf,high,low,close,amount,volume], axis = 1)
ths1129.columns = ['open', 'high', 'low', 'close', 'amount', 'volume']

ths1129.index = [pd.to_datetime(str(x).replace('-','')+' 112900') for x in ths1129.index.tolist()]

ths1129.index.name = 'dt'

ths20220208 = ths.between_time('930','1128').append(ths.between_time('1300','1500')).append(ths1129).sort_index()

# 处理右边的
ths = pd.read_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/000832.CSI.csv', index_col=0, parse_dates=True)
ths.index.name = 'dt'
ths = ths.rename(columns = {'amt':'amount'})
ths = ths.loc['20220209':'20220526']

temp = ths.between_time('930','931')

opendf = temp.groupby(temp.index.date)['open'].first()
close = temp.groupby(temp.index.date)['close'].last()
high = temp.groupby(temp.index.date)['high'].max()
low = temp.groupby(temp.index.date)['low'].min()
amount = temp.groupby(temp.index.date)['amount'].sum()
volume = temp.groupby(temp.index.date)['volume'].sum()
ths0930 = pd.concat([opendf,high,low,close,amount,volume], axis = 1)
ths0930.columns = ['open', 'high', 'low', 'close', 'amount', 'volume']

ths0930.index = [pd.to_datetime(str(x).replace('-','')+' 093000') for x in ths0930.index.tolist()]

ths0930.index.name = 'dt'

ths1300 = ths.at_time(datetime.time(13,1)).reset_index()
ths1300['dt'] = ths1300.dt.map(lambda x: x.replace(minute=0))
ths1300 = ths1300.set_index('dt')

ths = ths.shift(-1)

ths = ths.between_time('931','1129').append(ths.between_time('1301','1459')).append(ths0930).append(ths1300).sort_index()



# 从wind数据修补几天
wind = pd.read_excel('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/000832.CSI_wind.xlsx', index_col=2, parse_dates=True)
wind = wind.drop(['代码','名称'], axis = 1)
wind.index.name = 'dt'
wind.columns = ['open', 'high', 'low', 'close', 'amount', 'volume']
wind['amount'] = wind['amount'] * 1e6

xiufu = wind.loc['20220510':'20220511'].append(wind.loc['20220523':'20220524'])
xiufu = xiufu.between_time('930','1129').append(xiufu.between_time('1300','1459')).sort_index()

ths = ths.append(xiufu).sort_index()


ths = ths.append(ths20220208).sort_index()
ths = ths.reset_index()
ths['Ticker'] = '000832.CSI'
ths = ths.set_index(['dt','Ticker']).sort_index()

IO.pd_hdf5_writer(ths,'/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/000832.CSI.h5',dataset='000832.CSI', override=True)