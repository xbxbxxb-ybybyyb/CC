# coding: utf-8
# Author：fengchi863
# Date ：2022/7/16 19:47
import multiprocessing

def multiprocess(lines, func, iterable, *args):

    pool = multiprocessing.Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // lines
    remainder = len(iterable) % lines
    iter_start = 0
    for j in range(lines):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder -= 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter, ) + args)
        iter_start = iter_end
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async


def get_interval_data(y_raw, y_prob, y_clf, date_config, len_train):
    train_start_date = date_config['train_start_date']
    train_end_date = date_config['train_end_date']
    valid_start_date = date_config['valid_start_date']
    valid_end_date = date_config['valid_end_date']
    test_start_date = date_config['test_start_date']
    test_end_date = date_config['test_end_date']

    y_train = y_raw.iloc[len_train + train_start_date:train_end_date]
    y_valid = y_raw.iloc[valid_start_date:valid_end_date]
    y_test = y_raw.iloc[test_start_date:test_end_date]

    y_train_prob = y_prob.iloc[train_start_date:train_end_date - len_train]
    y_valid_prob = y_prob.iloc[valid_start_date - len_train:valid_end_date - len_train]
    y_test_prob = y_prob.iloc[test_start_date - len_train:test_end_date - len_train]

    y_train_clf = y_clf.iloc[train_start_date:train_end_date - len_train]
    y_valid_clf = y_clf.iloc[valid_start_date - len_train:valid_end_date - len_train]
    y_test_clf = y_clf.iloc[test_start_date - len_train:test_end_date - len_train]

    return y_train, y_valid, y_test, y_train_prob, y_valid_prob, y_test_prob, y_train_clf, y_valid_clf, y_test_clf