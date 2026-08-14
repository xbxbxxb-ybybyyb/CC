import IO
import pandas as pd

def get_df_ori():
    df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231205_new_data_test/test_data_2023.pkl')
    df_ori.columns = ['dt','Ticker','ins','ind']
    df_ori['dt'] = df_ori['dt'].apply(lambda x : pd.Timestamp(str(x)))
    df_ori['ins'] = df_ori['ins'].astype(float)
    df_ori['ind'] = df_ori['ind'].astype(float)
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
# factor_name_list = ['factor_qyh_heat_20231206_' + str(i) for i in range (13,14)]
factor_name_list = ['factor_qyh_heat_20231206_17']
print(factor_name_list)
res = pd.DataFrame()
for factor_name in factor_name_list:
    print(factor_name)
    m = __import__(factor_name)
    func = getattr(m,factor_name)
    df = func(df_ori.copy())
    df.to_pickle('/data/user/015585/01-因子挖掘/20231205_new_data_test/factor_file_20231206/' + factor_name + '.pkl')
    for col in df.columns:
        df_wind[col] = df[col].unstack().shift(2).stack()
        res_ic_day = df_wind.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))][[factor_name,'pct_chg']]\
            .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
        res_ic_2021 = df_wind.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(20211231))][[factor_name,'pct_chg']]\
            .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
        res_ic_2022 = df_wind.loc[pd.Timestamp(str(20220101)):pd.Timestamp(str(20221231))][[factor_name,'pct_chg']]\
            .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
        res_ic_2023 = df_wind.loc[pd.Timestamp(str(20230101)):pd.Timestamp(str(20231130))][[factor_name,'pct_chg']]\
            .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
        res.loc[col,'ic_all'] = res_ic_day
        res.loc[col,'ic_2021'] = res_ic_2021
        res.loc[col,'ic_2022'] = res_ic_2022
        res.loc[col,'ic_2023'] = res_ic_2023
        print('每日IC的均值：',res_ic_day)
        print('2021IC的均值：',res_ic_2021)
        print('2022IC的均值：',res_ic_2022)
        print('2023IC的均值：',res_ic_2023)


        def rank_(data_):
            data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1,
                                                                                                             1)).stack()
            return data_r
        df_wind['rank'] = rank_(df_wind['factor_qyh_heat_20231206_17'])
        market_avg_pct = df_wind['pct_chg'].groupby('dt').mean()
        import numpy as np
        for i in range(10):
            avg_pct_i = df_wind[(df_wind['rank']>=i/10) & (df_wind['rank']<=(i+1)/10)].groupby('dt')['pct_chg'].mean()
            print(i,(avg_pct_i - market_avg_pct).mean(),((avg_pct_i - market_avg_pct)>=0).sum() / len(avg_pct_i))
