# coding: utf-8
# Author：fengchi863
# Date ：2025/6/24 20:18

from dataApi import tradeDate
import pandas as pd

date_list = tradeDate.get_date_range(20250601, 20250624)

for _dat in date_list:
    print(_dat)
    df1 = pd.read_excel(f'/data/user/011477/Trade_Docs/{_dat}/Tuna/{_dat}_one_hand_buy_list_SZ1.xlsx')
    df2 = pd.read_excel(f'/data/user/011477/Trade_Docs/{_dat}/Tuna/{_dat}_one_hand_buy_list_SZ2.xlsx')
    df3 = pd.read_excel(f'/data/user/011477/Trade_Docs/{_dat}/Tuna/{_dat}_one_hand_buy_list_SH1.xlsx')
    df4 = pd.read_excel(f'/data/user/011477/Trade_Docs/{_dat}/Tuna/{_dat}_one_hand_buy_list_SH2.xlsx')

    df = pd.concat([df1, df2, df3, df4], axis=0)

    count = df.groupby('买入交易账户').count()
    count['证券代码'].describe()