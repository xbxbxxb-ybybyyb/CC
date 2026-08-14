from xquant.textdata import NewsData
import pandas as pd
import datetime
nd = NewsData()

start_date = '20240101' # 20230605
end_date = '20250331'
date_list = [pd.Timestamp(start_date) + datetime.timedelta(days=i) for i in range((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1)]
date_list = [x.strftime('%Y-%m-%d') for x in date_list]


# res = pd.DataFrame()
# for tradingday in date_list:
#     df = nd.getAnnouncement(start_date=tradingday, end_date=tradingday)
#     res = res.append(df)

df = nd.getAnnouncement(start_date='20250420', end_date='20250428')
df['DATE'] = df['PUBDATE'].apply(lambda x : str(x).split(' ')[0])
res = df[df['TEXTTITLE'].str.contains('风险')].groupby('DATE').count()['STOCK']
res = res.reindex(date_list)
print(res.fillna(0).mean())
#
# stock_list = list(set(df['STOCK']))
# stock_list.sort()
# for i in stock_list:
#     print(i)
