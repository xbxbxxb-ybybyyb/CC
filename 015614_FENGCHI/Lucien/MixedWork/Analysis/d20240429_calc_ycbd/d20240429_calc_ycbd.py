# coding: utf-8
# Author：fengchi863
# Date ：2024/4/29 14:40

from dataApi import tradeDate, stockList
import pandas as pd
from tqdm import tqdm

root_path = '/data/group/800463/stock_list/abnormal_notice_list/'
ycbd_path = '/data/group/800463/stock_list/ycbd_list/'

output_path = '/data/group/800463/stock_list/ycbd_list/d20240429_concat_before/'

date_list = tradeDate.get_date_range(20220818, 20240428)

for dat in tqdm(date_list):
    abnormal = pd.read_excel(root_path + f'abnormal_notice_list_{dat}.xlsx')
    ycbd = pd.read_excel(ycbd_path + f'ycbd_list_{dat}.xlsx', index_col=0)

    abnormal['证券代码'] = abnormal['证券代码'].apply(lambda x: stockList.trans_int2windcode(x))
    abnormal['date'] = dat
    abnormal['banned_indicator'] = ''
    abnormal['异常波动公告数'] = ''
    abnormal['stk_code'] = abnormal['证券代码']

    concat_df = pd.concat([ycbd, abnormal[ycbd.columns]], axis=0).reset_index(drop=True)
    concat_df.to_excel(output_path + f'ycbd_list_{dat}_bak.xlsx')