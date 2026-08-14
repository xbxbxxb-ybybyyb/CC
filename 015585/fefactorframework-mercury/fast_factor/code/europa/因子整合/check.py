import pandas as pd

df2 = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor2.pkl')
df3 = pd.read_pickle('/dfs/user/015585/00-草稿纸/group_level3_memory.pkl')

df2 = df2.loc[pd.Timestamp('20170110'): pd.Timestamp('20231231')]
df3 = df3.loc[pd.Timestamp('20170110'): pd.Timestamp('20231231')]

print(len(set(df2.index) & set(df3.index)) / len(set(df2.index) | set(df3.index)))


