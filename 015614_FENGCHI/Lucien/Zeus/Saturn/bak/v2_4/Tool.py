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


def get_interval_data(y_raw, y_prob, y_clf, date_config):
    train_start_date = date_config['train_start_date']
    train_end_date = date_config['train_end_date']
    valid_start_date = date_config['valid_start_date']
    valid_end_date = date_config['valid_end_date']
    test_start_date = date_config['test_start_date']
    test_end_date = date_config['test_end_date']

    y_raw['trade_date'] = y_raw.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
    y_prob['trade_date'] = y_prob.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
    y_clf['trade_date'] = y_clf.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

    # 由于是按照样本进行切分，比如把在一天的给切分了，那么下面按照日期分就不能分平了
    y_raw = y_raw.reindex(y_prob.index)

    y_train = y_raw.query(f'trade_date >= {train_start_date} & trade_date <= {train_end_date}')
    y_valid = y_raw.query(f'trade_date >= {valid_start_date} & trade_date <= {valid_end_date}')
    y_test = y_raw.query(f'trade_date >= {test_start_date} & trade_date <= {test_end_date}')

    y_train_prob = y_prob.query(f'trade_date >= {train_start_date} & trade_date <= {train_end_date}')
    y_valid_prob = y_prob.query(f'trade_date >= {valid_start_date} & trade_date <= {valid_end_date}')
    y_test_prob = y_prob.query(f'trade_date >= {test_start_date} & trade_date <= {test_end_date}')

    y_train_clf = y_clf.query(f'trade_date >= {train_start_date} & trade_date <= {train_end_date}')
    y_valid_clf = y_clf.query(f'trade_date >= {valid_start_date} & trade_date <= {valid_end_date}')
    y_test_clf = y_clf.query(f'trade_date >= {test_start_date} & trade_date <= {test_end_date}')

    y_train = y_train.drop('trade_date', axis=1)
    y_valid = y_valid.drop('trade_date', axis=1)
    y_test = y_test.drop('trade_date', axis=1)
    y_train_prob = y_train_prob.drop('trade_date', axis=1)
    y_valid_prob = y_valid_prob.drop('trade_date', axis=1)
    y_test_prob = y_test_prob.drop('trade_date', axis=1)
    y_train_clf = y_train_clf.drop('trade_date', axis=1)
    y_valid_clf = y_valid_clf.drop('trade_date', axis=1)
    y_test_clf = y_test_clf.drop('trade_date', axis=1)

    return y_train, y_valid, y_test, y_train_prob, y_valid_prob, y_test_prob, y_train_clf, y_valid_clf, y_test_clf