# coding: utf-8
# Author：fengchi863
# Date ：2021/6/11 14:40

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import save_xlsx, save_pickle
from ShortTermTrading.Util.System import get_minutely_df_true, add_stock_name

import pandas as pd
'''
file_path = [junk_path + '20210616_1.pkl',
             junk_path + '20210616_2.pkl',
             junk_path + '20210616_3.pkl',
             junk_path + '20210616_4.pkl']

df_list = list()
for idx in range(len(file_path)):
    res = pd.read_pickle(file_path[idx])
    print(res.sum().sum())
    df_list.append(res)

df_list[0] = df_list[0].reindex(columns=df_list[3].columns, fill_value=False)
df_list[1] = df_list[1].reindex(columns=df_list[3].columns, fill_value=False)
df_list[2] = df_list[2].reindex(columns=df_list[3].columns, fill_value=False)
df_list[3] = df_list[3].reindex(columns=df_list[3].columns, fill_value=False)

print('已读取完成')
df = pd.DataFrame()
df = df.append(df_list[0])
df = df.append(df_list[1])
df = df.append(df_list[2])
df = df.append(df_list[3])
print('已拼接完成')

stk_minute_point = df.sort_index()
save_pickle(stk_minute_point, junk_path, '20210616_v3.pkl')
# stk_minute_point = stk_minute_point.fillna(False)
# minutely_true_df = get_minutely_df_true(stk_minute_point)
# minutely_true_df = add_stock_name(minutely_true_df)
# save_xlsx(minutely_true_df, junk_path, 'minutely_true_df.xlsx')
'''
if __name__ == '__main__':
    # 分解池子
    stk_df = pd.read_pickle(junk_path + '20210616_v3.pkl')
    from tqdm import tqdm
    daily_stock_flag = stk_df.groupby('date').sum() > 0
    save_pickle(daily_stock_flag, junk_path, '20210616_daily_stock_flag.pkl')
    for stk_id in tqdm(stk_df.columns):
        res = stk_df[stk_id]
        res = pd.DataFrame(res)
        res.columns = ['prediction']
        if res.sum().sum() > 0:
            print(res.sum().sum())
        save_pickle(res, junk_path + '20210616/', '%d.pkl' % stk_id)
# '''