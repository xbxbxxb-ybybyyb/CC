import numpy as np
import pandas as pd
import csv
import IO

df = pd.read_csv('同花顺人气--2019.csv')
print(df.columns)
df['dt'] = df['日期'].apply(lambda x : pd.Timestamp(x))
df['Ticker'] = df['证券代码'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
df['Ticker'] = df['Ticker'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
df = df.drop(['日期','证券代码','证券简称','自选股热度','次日自选变化率','近7日自选变化率','近30日自选变化率'],axis = 1)
df = df.set_index(['dt','Ticker'])
df['is_value'] = 1
#
md_data = IO.read_data([20190101, 20191231],
                      columns=['vwap', 'pre_close', 'adjfactor', 'close', 'high', 'pct_chg', 'turn', 'amt'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data = md_data[md_data['amt'] > 0]
print('md_data原始shape',md_data.shape)
md_data = pd.merge(md_data,df[['is_value']],left_index=True, right_index=True, how='left')
print('同花顺覆盖的shape', md_data[md_data['is_value'] == 1].shape)
print('日均覆盖率：',(md_data[md_data['is_value'] == 1].groupby('dt').sum()['is_value'] / md_data.groupby('dt').count()['amt']).mean())
'''
沪深（包括科创）覆盖率97%，核查未覆盖的标的，多为退市公司，推测是同花顺按最新未退市标的做了筛选，理论上是全部覆盖
'''
# 全市场因子测试
md_data = pd.merge(md_data, df.drop(['is_value'],axis=1), left_index=True, right_index=True, how='left')
columns_ori = ['vwap', 'pre_close', 'adjfactor', 'close', 'high', 'amt', 'pct_chg', 'turn', 'is_value']
factor_columns = ['当日总热度', '近7天总热度', '近30天总热度', '当日浏览热度', '近7天浏览热度', '近30天浏览热度', '当日搜索热度',
       '近7天搜索热度', '近30天搜索热度', '当日关注粘性', '近3日关注粘性', '近7日关注粘性', '近30日关注粘性',]
func_dic = {
    'mean':pd.Series.mean,
    'std':pd.Series.std
}
rolling_param = [1,5,10]
for col in factor_columns:
    for func in func_dic:
        for rolling_day in rolling_param:
            name = f'{col}_{func}_{rolling_day}'
            print(name)
            if func == 'mean':
                md_data[name] = md_data[col].unstack().rolling(rolling_day,1).mean().stack()
            elif func == 'std':
                md_data[name] = md_data[col].unstack().rolling(rolling_day, 1).std().stack()
            print(md_data[[name]].tail())
corr_factor = md_data.groupby('dt').apply(lambda x: x.rank().corr())
res = corr_factor.stack().reset_index().groupby(
    ['level_1', 'level_2'])[0].mean().unstack()
res.to_csv('同花顺人气相关性.csv')
md_data['label'] = md_data['vwap'].unstack().shift(-2).stack() / md_data['vwap'].unstack().shift(-1).stack()
md_data.to_pickle('factor_20250221.pkl')
#
md_data_factor = md_data.drop(columns_ori, axis=1)
corr_df = md_data_factor.groupby('dt').apply(lambda x : x.rank().corr()['label'])
corr_df.mean().to_csv('因子IC日均_2019.csv')

# 同花顺5大因子
for i in ['点击量占比','自选股占比']:
    print(i)
    if i == '点击量占比':
        df = pd.read_csv('thsindex1.csv')
    if i == '自选股占比':
        df = pd.read_csv('thsindex4.csv')
    df['code'] = df['code'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
    df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df.columns = ['dt', 'Ticker', 'name', 'ori']
    df = df[['dt','Ticker','ori']]
    df = df.set_index(['dt', 'Ticker'])
    df['is_value'] = 1
    #
    md_data = IO.read_data([20160101, 20211231],
                           columns=['vwap', 'pre_close', 'adjfactor', 'close', 'high', 'amt', 'pct_chg', 'turn'],
                           alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data = md_data[md_data['amt'] > 0]
    print('md_data原始shape', md_data.shape)
    md_data = pd.merge(md_data, df[['is_value']], left_index=True, right_index=True, how='left')
    print('同花顺覆盖的shape', md_data[md_data['is_value'] == 1].shape)
    print('日均覆盖率：', (md_data[md_data['is_value'] == 1].groupby('dt').sum()['is_value'] / md_data.groupby('dt').count()[
        'amt']).mean())
    #
    # 全市场因子测试
    md_data = pd.merge(md_data, df.drop(['is_value'], axis=1), left_index=True, right_index=True, how='left')
    columns_ori = ['vwap', 'pre_close', 'adjfactor', 'close', 'high', 'amt', 'pct_chg', 'turn', 'is_value']
    factor_columns = ['ori', ]
    func_dic = {
        'mean': pd.Series.mean,
        'std': pd.Series.std
    }
    rolling_param = [1, 5, 10]
    for col in factor_columns:
        for func in func_dic:
            for rolling_day in rolling_param:
                name = f'{col}_{func}_{rolling_day}'
                print(name)
                if func == 'mean':
                    md_data[name] = md_data[col].unstack().rolling(rolling_day, 1).mean().stack()
                elif func == 'std':
                    md_data[name] = md_data[col].unstack().rolling(rolling_day, 1).std().stack()
                print(md_data[[name]].tail())
    md_data['label'] = md_data['vwap'].unstack().shift(-2).stack() / md_data['vwap'].unstack().shift(-1).stack()
    md_data.to_pickle(f'factor_{i}_20250221.pkl')
    corr_factor = md_data.groupby('dt').apply(lambda x: x.rank().corr())
    corr_factor.stack().reset_index().groupby(['level_1','level_2'])[0].mean().unstack().to_csv(f'因子间相关性_{i}.csv')
    #
    md_data_factor = md_data.drop(columns_ori, axis=1)
    corr_df = md_data_factor.groupby('dt').apply(lambda x: x.rank().corr()['label'])
    corr_df.mean().to_csv(f'因子IC日均_{i}_2019.csv')
