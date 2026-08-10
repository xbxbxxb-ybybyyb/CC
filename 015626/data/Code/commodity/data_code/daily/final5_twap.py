df = IO.read_data(alt = '/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5')
df = df.reset_index().rename(columns = {'Ticker':'category', 'wind_code':'Ticker'}).set_index(['dt', 'Ticker'])

df5_all = IO.read_data(columns = ['twap'], alt = '/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/MINUTE_5/H5/MD_CHINA_COMMODITY_5MIN.h5')

df5_filtered = df5_all[df5_all.index.get_level_values('dt').time == pd.to_datetime('14:55').time()]
df5_filtered = df5_filtered.reset_index()
df5_filtered['dt'] = pd.to_datetime(df5_filtered['dt'].dt.date)
df5_filtered['Ticker'] = df5_filtered['Ticker'].apply(lambda x:x.replace('.ZCE', '.CZC'))
df5_filtered = df5_filtered.set_index(['dt', 'Ticker']).rename(columns = {'twap':'final5_twap'})

df = df.join(df5_filtered, how = 'left')

df = df.reset_index().rename(columns = {'Ticker':'wind_code', 'category':'Ticker'}).set_index(['dt', 'Ticker'])

IO.pd_hdf5_writer(df, '/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY2.h5', dataset='MD_MAIN_CHINA_COMMODITY_DAILY2', data_columns=['dt', 'Ticker'])