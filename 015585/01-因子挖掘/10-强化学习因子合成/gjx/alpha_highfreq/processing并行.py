# import pickle
# import pandas as pd
# import os
#
# df = pd.read_pickle('/data/user/015585/share_file/for_sxs/高频数据/20180102.pkl')
# print(df.columns)
# print(sorted(list(set(df['MDTime']))))
# df = pd.read_pickle('/data/user/015585/share_file/for_sxs/高频数据/20180102.pkl')
# print(sorted(list(set(df['MDTime']))))

# 把MDTime也设置为index，和我的外面的代码对上

import pandas as pd
import os
from tqdm import tqdm
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
'''
有错误最后没用这个
'''

folder_path = '/data/user/015585/share_file/for_sxs/高频数据'
pkl_files = sorted(
    [f for f in os.listdir(folder_path) if f.endswith('.pkl')],
    key=lambda x: datetime.strptime(x.split('.')[0], '%Y%m%d')
)
pkl_files.remove('20180110.pkl')
pkl_files = pkl_files[:20]
data = []
all_label = []
def process_file(pkl_file):
    file_path = os.path.join(folder_path, pkl_file)
    df = pd.read_pickle(file_path)
    # 删除一些列
    df = df.drop(columns=['TradingPhaseCode','Buy4Price', 'Buy5Price', 'Buy6Price', 'Buy7Price', 'Buy8Price',
        'Buy9Price', 'Buy10Price', 'Sell4Price', 'Sell5Price', 'Sell6Price',
        'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price',
        'Buy4OrderQty', 'Buy5OrderQty', 'Buy6OrderQty', 'Buy7OrderQty',
        'Buy8OrderQty', 'Buy9OrderQty', 'Buy10OrderQty', 'Sell4OrderQty',
        'Sell5OrderQty', 'Sell6OrderQty', 'Sell7OrderQty', 'Sell8OrderQty',
        'Sell9OrderQty', 'Sell10OrderQty', 'Buy4NumOrders', 'Buy5NumOrders',
        'Buy6NumOrders', 'Buy7NumOrders', 'Buy8NumOrders',
        'Buy9NumOrders', 'Buy10NumOrders', 'Sell4NumOrders', 'Sell5NumOrders',
        'Sell6NumOrders', 'Sell7NumOrders', 'Sell8NumOrders', 'Sell9NumOrders',
        'Sell10NumOrders'])
    df = df[df['MDTime']>=93000000]
    # 计算一些平均成交价
    # 根绝Date和StockCode分组，计算LastPx的均值
    result = df.groupby(['dt', 'Ticker'])['LastPx'].mean()
    pre_close = df.groupby(['dt', 'Ticker'])['pre_close'].first()
    label = (result - pre_close) / pre_close
    print(label)
    # 接下来降频
    # 930-931之间每3秒保留一个数据，931-939之间每15秒保留一个数据，939-940之间每3秒保留一个数据
    # 1）其中最高价和最低价是区间的最高价和最低价，这里的指标是当日到目前时刻的最高价和最低价
    # 【所以逻辑是：1.如果区间内的几个快照显示的最高价发生了改变，则取最高的最高价作为这个区间的最高价
    #              2.如果区间内的几个快照显示的最高价没有发生改变，则取最高的LastPX作为这个区间的最高价】
    # 2）'TotalVolumeTrade','TotalValueTrade','NumTrades'需要后一个时刻和前一个时刻作差才是这个区间的成交量，成交额，成交笔数
    # 先生成时间序列
    time_group = [('9:30','9:31'),('9:31','9:39'),('9:39','9:40')]
    interval = ['3s','15s','3s']
    time_filter = []
    for i in range(0,3):
        times = pd.date_range(start=time_group[i][0], end=time_group[i][1], freq=interval[i]).time
        times = [time for time in times if time != pd.Timestamp('9:15').time()]

        # 将时间转换为9150000这种形式
        times = [int(time.strftime('%H%M%S%f')[:-3]) for time in times]
        time_filter += times[:-1]

    time_filter = [92959900] + time_filter
    idx = [ i for i in range(len(time_filter)-1)]
    df['label'] = pd.cut(df['MDTime'], bins=time_filter, labels=idx, right = True)
    groups = df.groupby(['dt', 'Ticker', 'label'], observed=False)
    df_piece = groups.last()
    # 计算差分
    diff_cols = ['TotalVolumeTrade', 'TotalValueTrade', 'NumTrades']
    groupb1 = df_piece.groupby(['dt', 'Ticker'])
    first_values = groupb1[diff_cols].first()
    df_piece[diff_cols] = groupb1[diff_cols].diff()
    # 保持每个分组的第一行的原值
    for name, group in groupb1:
        df_piece.loc[group.index[0], diff_cols] = first_values.loc[name]
    # print(group)#df_piece['NumTrades'])
    # df_piece[['TotalVolumeTrade','TotalValueTrade','NumTrades']] = df_piece.groupby(['dt', 'Ticker'])[['TotalVolumeTrade','TotalValueTrade','NumTrades']].diff()
    # 这里要增加一个逻辑，对于label小于等于20和abel大于52的行，将这三列除以3，对于label大于20小于等于52的，这三列除以15
    df_piece.loc[
        (df_piece.index.get_level_values('label') > 0) & (df_piece.index.get_level_values('label') <= 20), [
            'TotalVolumeTrade', 'TotalValueTrade', 'NumTrades']] /= 3
    df_piece.loc[
        df_piece.index.get_level_values('label') > 52, ['TotalVolumeTrade', 'TotalValueTrade', 'NumTrades']] /= 3
    df_piece.loc[
        (df_piece.index.get_level_values('label') > 20) & (df_piece.index.get_level_values('label') <= 52), [
            'TotalVolumeTrade', 'TotalValueTrade', 'NumTrades']] /= 15


    df_piece['chage_high'] = groups.last()['HighPx'] - groups.first()['HighPx']
    df_piece['chage_low'] = groups.last()['LowPx'] - groups.first()['LowPx']
    df_piece['max_lastpx'] = groups['LastPx'].max()
    df_piece['min_lastpx'] = groups['LastPx'].min()
    df_piece.loc[:, 'HighPx'] = np.where(df_piece['chage_high'] == 0, df_piece['max_lastpx'], df_piece['HighPx'])
    df_piece.loc[:, 'LowPx'] = np.where(df_piece['chage_low'] == 0, df_piece['min_lastpx'], df_piece['LowPx'])
    # 删除label列，索引变化为[dt,Ticker,feature]，列为MDTime, 删除'chage_high'，'chage_low'，'max_lastpx'，'min_lastpx'
    df_piece = df_piece.drop(columns=['chage_high','chage_low','max_lastpx','min_lastpx'])
    # df_piece = df_piece.reset_index(level='label')
    # df_piece = pd.DataFrame(df_piece.values.T, index =
    df_piece = df_piece.reset_index(level='label')
    df_piece = df_piece.drop(columns=['label'])
    df_piece.set_index('MDTime', append=True, inplace=True)

    return df_piece, label

with ThreadPoolExecutor(max_workers = 8) as executor:
    results = list(tqdm(executor.map(process_file, pkl_files), total=len(pkl_files)))

# 分别获取df和label的值构成list
for df, label in results:
    data.append(df)
    all_label.extend(pd.DataFrame(label))

df = pd.concat(data)
# 去掉第三重索引，把MDTime变成列，其他列变成第三重索引

df = df.sort_index(level=None)
df.to_pickle('./high_data.pkl')
print(df)

all_label = pd.concat(all_label)
all_label = all_label.sort_index(level=None)
all_label.to_pickle('./label.pkl')
print(all_label)

# 20181024只有499支股票，补一行进去【随便复制一个】
label = pd.read_pickle('./label.pkl')
label = pd.DataFrame(label,columns = ['label'])
df = label.loc[('2018-10-24',),:]
ddf = label.loc[('2018-10-24','603996.SH'),:]
label = pd.concat((label,ddf))
label = label.sort_index(level=None)
print(label.shape)
print(label.loc[('2018-10-24',),:])
label.to_pickle('./label.pkl')

data = pd.read_pickle('./high_data.pkl')
df = data.loc[('2018-10-24',),:]
ddf = data.loc[('2018-10-24','603996.SH'),:]
data = pd.concat((data,ddf))
data = data.sort_index(level=None)
print(ddf)
print(data.loc[('2018-10-24',),:])
data.to_pickle('./high_data.pkl')

# 最后存下来的是["Date", "stock_codes", "features"]为索引，MDTime是列