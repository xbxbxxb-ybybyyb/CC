import pandas as pd

if __name__ == '__main__':
    factor_x = '/dfs/group/800466/intern/wyb/X.pkl'
    factor_x_os = '/dfs/group/800466/intern/wyb/X_os.pkl'
    price_y = '/dfs/group/800466/intern/wyb/y.pkl'
    price_y_os = '/dfs/group/800466/intern/wyb/y_os.pkl'
    X = pd.read_pickle(factor_x)
    y = pd.read_pickle(price_y)
    X_os = pd.read_pickle(factor_x_os)
    y_os = pd.read_pickle(price_y_os)
    X_all = pd.concat([X, X_os])
    y_all = pd.concat([y, y_os])
    X_17_21 = X[(X.index.year >=2017) &(X.index.year <=2021)]
    y_17_21 = y[(y.index.year >=2017) &(y.index.year <=2021)]
    X_17_21.to_pickle('/dfs/group/800466/intern/wyb/17_21_X.pkl')
    y_17_21.to_pickle('/dfs/group/800466/intern/wyb/17_21_y.pkl')
    X_2022 = X[X.index.year==2022]
    y_2022 = y[y.index.year==2022]
    X_2022.to_pickle('/dfs/group/800466/intern/wyb/22_X.pkl')
    y_2022.to_pickle('/dfs/group/800466/intern/wyb/22_y.pkl')

    X_17_22 = X
    y_17_22 = y
    X_17_22.to_pickle('/dfs/group/800466/intern/wyb/17_22_X.pkl')
    y_17_22.to_pickle('/dfs/group/800466/intern/wyb/17_22_y.pkl')
    X_2023 = X_os[X_os.index.year==2023]
    y_2023 = y_os[y_os.index.year==2023]
    X_2023.to_pickle('/dfs/group/800466/intern/wyb/23_X.pkl')
    y_2023.to_pickle('/dfs/group/800466/intern/wyb/23_y.pkl')

    X_17_23 = X_all[(X_all.index.year>=2017) & (X_all.index.year <=2023)]
    y_17_23 = y_all[(y_all.index.year>=2017) & (y_all.index.year <=2023)]
    X_17_23.to_pickle('/dfs/group/800466/intern/wyb/17_23_X.pkl')
    y_17_23.to_pickle('/dfs/group/800466/intern/wyb/17_23_y.pkl')
    X_24 = X_all[(X_all.index.year>=2024) & (X_all.index.year <=2025)]
    y_24 = y_all[(y_all.index.year>=2024) & (y_all.index.year <=2025)]

    X_24.to_pickle('/dfs/group/800466/intern/wyb/24_X.pkl')
    y_24.to_pickle('/dfs/group/800466/intern/wyb/24_y.pkl')
    X_17_23.to_pickle('/dfs/group/800466/intern/wyb/17_23_X.pkl')
    y_17_23.to_pickle('/dfs/group/800466/intern/wyb/17_23_y.pkl')

    X_total = X_all[(X_all.index.year >= 2015) & (X_all.index.year <= 2027)]
    y_total = y_all[(y_all.index.year >= 2015) & (y_all.index.year <= 2027)]

    X_total.to_pickle('/dfs/group/800466/intern/wyb/X.pkl')
    y_total.to_pickle('/dfs/group/800466/intern/wyb/y.pkl')