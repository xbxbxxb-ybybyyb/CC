import IO
import pandas as pd

def get_df_ori():
    df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231205_new_data_test/tradingheat.pkl')
    df_ori.columns = ['Ticker','ins','ind','factor','dt']
    df_ori['dt'] = df_ori['dt'].apply(lambda x : pd.Timestamp(str(x)))
    df_ori['ins'] = df_ori['ins'].astype(float)
    df_ori['ind'] = df_ori['ind'].astype(float)
    df_ori['factor'] = df_ori['ind'].astype(float)
    df_ori = df_ori.set_index(['dt','Ticker'])
    df_ori = df_ori.sort_values(['dt','Ticker'])
    return df_ori
start_date,end_date = 20210101,20231130
#
df_wind = IO.read_data([start_date, end_date],
                      columns=['pct_chg'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_ori = get_df_ori()
#
res = pd.DataFrame()
factor_name = 'factor'
df_wind[factor_name] = df_ori[factor_name].unstack().shift(2).stack()
res_ic_day = df_wind.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))][[factor_name,'pct_chg']]\
    .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
res_ic_2021 = df_wind.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(20211231))][[factor_name,'pct_chg']]\
    .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
res_ic_2022 = df_wind.loc[pd.Timestamp(str(20220101)):pd.Timestamp(str(20221231))][[factor_name,'pct_chg']]\
    .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
res_ic_2023 = df_wind.loc[pd.Timestamp(str(20230101)):pd.Timestamp(str(20231130))][[factor_name,'pct_chg']]\
    .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
print('每日IC的均值：',res_ic_day)
print('2021IC的均值：',res_ic_2021)
print('2022IC的均值：',res_ic_2022)
print('2023IC的均值：',res_ic_2023)


