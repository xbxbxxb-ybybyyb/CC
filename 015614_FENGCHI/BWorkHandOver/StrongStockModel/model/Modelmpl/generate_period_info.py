# @Time : 2021/2/18 9:03
# @Author : Zhichen Lu
# @File : generate_period_info.py
from dataApi.tradeDate import get_date_range


def get_rolling_index(start,end, period=10, period_predict=10):
    rolling_train_test_idx_list = []
    date_list = get_date_range(start,end)
    if (len(date_list) - period) % period_predict == 0:
        length = (len(date_list) - period) // period_predict
    else:
        length = (len(date_list) - period) // period_predict + 1
    for idx in range(length):
        train_start_idx = idx * period_predict
        train_end_idx = idx * period_predict + period - 1
        if idx == (len(date_list) - period) // period_predict:
            test_start_idx = idx * period_predict + period
            test_end_idx = len(date_list) - 1
        else:
            test_start_idx = idx * period_predict + period
            test_end_idx = test_start_idx + period_predict - 1
        train_start_date, train_end_date, test_start_date, test_end_date = [date_list[i] for i in
                                                                            [train_start_idx, train_end_idx,
                                                                             test_start_idx, test_end_idx]]
        rolling_train_test_idx_list.append(
            (idx, (train_start_date, train_end_date, test_start_date, test_end_date)))
    return rolling_train_test_idx_list

period_info = get_rolling_index(20150309,20210319,200,10)
period_info