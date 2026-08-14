# coding: utf-8
# Author：fengchi863
# Date ：2025/4/24 15:43

from xquant.factordata import FactorData
from xquant.textdata import NewsData
import datetime as dt
import shutil

nd = NewsData()
fd = FactorData()

# nowdate = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
# last_date = fd.tradingday(nowdate, -2)[0]

root_path = '/data/group/800463/stock_list/abnormal_notice_list/'
user_path = '/data/user/015614/daily/灰名单生成/黑名单/'

'''
注意不同股票黑名单的日期可能是当天，可能是前一天
遇到紧急情况如无法生成，直接复制前一天的文件作为当天的该股票黑名单，然后再运行grey_list.py
'''
shutil.copyfile(root_path + 'abnormal_notice_list_20250930.xlsx',
                root_path + 'abnormal_notice_list_20251009.xlsx')
shutil.copyfile(user_path + 'abnormal_notice_list_20250930.xlsx',
                user_path + 'abnormal_notice_list_20251009.xlsx')