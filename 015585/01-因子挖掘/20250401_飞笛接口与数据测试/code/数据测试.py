import pandas as pd
import numpy as np
import os
import IO
os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdbJG.stockdata import StockData
from xquant.thirdpartydata.factordata import FactorData
import sys
s = FactorData()
xdb_datasource = StockData()
# df = s.get_factor_value("GOGOAL2_STOCK_CHANGE_ATTRIBUTION")
df = pd.read_pickle('feidi_all_for_stat.pkl')
# df.to_pickle('feidi_all_for_stat.pkl')
'''
Index(['ID', 'TRADINGCODE', 'HTCODE', 'SECUABBR', 'SECUCODE', 'EXCHANGECODE',
       'BOARDCODE', 'CHANGETYPE', 'EVENTTITLE', 'CHANGEATTRIBUTION', 'PUBDATE',
       'CHANGERATE', 'TOPICID', 'TOPICNAME', 'ISVALID', 'ENTRYTIME',
       'UPDATETIME', 'GROUNDTIME', 'RESOURCEID', 'RECORDID'],
'''
# 数据预处理
for col in ['PUBDATE', 'ENTRYTIME', 'UPDATETIME', 'GROUNDTIME']:
    df[col] = df[col].apply(lambda x : pd.Timestamp(x))
df = df.rename(columns = {'PUBDATE':'PUBTIME'})
df['PUBDATE'] = df['PUBTIME'].apply(lambda x : x.normalize() if not pd.isna(x) else np.nan)
df['year'] = df['PUBDATE'].apply(lambda x : x.year)
df = df[df['PUBDATE'] >= pd.Timestamp('20220101')]
# 数据量统计:客观上的数据量
df_count_day = df.groupby('PUBDATE').count()['ID'].to_frame().reset_index()
df_count_day['year'] = df_count_day['PUBDATE'].apply(lambda x : x.year)
df_count_day = df_count_day.set_index('PUBDATE')

df_count_day_pos = df[df['CHANGETYPE'] == 1].groupby('PUBDATE').count()['ID'].to_frame().reset_index()
df_count_day_pos['year'] = df_count_day_pos['PUBDATE'].apply(lambda x : x.year)
df_count_day_pos = df_count_day_pos.set_index('PUBDATE')

df_count_day_neg = df[df['CHANGETYPE'] == -1].groupby('PUBDATE').count()['ID'].to_frame().reset_index()
df_count_day_neg['year'] = df_count_day_neg['PUBDATE'].apply(lambda x : x.year)
df_count_day_neg = df_count_day_neg.set_index('PUBDATE')
print('每年的日均数量：')
print(df_count_day.groupby('year').mean())
print('每年正向触发日均数量：')
print(df_count_day_pos.groupby('year').mean())
print('每年负向触发日均数量：')
print(df_count_day_neg.groupby('year').mean())
# 统计板块信息覆盖度
num_topic = len(df[~df['TOPICNAME'].isna()])
df_pos = df[df['CHANGETYPE'] == 1]
df_neg = df[df['CHANGETYPE'] == -1]
num_topic_pos = len(df_pos[~df_pos['TOPICNAME'].isna()])
num_topic_neg = len(df_neg[~df_neg['TOPICNAME'].isna()])
print(f'TOPIC_NAME覆盖度：{num_topic/len(df)}')
print(f'TOPIC_NAME_POS覆盖度：{num_topic_pos/len(df_pos)}')
print(f'TOPIC_NAME_NEG覆盖度：{num_topic_neg/len(df_neg)}')
# 和每日涨停的差异
def cal_ul_price(pre_close_dataframe, ratio = 0.1):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+ratio) + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+2*ratio) + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
md_data = IO.read_data([20220601, 20250331], columns=['amt', 'high','open','close','pre_close','vwap','adjfactor'],
                        alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['ul_price'] = cal_ul_price(md_data)
md_data['is_zt'] = (md_data['high'] == md_data['ul_price']).apply(int) # 注意是触碰到涨停价格
md_data_filter = md_data[md_data['is_zt'] == 1]
df_stat = df.rename(columns = {'PUBDATE':'dt', 'HTCODE':'Ticker'}).set_index(['dt','Ticker'])
df_stat['is_value'] = 1
res = pd.merge(md_data_filter[['is_zt']], df_stat[['is_value']], left_index=True, right_index=True, how='left')
res = res.loc[pd.Timestamp('20220701'):]
print(f'对涨停股票的覆盖率：{res["is_value"].sum() / len(res)}')
# 此处抽样检查了一些没有覆盖的标的，发现都是一触即退的样本/特殊样本譬如退市，但也有20250331 特力A涨停没有记录
# UPDATE和ENTRY
df['timedelta_update_entry'] = df['UPDATETIME'] - df['ENTRYTIME']
print('UPDATE和ENTRY的差异：')
print(df[df['PUBTIME'] >= pd.Timestamp('20250101')]['timedelta_update_entry'].quantile([0.25,0.5,0.75,0.9,0.99]))
# 鉴于pubdate最早为2022-07-01，entrytime最早为2022-10-31，从2023-01-01起验证时效性
df_sxs = df[df['PUBTIME'] >= pd.Timestamp('20230101')]
df_sxs['timedelta'] = df_sxs['ENTRYTIME'] - df_sxs['PUBTIME']
# 负数：这个是因为我们Pubdate取得是飞笛的news_release_time，有可能是他推送我们数据之后再上架，有一两秒延迟
print('entrytime更早的数量:',df_sxs[df_sxs['timedelta'] < pd.Timedelta('0 days')].shape[0])
print(f'time_delta(和pubtime差异)的均值为{df_sxs["timedelta"].mean()}, 分位数为{df_sxs["timedelta"].quantile([0.25,0.5,0.75,0.9,0.99])}')
# 进一步考察和股票实际触发时间的时效性
df_sxs_zt_time = pd.merge(md_data_filter[['is_zt','high','ul_price','pre_close']], df_stat[['is_value','PUBTIME','ENTRYTIME']],
                          left_index=True, right_index=True, how='left')
df_sxs_zt_time = df_sxs_zt_time[df_sxs_zt_time['PUBTIME'] >= pd.Timestamp('20230101')]
df_sxs_zt_time['zt_time'] = np.nan
for index, row in df_sxs_zt_time.iterrows():
    print(index)
    dt = index[0]
    Ticker = index[1]
    ul_price = row['ul_price']
    try:
        df_trade = xdb_datasource.get_trade(dt.strftime('%Y%m%d'), Ticker)
        zt_time = df_trade[df_trade['trade_price'] == ul_price]['md_time'].min()
        df_sxs_zt_time.loc[index, 'zt_time'] = zt_time
    except:
        pass
df_sxs_zt_time.to_pickle('df_sxs_zt_time.pkl')

def combine_datetime(row):
    try:
        time_int = int(row['zt_time'])
        date = row.name[0]
        time_str = f"{time_int:09d}"
        return pd.Timestamp(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=int(time_str[:2]),
            minute=int(time_str[2:4]),
            second=int(time_str[4:6]),
            microsecond=int(time_str[6:9]) * 1000
        )
    except ValueError as e:
        return np.nan
for index, row in df_sxs_zt_time.iterrows():
    sys.stdout.write(f'\r{index}')
    sys.stdout.flush()
    df_sxs_zt_time.loc[index, 'zt_timestamp'] = combine_datetime(row)

df_sxs_zt_time['timedelta_2zttime'] = df_sxs_zt_time['ENTRYTIME'] - df_sxs_zt_time['zt_timestamp']
print(f'time_delta(和zttime的差异)的均值为{df_sxs_zt_time["timedelta_2zttime"].mean()}, 90%分位数为{df_sxs_zt_time["timedelta_2zttime"].quantile([0.25,0.5,0.75,0.9,0.99])}')
print('2025以来时效性：')
print(df_sxs_zt_time[df_sxs_zt_time['PUBTIME'] >= pd.Timestamp('20250101')]["timedelta_2zttime"].quantile([0.25,0.5,0.75,0.9,0.99]))

