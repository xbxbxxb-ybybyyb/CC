# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 15:25

from dataApi import tradeDate, sendInfo
import pandas as pd
import numpy as np

# start_date = 20150101
start_date = 20221001
end_date = 20221027
date_list = tradeDate.get_date_range(start_date, end_date)

ret_df = pd.DataFrame(index=date_list, columns=['样本数量', 'V1概念数量', 'V2概念数量', 'V1_SW概念比例', 'V2_SW概念比例', 'V2/V1 pct', 'V1_5d概念数量', 'V2_5d概念数量', 'V2_5d/V1_5d pct', 'V1集中度', 'V2集中度'])
demo_v1 = pd.DataFrame()
demo_v2 = pd.DataFrame()
for trade_date in date_list:
    # v1_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_max_pctchg_concept/jupiter/{trade_date}.pkl'
    # v2_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_min_concept_num_concept/jupiter/{trade_date}.pkl'

    v1_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_min_concept_num_concept/jupiter/{trade_date}.pkl'
    v2_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_min_concept_num_concept_v20230403/jupiter/{trade_date}.pkl'
    samples_concept1 = pd.read_pickle(v1_block_path)
    samples_concept2 = pd.read_pickle(v2_block_path)

    demo_v1 = demo_v1.append(samples_concept1)
    demo_v2 = demo_v2.append(samples_concept2)
    # if '&' in ','.join(samples_concept2['概念名称'].dropna().tolist()):
    #     print(1)
    # check = pd.concat([samples_concept1, samples_concept2.rename(columns={'概念代码': '概念代码2', '概念名称': '概念名称2'})], axis=1)
    group1 = samples_concept1.groupby('概念名称')['概念代码'].count()
    group2 = samples_concept2.groupby('概念名称')['概念代码'].count()
    group1_count = (group1 >= 3).sum()
    group2_count = (group2 >= 3).sum()
    concept_num2 = len(samples_concept2['概念代码'].unique())
    samples_num = len(samples_concept1)
    concept_num1 = len(samples_concept1['概念代码'].unique())
    sw21_num = len(list(filter(lambda x: str(x).endswith('.SI'), list(samples_concept1['概念代码'].unique()))))
    sw22_num = len(list(filter(lambda x: str(x).endswith('.SI'), list(samples_concept2['概念代码'].unique()))))
    ret_df.loc[trade_date, ['样本数量', 'V1概念数量', 'V2概念数量', 'V1_SW概念比例', 'V2_SW概念比例']] = [samples_num, concept_num1, concept_num2, sw21_num / concept_num1, sw22_num / concept_num2]
    ret_df.loc[trade_date, ['V1集中度', 'V2集中度']] = [group1_count, group2_count]

demo_v1.to_excel('/data/user/015614/junkData/demo_v1.xlsx')
demo_v2.to_excel('/data/user/015614/junkData/demo_v2.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/junkData/demo_v2.xlsx')
for trade_date in date_list:
    trade_date_list = [tradeDate.get_pre_trade_date(trade_date, 4),
                       tradeDate.get_pre_trade_date(trade_date, 3),
                       tradeDate.get_pre_trade_date(trade_date, 2),
                       tradeDate.get_pre_trade_date(trade_date),
                       trade_date]
    trade_date_list = list(filter(lambda x: x >= 20150101, trade_date_list))
    concept1_list = list()
    concept2_list = list()
    for dat in trade_date_list:
        # v1_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_max_pctchg_concept/jupiter/{dat}.pkl'
        # v2_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_min_concept_num_concept/jupiter/{dat}.pkl'

        v1_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_min_concept_num_concept/jupiter/{dat}.pkl'
        v2_block_path = f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_min_concept_num_concept_v20230403/jupiter/{dat}.pkl'
        samples_concept1 = pd.read_pickle(v1_block_path)
        samples_concept2 = pd.read_pickle(v2_block_path)
        concept1_list.extend(samples_concept1['概念代码'].tolist())
        concept2_list.extend(samples_concept2['概念代码'].tolist())
    concept1_5d_num = len(set(concept1_list))
    concept2_5d_num = len(set(concept2_list))
    ret_df.loc[trade_date, ['V1_5d概念数量', 'V2_5d概念数量']] = [concept1_5d_num, concept2_5d_num]

ret_df['V2/V1 pct'] = ret_df['V2概念数量'] / ret_df['V1概念数量']
ret_df['V2_5d/V1_5d pct'] = ret_df['V2_5d概念数量'] / ret_df['V1_5d概念数量']
sendInfo.send_file(ret_df)