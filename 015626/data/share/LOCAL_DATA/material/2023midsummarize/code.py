df_daily= IO.read_data(alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5')
df_daily['num'] = [x[4:6] for x in df_daily.index.get_level_values(1).tolist()] 
season = df_daily[df_daily['num'].isin(['03','06','09','12']) & (df_daily['expiration_days'] >=3) ]

basis_list = []
for ticker in ['IC.CFE','IF.CFE','IH.CFE','IM.CFE']:
    tseason = season[season.prod_id == ticker].sort_index()

    df00 = tseason.groupby('dt').apply(lambda x: x.iloc[0:1, :]).reset_index(level=0, drop=True).reset_index(level=1)
    df01 = tseason.groupby('dt').apply(lambda x: x.iloc[1:2, :]).reset_index(level=0, drop=True).reset_index(level=1)


    basis = ((df01['close'] / df00['close'] -1 ) * 4).to_frame()
    basis.columns = [ticker[:2]]
    basis_list.append(basis)

df_basis = pd.concat(basis_list, axis = 1)