import pandas as pd
import numpy as np
import IO
import os
from xquant.textdata import ResearchReport
from joblib import Parallel, delayed
import datetime

rr = ResearchReport()
def get_tradingcode_list(x):
    tradingcode_list = []
    for i in x:
        if 'tradingCode' in i:
            tradingcode_list.append(i['tradingCode'])
    return tradingcode_list
def get_rr_by_date(date1, date2, page_size=1000):
    df_total = rr.get_vsat_data(pubDateStart = date1,pubDateEnd = date2)
    totalCount = df_total.iloc[0]["totalCount"]
    if totalCount > 10000:
        print(f'超过1万条!!!!!!：start={date1},end={date2},num={totalCount}')
        error_date.append((date1,date2))
    page_nums = int(totalCount / 1000) + 1
    res = pd.DataFrame()
    for i in range(1,page_nums+1):
        df = rr.get_vsat_data(page_num = i, page_size = page_size, pubDateStart = date1,pubDateEnd = date2)
        res = res.append(df)
    # tradingcode_list
    res['tradingcode_list'] = res['company'].apply(lambda x : get_tradingcode_list(x))

    print(f'{date1},{date2},shape={res.shape}')
    return res

start_date = '20150930'
end_date = '20241231'
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
date_list = [i.strftime('%Y%m%d') for i in date_list]

root_path = '/dfs/group/800463/data/research_report_data/rr_basicinfo/'
error_date = []

print(f'start_date={start_date},end_date={end_date}')
# 下载基本信息
for date in date_list:
    res = get_rr_by_date(date,date)
    res.to_pickle(f'{root_path}{date}.pkl')
# 解析pdf

annex_lst = df["annex"].tolist()
for annex in annex_lst[:2]:
    for i in annex:
        pdfurl_list.append(i["url"])
print(pdfurl_list)
# ['https://000283-datayes-news.s3.cn-northwest-1.amazonaws.com.cn/vsat/2024/12/11/202412110002GI001J.pdf',
# 'https://000283-datayes-news.s3.cn-northwest-1.amazonaws.com.cn/vsat/2024/12/09/202412090002GI004F.pdf']

# 下载pdf
for pdf_url in pdfurl_list:
    rr.download_vsat_pdf(pdf_url, "./")




