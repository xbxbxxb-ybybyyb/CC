import pandas as pd

if __name__ == '__main__':
    price_y = '/dfs/group/800466/intern/TWAP_SPOT.h5'
    y = pd.read_hdf(price_y).xs('IF.CFE',level='Ticker')
    y_17_21 = y[(y.index.year >= 2015) &(y.index.year <=2027)]
    y_17_21.to_pickle('/dfs/group/800466/intern/wyb/y_index.pkl')

    #X_17_21.to_pickle('/dfs/group/800466/intern/wyb/17_21_X.pkl')
    y_17_21.to_pickle('/dfs/group/800466/intern/wyb/17_21_y_index.pkl')


    y_17_22 = y[(y.index.year >= 2017) &(y.index.year <=2022)]
    y_17_22.to_pickle('/dfs/group/800466/intern/wyb/17_22_y_index.pkl')


    y_17_23 = y[(y.index.year >= 2017) & (y.index.year <=2023)]

    y_17_23.to_pickle('/dfs/group/800466/intern/wyb/17_23_y_index.pkl')

