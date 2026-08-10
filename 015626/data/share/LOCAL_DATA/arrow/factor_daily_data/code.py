pathlist = glob.glob('/data/user/015626/data/share/LOCAL_DATA/arrow/factor_daily_data/*/*.h5')

def get_r(path):
    fac = pd.read_hdf(path).unstack().shift().stack()
    factor_name = path.split('/')[-1][:-3]
    return {factor_name : fac[factor_name].replace([np.inf, -np.inf], np.nan).corr(ylabel)}
with Pool(24) as pool:
    rlist = pool.map(get_r, pathlist)

pd.concat([abs(pd.Series(x)) for x in rlist]).sort_values(ascending = False).to_csv('/data/user/015626/data/share/LOCAL_DATA/arrow/factor_daily_data/abs_ic.csv')