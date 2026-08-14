# coding: utf-8
# Author：fengchi863
# Date ：2023/7/7 9:25

"""
用于半年报PPT绘图，计算Jupiter和Europa的参与率
"""

import pandas as pd
import numpy as np
from dataApi import tradeDate
from dataApi.sendInfo import send_file
from tqdm import tqdm

date_list = tradeDate.get_date_range(20220518, 20230630)
label_path = '/data/group/800463/日内强势股/log_parse/因子耗时/'
jup_triggered = pd.read_excel(label_path + f'实盘触发标签汇总_2023-07-06.xlsx')
jup001_triggered = pd.read_excel(label_path + f'实盘触发标签汇总New_2023-07-06.xlsx')

parti_ratio_df = pd.DataFrame(index=date_list, columns=['triggered', 'signal', 'parti_ratio'])

for _dat in tqdm(date_list):
    _dat = str(_dat)
    _dat_str = _dat[:4] + '-' + _dat[4:6] + '-' + _dat[6:8]

    jup_triggered['datelist'] = jup_triggered['dt'].apply(lambda x: x.strftime('%Y%m%d'))
    jup001_triggered['datelist'] = jup001_triggered['dt'].apply(lambda x: x.strftime('%Y%m%d'))
    triggered_list1 = jup_triggered.query(f'datelist == "{_dat}"')['Ticker']
    triggered_list2 = jup001_triggered.query(f'datelist == "{_dat}"')['Ticker']
    triggered_list = list(set(triggered_list1).intersection(triggered_list2))

    signal_list1 = jup_triggered.query(f'datelist == "{_dat}" & shouldBuySignal == 1')['Ticker']
    signal_list2 = jup001_triggered.query(f'datelist == "{_dat}" & shouldBuySignal == 1')['Ticker']
    signal_list = list(set(signal_list1).intersection(signal_list2))

    parti_ratio_df.loc[int(_dat), 'triggered'] = len(triggered_list)
    parti_ratio_df.loc[int(_dat), 'signal'] = len(signal_list)
    parti_ratio_df.loc[int(_dat), 'parti_ratio'] = len(signal_list) / len(triggered_list)

parti_ratio_df['parti_ratio_roll5d'] = parti_ratio_df['parti_ratio'].rolling(5, min_periods=1).mean()
send_file(parti_ratio_df)









