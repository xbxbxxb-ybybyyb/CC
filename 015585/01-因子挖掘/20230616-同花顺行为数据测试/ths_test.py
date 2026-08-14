import numpy as np
import pandas as pd
import csv
# 读取txt写入csv
out = open('thsindex4.csv', 'w', newline='')  # 要转成的.csv文件，先创建一个LF1big.csv文件
csv_writer = csv.writer(out, dialect='excel')

f = open("thsindex4_2016-2021.txt", "r")
for line in f.readlines():
    line = line.replace('|', '\t')  # 将每行的逗号替换成空格
    list = line.split()  # 将字符串转为列表，从而可以按单元格写入csv
    csv_writer.writerow(list)
# 清洗格式
df = pd.read_csv('thsindex4.csv')
df['code'] = df['code'].apply(lambda x:str(x).zfill(6))#补tradingcode的0
df['code'] = df['code'].apply(lambda x:x+'.SH'if x.startswith('6') else x+'.SZ')
df['date'] = df['date'].apply(lambda x:pd.Timestamp(x))
df.columns = ['dt','Ticker','name','factor']
#
df = df.set_index(['dt','Ticker'])
df_test = df['factor']
