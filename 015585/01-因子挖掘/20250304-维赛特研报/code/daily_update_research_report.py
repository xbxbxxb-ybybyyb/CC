import pandas as pd
import numpy as np
import IO
import os
from xquant.textdata import ResearchReport
from joblib import Parallel, delayed
import datetime
import time
import shutil
rr = ResearchReport()
'''
1、研报获取是按照pubdate,但信息技术部实际入库时间往往比pubdate晚，在几分钟-1周不等
2、每日更新时，重新落过去7自然日的基本信息，再根据基本信息下载“增量”的pdf
3、由此，日期.pkl代表的是目前能拿到的，pubdate为日期 的研报。使用历史数据如果需要控制未来信息，可以参考entrytime做筛选
'''
# ==============================================step1 basicinfo===================================================
# 基本信息相关函数
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
# 下载过去7日的基本信息，直接覆盖

end_date = time.strftime('%Y%m%d', time.localtime()) # '20250101'
# end_date = '20250831'
start_date = (pd.Timestamp(end_date) - pd.Timedelta(days=7)).strftime('%Y%m%d')

start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
date_list = [i.strftime('%Y%m%d') for i in date_list]

root_path = '/dfs/group/800463/public/research_report_data/rr_basicinfo/'
error_date = []
for date in date_list:
    res = get_rr_by_date(date,date)
    res.to_pickle(f'{root_path}{date}.pkl')
print(f'start_date={start_date},end_date={end_date}, 研报基本信息下载完成')

# =============================================step2 content======================================================
command = 'pip install pdfplumber'
os.system(command)
command = 'pip install PyMuPDF'
os.system(command)
import pdfplumber
import fitz

def download_pdf(pdf_url, pdf_save_path, date):
    if not os.path.exists(f'{pdf_save_path}{date}'):
        os.makedirs(f'{pdf_save_path}{date}')
    if pdf_url[-3:] == 'pdf':
        url_prefix = "http://168.7.16.200:28118/000283-datayes-news"
        if "https://000283-datayes-news.s3.cn-northwest-1.amazonaws.com.cn" in pdf_url:
            pdf_url = pdf_url.replace("https://000283-datayes-news.s3.cn-northwest-1.amazonaws.com.cn",
                                      url_prefix)
        elif "https://htfic.htzq.com.cn/ht/report" in pdf_url:
            pdf_url = pdf_url.replace("https://htfic.htzq.com.cn/ht/report", url_prefix)
        rr.download_vsat_pdf(pdf_url, f'{pdf_save_path}{date}/')
    return 1
def del_pdf_file(pdf_save_path, date):
    shutil.rmtree(f'{pdf_save_path}{date}/')
    return
def parse_pdf_file(pdf_save_path, date, df_ori):
    def extract_text_from_df_test(pdf_path):
        text = ''
        try:
            with fitz.open(pdf_path) as pdf:
                for page_num in range(pdf.pageCount):
                    text += pdf.loadPage(page_num).getText()
        except:
            pass
        return text
    df_ori['content'] = ''
    for reportCode in df_ori['reportCode']:
        if os.path.exists(f'{pdf_save_path}{date}/{reportCode}.pdf'):
            df_ori.loc[df_ori[df_ori['reportCode'] == reportCode].index, 'content'] = extract_text_from_df_test(f'{pdf_save_path}{date}/{reportCode}.pdf')
    return df_ori
def get_url(x):
    if len(x) > 1:
        print(f'存在不止1个url，annex={x}')
        url = ''
    elif len(x) == 0:
        # print(f'没有pdf的url，annex={x}')
        url = ''
    else:
        url = x[0]['url']
    return url
def get_pdf_text_by_date(date, basicinfo_path, pdf_save_path, out_path):
    # 读取对应date的基本信息，获取pdf的url
    df_ori = pd.read_pickle(f'{basicinfo_path}{date}.pkl')
    df_ori['content_url'] = df_ori['annex'].apply(lambda x : get_url(x))
    # 识别新增的url
    try:
        df_content_exists = pd.read_pickle(f'{out_path}{date}.pkl')
        list_content_url_exists = list(df_content_exists['content_url'])
    except:
        df_content_exists = pd.DataFrame(columns = ['reportCode', 'content_url', 'content'])
        list_content_url_exists = []
    # 下载当日新增的到中转文件夹
    for url in df_ori['content_url']:
        if url not in list_content_url_exists:
            download_pdf(url, pdf_save_path, date)
    # 解析文件夹下所有pdf文件，以字符串形式保存在df_ori中
    df_ori = parse_pdf_file(pdf_save_path, date, df_ori)
    # 将df_ori中新增的部分append到df_content_exists
    df_content_exists = df_content_exists.append(df_ori[df_ori['content'].apply(len) > 0][['reportCode', 'content_url', 'content']])
    df_content_exists.to_pickle(f'{out_path}{date}.pkl')
    # 删除对应日期的pdf临时中转文件夹
    if os.path.exists(f'{pdf_save_path}{date}/'):
        del_pdf_file(pdf_save_path, date)
    return


basicinfo_path = '/dfs/group/800463/public/research_report_data/rr_basicinfo/'
pdf_save_path = '/dfs/group/800463/public/research_report_data/文件中转/'
out_path = '/dfs/group/800463/public/research_report_data/rr_content/'



factor_df_list = Parallel(n_jobs=7)(delayed(get_pdf_text_by_date)(date,basicinfo_path,pdf_save_path,out_path) for date in date_list)

# 发送link消息
from xquant.xqutils.helper import link

lm = link.LinkMessage(['015585'])
end_date = end_date.strftime('%Y%m%d')
df_basicinfo = pd.read_pickle(f'{basicinfo_path}{end_date}.pkl')
df_content = pd.read_pickle(f'{out_path}{end_date}.pkl')
message = f'研报数据下载:{end_date} 成功，基本信息长度{len(df_basicinfo)}，正文文件长度{len(df_content)}'
lm.sendMessage(message)
