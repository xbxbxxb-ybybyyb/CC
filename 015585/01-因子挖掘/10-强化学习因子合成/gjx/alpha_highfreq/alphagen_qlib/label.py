import pandas as pd
df = pd.read_pickle('/data/user/015585/share_file/for_sxs/low_frequency_all.pkl')
df['avwap'] = df['adjfactor']*df['vwap']
df['a940'] = df['adjfactor']*df['940']
df['low_label'] = df.groupby(level=1).apply(lambda df: (df['avwap'].shift(-2)-df['avwap'].shift(-1))/df['avwap'].shift(-1)).reset_index(level=0, drop=True)
df['high_label'] = df.groupby(level=1).apply(lambda df: (df['avwap'].shift(-1)-df['a940'])/df['a940']).reset_index(level=0, drop=True)
df1 = pd.read_pickle('/data/user/015585/share_file/for_sxs/low_frequency.pkl')


# 在训练的时候用的上面那个，在最后PPT上展示因子池里的因子的时候用的下面正确的数据【没有来得及在训练的时候改掉】
df = pd.read_pickle('/data/user/015585/share_file/for_sxs/low_frequency_all.pkl')
df['avwap'] = df['adjfactor']*df['vwap']
df['a940'] = df['adjfactor']*df['940']
ddf = df.unstack(-1)
df = ddf.stack()
# df['low_label'] = df.groupby(level=1).apply(lambda df: (df['avwap'].shift(-2)-df['avwap'].shift(-1))/df['avwap'].shift(-1)).reset_index(level=0, drop=True)
df['label'] = df.groupby(level=1).apply(lambda df: (df['avwap'].shift(-1)-df['a940'])/df['a940']).reset_index(level=0, drop=True)
df1 = pd.read_pickle('/data/user/015585/share_file/for_sxs/low_frequency.pkl')


print(df1)
print(df)
ff = df1.merge(pd.DataFrame(df[['low_label','high_label']],columns=['low_label','high_label'],index = df.index), left_index=True, right_index=True, how='left')
ff = ff.drop_duplicates()
print(ff)
ff = pd.concat((ff,ff.loc[('2018-10-24', '603996.SH') ,:]))
ff = ff.sort_index(level=None)
print(ff)
# ff['low_label'].to_pickle('/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/low_label.pkl')
# ff['high_label'].to_pickle('./high_label.pkl')
# groups = df.groupby(level=1)
# for group in groups:
#     print(group)
label1 = ff['high_label']
print(label1)
label1.to_pickle('./label.pkl')
# # 低频的文件夹
# label2 = ff['low_label']
# print(label2)
# null_counts = label2.isnull().groupby(level='dt').sum()
# print(null_counts)
# label2.to_pickle('/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/label.pkl')
# df1 = pd.concat((df1,df1.loc[('2018-10-24', '603996.SH') ,:]))
# df1['label'].to_pickle('/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/label1.pkl')