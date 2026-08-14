# 文档http://168.63.25.218:8080/sdk-help/xquant-api/textdata/Xnewsdata/#7110-get_datayes_news-ai
from xquant.textdata import NewsData
nd = NewsData()

df = nd.get_datayes_news('2025-05-06 00:00:00', '2025-05-06 13:00:00', 1)
print(df)

df = nd.get_datayes_news('2025-05-06', '2025-05-07', 1)
print(df)

df = nd.get_datayes_news('2025-05-06', '2025-05-07', 1, date_field='updatetime')
print(df)

df = nd.get_datayes_news('2025-05-06', '2025-05-07', 1, date_field='effectivetime')
print(df)

# from xquant.textdata import NewsData
# nd = NewsData()
# 文档 http://168.63.25.218:8080/sdk-help/xquant-api/textdata/Xnewsdata/#7111-get_datayes_company_score_news-
df = nd.get_datayes_company_score_news(start_date='2024-01-01', end_date='2024-01-02')
print(df)

df = nd.get_datayes_company_score_news(start_date='2025-05-06', end_date='2025-05-07',tradingcode=['000063'])
print(df)

df = nd.get_datayes_company_score_news(start_date='2025-05-06 00:00:00', end_date='2025-05-06 08:00:00',tradingcode=['000063'])
print(df)

df = nd.get_datayes_company_score_news(start_date='2025-05-06 00:00:00', end_date='2025-05-06 08:00:00',tradingcode=['000063'])
print(df)