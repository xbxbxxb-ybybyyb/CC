import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

top_num=30
detail_num=5
start_date, end_date = 20220101, 20230331
start_date_, end_date_ =s.tradingday(start_date, -50)[0], s.tradingday(end_date, 30)[-1]

#读取数据
AShareStrangeTrade=s.get_factor_value('WIND_AShareStrangeTrade',S_STRANGE_ENDDATE=['>='+str(start_date)])
df=AShareStrangeTrade[['S_INFO_WINDCODE', 'S_STRANGE_BGDATE', 'S_STRANGE_ENDDATE',
       'S_STRANGE_RANGE', 'S_STRANGE_VOLUME', 'S_STRANGE_AMOUNT',
       'S_STRANGE_TRADERNAME', 'S_STRANGE_TRADERAMOUNT', 'S_STRANGE_BUYAMOUNT',
       'S_STRANGE_SELLAMOUNT']]
df.columns=['code','begin','end','pct','volume','amt','trader_name','trader_amt','trader_buyamt','trader_sellamt']
df['trader_buyamt']=df['trader_buyamt'].fillna(0)
df['trader_sellamt']=df['trader_sellamt'].fillna(0)
print('全部：',len(df))

#去除科创板、北交所
df=df[~df['code'].str.startswith('68').values]
df=df[~df['code'].str.endswith('.BJ').values]
print('去除科创板、北交所：',len(df))

#去除上市新股
def cal_after_not_ul(md_df):
    md_df=md_df.copy()
    ipo_data = IO.read_data([20000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
    ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
    ipo_data = ipo_data.reset_index()
    ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00'])]  # 筛选上交所和深交所股票，不包括科创板
    ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
    ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
    ipo_data['dt'] = ipo_data['list_date']
    ipo_data['is_list_date'] = True
    ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date']]

    md_df = md_df.join(ipo_data)
    md_df['after_list'] = md_df['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
    md_df.loc[md_df['amt'] == 0]['after_list'] = np.nan
    md_df['list_len'] = md_df['after_list'].unstack().rolling(10000, 1).sum().stack()
    md_df.loc[(md_df['list_len'].isnull() & (md_df['amt'] > 0)), 'list_len'] = 250
    md_df['list_len'] = md_df['list_len'].unstack().fillna(method='ffill').stack()
    md_df.loc[(md_df['list_len'] > 250), 'list_len'] = 250

    md_df['1_1_ul_price'] = (md_df['pre_close'] * 100 * 1.1 + 0.5).apply(np.floor) / 100  # 正常的涨停价
    md_df['1_44_ul_price'] = (md_df['pre_close'] * 100 * 1.44 + 0.5).apply(np.floor) / 100  # 首日的涨停价
    md_df['is_one_ul'] = np.nan
    md_df.loc[md_df['amt']>0, 'is_one_ul'] = 0 #有交易的变为0
    md_df.loc[(md_df['is_list_date'] & (md_df['close'] == md_df['1_44_ul_price'])), 'is_one_ul'] = 2 #第一天涨停变为2
    md_df.loc[(md_df['open'] == md_df['close']) & (md_df['high'] == md_df['low']) & (md_df['close'] == md_df['1_1_ul_price']), 'is_one_ul'] = 1  # 正常一字板变为1
    md_df['is_list_ul'] = (md_df['is_one_ul'].unstack().rolling(10000, 1).mean() > 1).stack()
    md_df['is_list_ul'] = md_df['is_list_ul'] == True
    md_df['first_not_ul'] = ((md_df['is_list_ul'].unstack().shift(1).stack()==True) & (md_df['is_list_ul']==False) |
                             (md_df['is_list_date'] & (md_df['is_list_ul']==False)))#前日是上市涨停，当日不涨停; 或者上市首日开板
    md_df.loc[md_df['first_not_ul']!=True, 'first_not_ul'] = np.nan

    md_df['after_first_not_ul'] = md_df['first_not_ul'].unstack().fillna(method='ffill').stack()  # 上市后的标记
    md_df.loc[md_df['amt'] == 0]['after_first_not_ul'] = np.nan
    md_df['after_not_ul_len'] = md_df['after_first_not_ul'].unstack().rolling(10000, 1).sum().stack()
    md_df.loc[(md_df['after_not_ul_len'].isnull() & (md_df['amt'] > 0) & (md_df['is_list_ul']==False)), 'after_not_ul_len'] = 200
    md_df['after_not_ul_len'] = md_df['after_not_ul_len'].unstack().fillna(method='ffill').stack()
    md_df.loc[(md_df['after_not_ul_len'] > 200), 'after_not_ul_len'] = 200
    return md_df['after_not_ul_len']
md = IO.read_data([start_date_, end_date_],
                  columns=['pre_close', 'open', 'close', 'high', 'low', 'adjfactor','pct_chg','amt'],
                  alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['after_not_ul_len'] = cal_after_not_ul(md)
df['dt']=pd.to_datetime(df['end'])
df['Ticker']=df['code']
df=df.set_index(['dt','Ticker'])
df['after_not_ul_len']=md['after_not_ul_len']
df=df[df['after_not_ul_len']>10]
df=df.reset_index().drop(columns=['dt','Ticker','after_not_ul_len'])
print('去除上市新股：',len(df))


#去除相同范围
begin_isna_list=list(df.loc[df['begin'].isna(),'end'].unique())
df=df[~((df['begin']==df['end'])&(df['end'].isin(begin_isna_list)))]
df['begin']=df['begin'].fillna(df['end'])
print('去除相同范围：',len(df))

#去除严重异常波动的投资者分类交易统计
dff=df.copy()
dff['trader_name']=dff['trader_name']+';'
tem=dff.groupby(['code','begin','end'])['trader_name'].sum()
tem_yzyc=tem[tem.str.contains('中小投资者;|其他自然人;|机构;|深股通投资者;')] #注意：主板也会有严重异常波动，后续需要检查！！！
df=df.set_index(['code','begin','end'])
df=df[~df.index.isin(list(tem_yzyc.index))].reset_index()
print('去除严重异常波动：',len(df))

#替换机构专用
df['trader_name']=df['trader_name'].replace(['机构专用1','机构专用2','机构专用3'],'机构专用')

#买方前五和卖方前五
df['buy_rank']=df.groupby(['code','begin','end'])['trader_buyamt'].rank(ascending=False)
df['sell_rank']=df.groupby(['code','begin','end'])['trader_sellamt'].rank(ascending=False)
df['buy5']=(df['buy_rank']<=5).astype(float)
df['sell5']=(df['sell_rank']<=5).astype(float)
df_buy=df[df['buy5']==1]
df_sell=df[df['sell5']==1]

df.to_pickle('/data/user/018107/factor_zooN/AShareStrangeTrade/strange_20220101_20230331.pkl')

#——————第零部分：每月统计——————
sample=pd.DataFrame()
sample['count']=df.groupby(['code','begin','end']).size()
sample=sample[sample['count']>=5]
sample['buy_amt']=df_buy.groupby(['code','begin','end'])['trader_buyamt'].sum()
sample['sell_amt']=df_sell.groupby(['code','begin','end'])['trader_sellamt'].sum()
sample['amt']=sample['buy_amt']+sample['sell_amt']

day_sample=sample.reset_index()
day_sample['month']=day_sample['end'].apply(lambda x:x[:6])
sta=pd.DataFrame()
sta['count']=day_sample.groupby('month').size()
sta['amt']=day_sample.groupby('month')['amt'].sum()/10000/10000#单位为亿元

#——————第一部分：股票信息——————
stock=pd.DataFrame()
stock['count']=sample.groupby(['code']).size()
stock['amt']=sample.groupby(['code'])['amt'].sum()/10000/10000#单位为亿元
stock=stock.sort_values('count',ascending=False).head(top_num)
name_data = IO.read_data([end_date, end_date], universe=list(stock.index.unique()), columns=['STOCK_NAME'],
                         alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
name_data = name_data.groupby(['dt', 'Ticker']).first()
stock['name']=name_data.reset_index().set_index('Ticker')['STOCK_NAME']

#股票的买入和卖出
stock_trader=pd.DataFrame()
stock_trader['buy_count']=df_buy.groupby(['code','trader_name']).size()
stock_trader['buy_amt']=df_buy.groupby(['code','trader_name'])['trader_buyamt'].sum()/10000/10000#单位为亿元
stock_trader['sell_count']=df_sell.groupby(['code','trader_name']).size()
stock_trader['sell_amt']=df_sell.groupby(['code','trader_name'])['trader_sellamt'].sum()/10000/10000#单位为亿元

stock_trader_buy=stock_trader.sort_values(['code','buy_amt'],ascending=False)
stock_trader_buy=stock_trader_buy.groupby('code').head(detail_num)
stock_trader_buy=stock_trader_buy.reset_index(level='trader_name')
stock_trader_buy['str']=stock_trader_buy['trader_name']+'('+stock_trader_buy['buy_count'].astype(str)+','+stock_trader_buy['buy_amt'].apply(lambda x:'%.2f'%x)+')'

stock_trader_sell=stock_trader.sort_values(['code','sell_amt'],ascending=False)
stock_trader_sell=stock_trader_sell.groupby('code').head(detail_num)
stock_trader_sell=stock_trader_sell.reset_index(level='trader_name')
stock_trader_sell['str']=stock_trader_sell['trader_name']+'('+stock_trader_sell['sell_count'].astype(str)+','+stock_trader_sell['sell_amt'].apply(lambda x:'%.2f'%x)+')'

stock['buy_detail']=stock_trader_buy.groupby('code')['str'].sum()
stock['sell_detail']=stock_trader_sell.groupby('code')['str'].sum()

#——————第二部分：营业部信息——————
trader_buy=pd.DataFrame()
trader_buy['count']=df_buy.groupby('trader_name').size()
trader_buy['buy_amt']= df_buy.groupby('trader_name')['trader_buyamt'].sum() / 10000 / 10000#单位为亿元
trader_buy=trader_buy.sort_values('buy_amt', ascending=False).head(top_num)

trader_stock_buy=stock_trader.sort_values(['trader_name','buy_amt'],ascending=False)
trader_stock_buy=trader_stock_buy.groupby('trader_name').head(detail_num)
trader_stock_buy=trader_stock_buy.reset_index(level='code')
trader_stock_buy['str']=trader_stock_buy['code']+'('+trader_stock_buy['buy_count'].astype(str)+','+trader_stock_buy['buy_amt'].apply(lambda x:'%.2f'%x)+')'

trader_sell=pd.DataFrame()
trader_sell['count']=df_sell.groupby('trader_name').size()
trader_sell['sell_amt']= df_sell.groupby('trader_name')['trader_sellamt'].sum() / 10000 / 10000#单位为亿元
trader_sell=trader_sell.sort_values('sell_amt', ascending=False).head(top_num)

trader_stock_sell=stock_trader.sort_values(['trader_name','sell_amt'],ascending=False)
trader_stock_sell=trader_stock_sell.groupby('trader_name').head(detail_num)
trader_stock_sell=trader_stock_sell.reset_index(level='code')
trader_stock_sell['str']=trader_stock_sell['code']+'('+trader_stock_sell['sell_count'].astype(str)+','+trader_stock_sell['sell_amt'].apply(lambda x:'%.2f'%x)+')'

trader_buy['buy_detail']=trader_stock_buy.groupby('trader_name')['str'].sum()
trader_sell['sell_detail']=trader_stock_sell.groupby('trader_name')['str'].sum()

file_name = '/data/user/018107/factor_zooN/sta/龙虎榜统计结果_v20230412.xlsx'
excel_writer = pd.ExcelWriter(file_name)
sta.to_excel(excel_writer, sheet_name='每月统计')
stock.to_excel(excel_writer, sheet_name='股票买入和卖出')
trader_buy.to_excel(excel_writer, sheet_name='营业部买入')
trader_sell.to_excel(excel_writer, sheet_name='营业部卖出')
excel_writer.save()