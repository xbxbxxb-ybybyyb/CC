import pandas as pd
import os
from xquant.textdata import ResearchReport

rr = ResearchReport()
url_prefix = "http://168.7.16.200:28118/000283-datayes-news"
pdf_url = 'https://htfic.htzq.com.cn/ht/report/vsat/2025/01/01/202501010002GI002Y.pdf'
if "https://000283-datayes-news.s3.cn-northwest-1.amazonaws.com.cn" in pdf_url:
    pdf_url = pdf_url.replace("https://000283-datayes-news.s3.cn-northwest-1.amazonaws.com.cn",
                              url_prefix)
elif "https://htfic.htzq.com.cn/ht/report" in pdf_url:
    pdf_url = pdf_url.replace("https://htfic.htzq.com.cn/ht/report", url_prefix)
rr.download_vsat_pdf(pdf_url, '/data/user/015585/')