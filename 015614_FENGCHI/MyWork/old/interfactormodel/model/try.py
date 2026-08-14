if __name__ == '__main__':
    from scipy.stats import norm, kurtosis, skew
    import time
    t = time.time()
    #factor_diversity = (bottleneck.nanrankdata(factor, axis=1) % 1 == 0).sum(axis=1) / code_valid_num[d]
    factor_pool_day = factor_pool[date_list.index(date)]
    factor_multi_period_weight_day = factor_multi_period_weight[model_date_list.index(date)]
    factor = np.full((factor_num, code_num), 0.)
    factor[factor_pool_day] = np.load('%s%s %s.npy' % (middle_address, 'factor_standardize', date))
    compound_factor = factor_multi_period_weight_day.dot(factor)


    time.time() - t

    STOCK_POOL = Array('d', stock_pool.flatten(), lock=False)
    FACTOR = Array('d', date_num * factor_num * code_num, lock=False)
    FACTOR_STATS = Array('d', date_num * factor_num * 4, lock=False)

    del stock_pool


    def _load_factor(sub_list, line=0):
        global FACTOR, date_list, factor_list, factor_address, code_list, factor_num, code_num
        for date in tqdm(sub_list, desc=line):
            day = date_list.index(date)
            FACTOR[day * factor_num * code_num: (day + 1) * factor_num * code_num] = load_factor(
                date, factor_list, factor_address, code_list).values.flatten()


    def corrcoef(X, y=None, axis=-1):

        X = factor
        X = X.swapaxes(0, axis)
        if y == None:
            X_mean = np.nanmean(X, axis=0)
            X_std = np.nanstd(X, ddof=1, axis=0)
            X = (X - X_mean) / X_std
            X = np.ma.masked_invalid(X)
            corr = np.ma.dot(X.T, X)
            corr.set_fill_value(np.nan)
            return corr.data
        else:
            y = np.atleast_2d(y).swapaxes(0, axis)
            X[np.all(np.isnan(y), axis=1)] = np.nan
            X_mean = np.nanmean(X, axis=0)
            X_std = np.nanstd(X, ddof=1, axis=0)
            X = (X - X_mean) / X_std
            X = np.ma.masked_invalid(X)

            y_mean = np.nanmean(y, axis=0)
            y_std = np.nanstd(y, ddof=1, axis=0)
            y = (y - y_mean) / y_std
            y = np.ma.masked_invalid(y)
            corr = np.ma.dot(X.T, y)
            corr.set_fill_value(np.nan)
            return corr.data


    multiprocess(20, _load_factor, date_list)

    factor_skew = skew(factor, axis=1, nan_policy='omit')
    factor_kurt = kurtosis(factor, axis=1, nan_policy='omit')

    for date in date_list:
        np.save(middle_address + 'factor_pool ' + str(date),
                (np.load('%s%s %s.npy' % (middle_address, 'factor_complete', date)) > factor_complete_limit) &
                (np.load('%s%s %s.npy' % (middle_address, 'factor_diversity', date)) > factor_diversity_limit))


        (((factor_pool_select & (active_mean_net > 0))[4].sum(axis=1) / factor_pool.sum(axis=1)[select_days - 1:])).mean()

        MI_roll = factor_direction_merge(MI_roll, factor_pos, factor_neg)
        group_MI_roll = factor_direction_merge(group_MI_roll, factor_pos, factor_neg)

    aaa = np.array([[3., 7., 5., 2., 1.], [0., 3., 2., np.nan, 9.]])
    ara = (- aaa).argsort(axis=1)
    ana = np.isnan(aaa)

    bbb = np.random.rand(2, 5, 5)
    bbb[ana] = np.nan
    bbb.swapaxes(1, 2)[ana] = np.nan
    ccc = bbb[np.arange(bbb.shape[0])[:, None, None], ara[:, :, None], ara[:, None, :]]
    np.tri

    aaa = np.array([5, 3, 7, 1, 9])
    bbb = aaa.argsort()
    ccc = np.array([False, True, False, False, True])
    aaa[bbb][ccc] = 0