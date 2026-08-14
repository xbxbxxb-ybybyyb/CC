import pandas as pd
import numpy as np
# import IO
import os
from xquant.textdata import ResearchReport
from joblib import Parallel, delayed
import datetime
import shutil
import time
command = 'pip install pdfplumber'
os.system(command)
command = 'pip install PyMuPDF'
os.system(command)
import pdfplumber
import fitz

rr = ResearchReport()

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
    def extract_text_from_df(pdf_path):
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
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
    # 下载当日所有pdf到中转文件夹
    for url in df_ori['content_url']:
        download_pdf(url, pdf_save_path, date)
    # 解析文件夹下所有pdf文件，以字符串形式保存在df_ori中
    df_ori = parse_pdf_file(pdf_save_path, date, df_ori)
    df_ori[['reportCode', 'content_url', 'content']].to_pickle(f'{out_path}{date}.pkl')
    # 删除对应日期的pdf临时中转文件夹
    del_pdf_file(pdf_save_path, date)
    return

start_date = '20250101'
end_date = '20250827'
basicinfo_path = '/dfs/group/800463/public/research_report_data/rr_basicinfo/'
pdf_save_path = '/dfs/group/800463/public/research_report_data/文件中转/'
out_path = '/dfs/group/800463/public/research_report_data/rr_content/'
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
date_list = [i.strftime('%Y%m%d') for i in date_list]

def get_loss_date(basicinfo_path, out_path):
    list_basicinfo = os.listdir(basicinfo_path)
    list_content = os.listdir(out_path)
    res = [i for i in list_basicinfo if i not in list_content]
    res = [i.replace('.pkl','') for i in res]
    res.sort()
    return res

date_loss = get_loss_date(basicinfo_path, out_path)

# time_list = [time.localtime()]

factor_df_list = Parallel(n_jobs=24)(delayed(get_pdf_text_by_date)(date,basicinfo_path,pdf_save_path,out_path) for date in date_loss)
