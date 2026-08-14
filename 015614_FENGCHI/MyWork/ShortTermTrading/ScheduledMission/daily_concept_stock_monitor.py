# coding: utf-8
# Author：fengchi863
# Date ：2021/6/9 19:53
import os, sys
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')
sys.path.append('/data/user/fengchi/MyWork/FaaMonitor')
from FaaMonitor.personal.fengchi.generate3DailyStock.add2excel import Add2Excel
import pandas as pd
from ShortTermTrading.Util.tools import send_message, send_file, save_xlsx
from ShortTermTrading.conf.path_conf import junk_path

a2e = Add2Excel()

path = '/data/group/800319/Concept_monitor/主题个股监控%d.xlsx' % a2e.date
df1 = pd.read_excel(path)
df1 = df1.rename(columns={'Unnamed: 0': '股票代码'})

res = a2e.start_convert(df1)
columns_list = res.columns.tolist()[0:6] + ['低位股', '补涨/中位股', '龙头首阴'] + res.columns.tolist()[6:]
res = res[columns_list]
save_xlsx(res, junk_path, '主题个股监控%d.xlsx' % a2e.date)
send_file(['015614'], junk_path + '主题个股监控%d.xlsx' % a2e.date)
print('已发送到xquant')