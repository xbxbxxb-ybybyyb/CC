import pandas as pd
def factor_to_signal(path, in_t = 0.8, out_t = 0.5):
    df = pd.read_hdf(path)
    factorname = df.columns[0]

    condition1 = df[factorname] >= in_t
    condition2 = df[factorname].shift(1) < in_t
    df.loc[condition1 & condition2, 'signal_long'] = 1

    condition1 = df[factorname] < out_t
    condition2 = df[factorname].shift(1) >= out_t
    df.loc[condition1 & condition2, 'signal_long'] = 0

    condition1 = df[factorname] <= (-1 * in_t)
    condition2 = df[factorname].shift(1) > (-1 * in_t)
    df.loc[condition1 & condition2, 'signal_short'] = -1

    condition1 = df[factorname] > (-1 * out_t)
    condition2 = df[factorname].shift(1) <= (-1 * out_t)
    df.loc[condition1 & condition2, 'signal_short'] = 0

    df['signal'] = df[['signal_long', 'signal_short']].sum(axis = 1, min_count = 1, skipna = True)
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]

    df['signal'] = temp['signal']
    df['signal'] = df['signal'].fillna(method = 'ffill')
    df['signal'] = df['signal'].fillna(value = 0)

    df = df[['signal']]
    df.columns = [factorname]
    return df