from xquant.thirdpartydata.factordata import FactorData
s = FactorData()
from xquant.textdata import NewsData
nd = NewsData()
df = s.get_factor_value("ODS_NEWS_HEARSAY_D",  pubdate=['>=20250414','<20250415'])
print(df.shape)
url_test = df['contenturl'].iloc[0].replace('https://kf077vr01.s3.cn-north-1.amazonaws.com.cn','http://168.7.16.200:28118/kf077vr01')
print(url_test)
data = nd.get_zxai_news_content(url=url_test)
print(data)