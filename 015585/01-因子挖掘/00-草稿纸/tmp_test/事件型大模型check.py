import pandas as pd

date = '20250606'
word = '浙江众成'
concept = '成人用品'
tmp = pd.read_pickle(f'/dfs/group/800463/data/news_data/news_data_combo/{date}.pkl', compression = 'gzip')
tmp = list(set(tmp[tmp['content'].str.contains(word)]['content']))
count=0
for i in tmp:
    print('')
    if concept in i:
        print(i)
        count+=1
print(count)

# tmp2 = pd.read_pickle(f'/dfs/group/800463/data/news_data/fid_abnormal/20250603.pkl')




