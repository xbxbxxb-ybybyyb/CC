import pandas as pd
import os
import numpy as np
import IO
# 雪球
root_path = '/dfs/user/015585/05_datago/test_data/sftp/XACRIS/20250213-delivery/'
package_list = ['XACRIS-V3_natural_day_stat',
                'XACRIS-V3_post_hotness_info',
                'XACRIS-V3_post_info',
                'XACRIS-V3_post_related_stock',
                'XACRIS-V3_user_info']
df_nd_stat = pd.read_csv(f'{root_path}{package_list[0]}/{package_list[0]}_20200101to20241231.csv')

df_nd_stat_202411 = df_nd_stat[(df_nd_stat['pub_date'] <= '2024-11-30') & (df_nd_stat['pub_date'] >= '2024-11-01')]
df_nd_stat_202411.to_pickle('/dfs/user/015585/999_sharefiles/for_wys/202502_雪球与股吧数据样例/雪球_202411.pkl')
# 股吧
root_path = '/dfs/user/015585/05_datago/test_data/sftp/GACRIS/20250213-delivery/'
package_list = ['GACRIS-V3_natural_day_basic_stat',
                'GACRIS-V3_post_hotness_info',
                'GACRIS-V3_post_info',
                'GACRIS-V3_post_related_stock',
                'GACRIS-V3_user_info',
                'GACRIS-V3_cfh_natural_day_stat',
                'GACRIS-V3_platform_post_daily_stat'
                ]
df_nd_stat = pd.read_csv(f'{root_path}{package_list[0]}/{package_list[0]}_20200101to20241231.csv')
df_nd_stat_cfh = pd.read_csv(f'{root_path}{package_list[5]}/{package_list[5]}_20200101to20241231.csv')
df_nd_stat_plat = pd.read_csv(f'{root_path}{package_list[6]}/{package_list[6]}_20200101to20241231.csv')

df_nd_stat_202411 = df_nd_stat[(df_nd_stat['pub_date'] <= '2024-11-30') & (df_nd_stat['pub_date'] >= '2024-11-01')]
print(df_nd_stat_202411.shape)
df_nd_stat_202411.to_pickle('/dfs/user/015585/999_sharefiles/for_wys/202502_雪球与股吧数据样例/股吧_个人帖子_202411.pkl')

df_nd_stat_cfh_202411 = df_nd_stat_cfh[(df_nd_stat_cfh['pub_date'] <= '2024-11-30') & (df_nd_stat_cfh['pub_date'] >= '2024-11-01')]
print(df_nd_stat_cfh_202411.shape)
df_nd_stat_cfh_202411.to_pickle('/dfs/user/015585/999_sharefiles/for_wys/202502_雪球与股吧数据样例/股吧_财富号文章_202411.pkl')

df_nd_stat_plat_202411 = df_nd_stat_plat[(df_nd_stat_plat['pub_date'] <= '2024-11-30') & (df_nd_stat_plat['pub_date'] >= '2024-11-01')]
print(df_nd_stat_plat_202411.shape)
df_nd_stat_plat_202411.to_pickle('/dfs/user/015585/999_sharefiles/for_wys/202502_雪球与股吧数据样例/股吧_平台生成文章_202411.pkl')
