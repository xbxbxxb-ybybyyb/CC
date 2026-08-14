import pandas as pd

index0 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20160101_20191231.pkl')
index1 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20200101_20200630.pkl')
index2 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20200701_20201231.pkl')
index3 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20210101_20210630.pkl')
index4 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20210701_20211231.pkl')
index5 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20220101_20220630.pkl')
index6 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20220701_20221231.pkl')
index7 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20230101_20230630.pkl')
index8 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20230701_20231231.pkl')
index9 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20240101_20240630.pkl')
index10 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20240701_20241231.pkl')
index11 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20250101_20250513.pkl')

index_df = pd.concat([index0,index1,index2,index3,index4,index5,index6,index7,index8,index9,index10,index11]).sort_index()

index_df['1430_is_zt'] = (index_df['1430_price']==index_df['ul_price']).astype(float)
index_df['1430_is_dt'] = (index_df['1430_price']==index_df['dl_price']).astype(float)

sta = pd.DataFrame(index=index_df.index.get_level_values(0).unique())
sta['涨停股权重比例'] = (index_df['1430_is_zt']*index_df['weight']).groupby('dt').sum()
sta['涨停股个数'] = index_df['1430_is_zt'].groupby('dt').sum()

sta['跌停股权重比例'] = (index_df['1430_is_dt']*index_df['weight']).groupby('dt').sum()
sta['跌停股个数'] = index_df['1430_is_dt'].groupby('dt').sum()

index_df.to_pickle('/dfs/user/023859/neptune/index_df_20160101_20250513.pkl')
sta.to_excel('/dfs/user/023859/share_file/for_wys/zz1000/20250513/交易日1430时点涨跌停权重比例_20160101_20250513.xlsx')


