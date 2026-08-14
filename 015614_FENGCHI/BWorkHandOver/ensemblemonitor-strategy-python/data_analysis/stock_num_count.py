# @Time : 2021/7/8 16:32
# @Author : Zhichen Lu
# @File : stock_num_count.py

import pandas as pd
import os
from dataApi.getData import trans_int2windcode
from dataApi.sendInfo import send_file

def format_df(df,port_id,index=None):
    df['组合编号'] = df['组合编号'].apply(lambda x : str(x)[:len(port_id)])
    df = df[df['组合编号'].eq(port_id)].set_index('证券代码')
    if '交易市场' in df.columns:
        df = df[df['交易市场'].isin(['深交所A','上交所A'])]
    df.index = df.index.astype(int).map(trans_int2windcode)
    return df

path = '/data/user/015664/AFuckingTrigger/实盘/'

os.listdir(f'{path}20210708/')
afternoon_path = '/data/user/011477/order/O32/afternoon/'


stat = {}
detail = {}
for date in [20210702,20210705,20210706,20210707,20210708]:
    holding = pd.read_excel(f'{afternoon_path}综合信息查询_组合证券_{date}.xls')
    holding = format_df(holding,'201001')
    holding = holding[['市值','持仓']]
    holding = holding[holding['持仓']>0]

    order_detail = pd.read_excel(f'/data/user/015664/AFuckingTrigger/实盘/{date}/成交明细及收盘持仓情况{date}.xlsx',sheet_name='委托成交明细')
    sold_info = order_detail[order_detail['类型'].eq('当日卖出')][[ '证券代码', '委托量', '实际成交量']].groupby('证券代码').sum()
    sold_info['完成率'] = sold_info['实际成交量']/sold_info['委托量']
    sold_info = sold_info[sold_info['完成率']<1]

    left_stock = holding[holding['市值']<300000].index.tolist()#list(set(sold_info.index).intersection(set(holding.index)))
    unfinised_info = pd.concat([holding.loc[left_stock],sold_info.loc[left_stock]],axis=1).rename(columns={'市值':'当日收盘持仓市值','持仓':'收盘持仓量','委托量':'当日卖出委托量'}).sort_values('收盘持仓量')
    unfinised_info['备注'] = unfinised_info['收盘持仓量'].apply(lambda x : '零股' if x < 100 else '委托未卖完及小于30万')

    detail[date] = unfinised_info
    stat[date] = unfinised_info.groupby('备注').size()
    stat[date]['当日持仓总量'] = holding.shape[0]
    stat[date]['有效持仓'] = stat[date]['当日持仓总量'] - unfinised_info.shape[0]

stat = pd.DataFrame(stat).T
out_file = '/data/user/015664/AFuckingTrigger/实盘/零股及未完成情况统计.xlsx'
with pd.ExcelWriter(out_file) as writer:
    stat.to_excel(writer,sheet_name='合计')
    for each in sorted(detail.keys()):
        detail[each].to_excel(writer,sheet_name=f'{each}详情')
writer.close()

send_file(['015664'],out_file)
"""



from online_conf import code_list_path,holding_info_path
import pandas as pd
industry = pd.read_excel('/data/group/800319/Concept_monitor/概念板块分工及对应个股.xlsx')
industry = industry[industry['概念板块'].notnull()].groupby([industry.columns[0],'概念板块']).first().reset_index().set_index('Unnamed: 0')
industry = industry[industry['概念板块'].isin(['光伏','半导体','锂电池'])]

date = 20210708

import numpy as np
holding = pd.read_excel(f'{afternoon_path}综合信息查询_组合证券_{date}.xls')
holding = format_df(holding,'201001')
holding = holding[holding['交易市场'].isin(['深交所A','上交所A'])]
holding = holding[['市值','持仓']]
holding = holding[holding['持仓']>0]#.set_index('证券代码')
# holding.index = holding.index.map(lambda x : trans_int2windcode(int(x)))

inter_stk = list(set(industry.index).intersection(set(holding.index)))

holding['市值占比'] = holding['市值']/holding['市值'].sum()
holding['板块'] = np.nan
holding['板块'] = industry.loc[inter_stk,'概念板块'].reset_index().groupby('Unnamed: 0').first().reindex(inter_stk)
holding.groupby('板块').sum()



code_list = pd.read_pickle(code_list_path+'20210707.pkl')


holding_industry = industry.loc[list(holding.keys())]
pool_industry = industry.loc[list(set(code_list).intersection(industry.index))]
stat = pd.DataFrame({'持仓':holding_industry.groupby('概念板块').size(),
                     '股票池':pool_industry.groupby('概念板块').size()})

with pd.ExcelWriter('./板块统计.xlsx') as writer:
    holding_industry.to_excel(writer,sheet_name='持仓情况')
    pool_industry.to_excel(writer,sheet_name='股票池情况')
    stat.to_excel(writer,sheet_name='数量')
    (stat/stat.sum()).to_excel(writer,sheet_name='占比')

writer.close()
from dataApi.sendInfo import send_file
send_file(['015664'],'./板块统计.xlsx')



"""