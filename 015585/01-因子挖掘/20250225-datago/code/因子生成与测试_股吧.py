import pandas as pd
import os
import numpy as np
import IO
import decimal


def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
# 数据准备
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

df_nd_stat['dt'] = df_nd_stat['pub_date'].apply(pd.Timestamp)
df_nd_stat['year'] = df_nd_stat['dt'].apply(lambda x : x.year)
df_nd_stat = df_nd_stat.rename(columns = {'stock_id':'Ticker'})
df_nd_stat = df_nd_stat.set_index(['dt','Ticker'])
df_nd_stat['is_value'] = 1 # 添加标识符便于统计全面性

columns_ori = ['amt', 'pre_close', 'close', 'high', 'vwap']
md_data = IO.read_data([20200101, 20241231], columns = columns_ori,
                       alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['zcz']=(((md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='30'))&(md_data.reset_index()['dt']>='2020-08-24'))
|(md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='68'))).values
md_data['bj'] = (md_data.reset_index()['Ticker'].apply(lambda x:x[-2:]=='BJ')).values
zt_price = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
zt_price[md_data['zcz']] = np.floor(md_data['pre_close'] * 100 * 1.2 + 0.5) / 100
zt_price[md_data['bj']] = np.floor(md_data['pre_close'] * 100 * 1.3 + 0.5) / 100
md_data['zt_price'] = zt_price
md_data['is_trigger'] = md_data['high'] >= (md_data['zt_price'] - 0.01).apply(lambda x : round_(x,2))
md_data['is_zt'] = md_data['close'] == md_data['zt_price']
# 因子计算
factor_columns = ['read_neg_sum', 'reply_neg_sum', 'post_neg_sum',
       'user_neg', 'user_avg_bar_age_neg', 'read_neu_sum', 'reply_neu_sum',
       'post_neu_sum', 'user_neu', 'user_avg_bar_age_neu', 'read_pos_sum',
       'reply_pos_sum', 'post_pos_sum', 'user_pos', 'user_avg_bar_age_pos',
       'read_all_sum', 'reply_all_sum', 'post_all_sum', 'user_all',
       'user_avg_bar_age_all', 'senti_score_div', 'senti_score_log',
       'senti_conform']


func_dic = {
    'mean': pd.Series.mean,
    'std': pd.Series.std
}
rolling_param = [1, 5, 10]
### 全市场
md_data_calc = pd.merge(md_data, df_nd_stat[factor_columns], left_index=True, right_index=True, how='left')
for col in factor_columns:
    for func in func_dic:
        for rolling_day in rolling_param:
            name = f'{col}_{func}_{rolling_day}'
            print(name)
            if func == 'mean':
                md_data_calc[name] = md_data_calc[col].unstack().rolling(rolling_day, 1).mean().stack().fillna(0)
            elif func == 'std':
                md_data_calc[name] = md_data_calc[col].unstack().rolling(rolling_day, 1).std().stack()
            # print(md_data_calc[[name]].tail())
md_data_calc['label'] = md_data_calc['vwap'].unstack().shift(-2).stack() / md_data_calc['vwap'].unstack().shift(-1).stack()
md_data_calc.to_pickle(f'factor_股吧_全市场_20250228.pkl')
corr_factor = md_data_calc.groupby('dt').apply(lambda x: x.rank().corr())
corr_factor.stack().reset_index().groupby(['level_1', 'level_2'])[0].mean().unstack().loc[factor_columns,columns_ori].to_csv(f'因子间相关性_股吧_全市场.csv')
#
md_data_factor = md_data_calc.drop(columns_ori, axis=1)
corr_df = md_data_factor.groupby('dt').apply(lambda x: x.rank().corr()['label'])
corr_df.mean().to_csv(f'因子IC日均_股吧_全市场_2020_2024.csv')

### europa
md_data['label'] = md_data['vwap'].unstack().shift(-2).stack() / md_data['zt_price'].unstack().shift(-1).stack()
md_data_europa = md_data[(md_data['is_trigger'].unstack().shift(-1).stack() == True) & (md_data['is_zt'] == False)]
md_data_calc = pd.merge(md_data_europa, df_nd_stat[factor_columns], left_index=True, right_index=True, how='left')
for col in factor_columns:
    for func in func_dic:
        for rolling_day in rolling_param:
            name = f'{col}_{func}_{rolling_day}'
            print(name)
            if func == 'mean':
                md_data_calc[name] = md_data_calc[col].unstack().rolling(rolling_day, 1).mean().stack().fillna(0)
            elif func == 'std':
                md_data_calc[name] = md_data_calc[col].unstack().rolling(rolling_day, 1).std().stack()
                # print(md_data_calc[[name]].tail())

md_data_calc.to_pickle(f'factor_股吧_europa_20250228.pkl')
corr_factor = md_data_calc.groupby('dt').apply(lambda x: x.rank().corr())
corr_factor.stack().reset_index().groupby(['level_1', 'level_2'])[0].mean().unstack().loc[factor_columns,columns_ori].to_csv(f'因子间相关性_股吧_europa.csv')
#
md_data_factor = md_data_calc.drop(columns_ori, axis=1)
corr_df = md_data_factor.groupby('dt').apply(lambda x: x.rank().corr()['label'])
corr_df.mean().to_csv(f'因子IC日均_股吧_europa_2020_2024.csv')
