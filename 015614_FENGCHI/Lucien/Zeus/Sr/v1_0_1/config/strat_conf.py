# coding: utf-8
# Author：fengchi863
# Date ：2023/11/20 15:02

STRATEGY_NAME = 'Sr'
STRATEGY_VERSION = 'v1_0_1'
PERIOD = 'period1'

bt_out_path = '/data/user/015614/Zeus/backtest/'
pred_out_path = '/data/user/015614/Zeus/pred/'
log_path = '/data/user/015614/Zeus/logs/'
factor_path = '/data/user/015614/Zeus/factor_list/'
factor_select_path = '/data/user/015614/Zeus/factor_select/'
model_save_path = '/data/user/015614/Zeus/pred/'

DATE_CONFIG = {
    'period1_fit': dict(train_start_date=20160101, train_end_date=20200630,
                    test_start_date=20200701, test_end_date=20201231, fit_start_date=20210101, fit_end_date=20211231),
    'period1': dict(train_start_date=20160101, train_end_date=20200630,
                    test_start_date=20200701, test_end_date=20201231, fit_start_date=20201201, fit_end_date=20201231),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20201231,
                    test_start_date=20200701, test_end_date=20201231, fit_start_date=20201201, fit_end_date=20201231),

    'period2_fit': dict(train_start_date=20160101, train_end_date=20201231,
                    test_start_date=20210101, test_end_date=20210630, fit_start_date=20210701, fit_end_date=20220630),
    'period2': dict(train_start_date=20160101, train_end_date=20201231,
                    test_start_date=20210101, test_end_date=20210630, fit_start_date=20210601, fit_end_date=20210630),
    'period2_roll': dict(train_start_date=20160101, train_end_date=20210630,
                    test_start_date=20210101, test_end_date=20210630, fit_start_date=20210601, fit_end_date=20210630),

    'period3_fit': dict(train_start_date=20160101, train_end_date=20210630,
                        test_start_date=20210701, test_end_date=20211231, fit_start_date=20220101, fit_end_date=20221231),
    'period3': dict(train_start_date=20160101, train_end_date=20210630,
                        test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),
    'period3_roll': dict(train_start_date=20160101, train_end_date=20211231,
                        test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),

    'period4_fit': dict(train_start_date=20160101, train_end_date=20211231,
                        test_start_date=20220101, test_end_date=20220630, fit_start_date=20220701, fit_end_date=20230630),
    'period4': dict(train_start_date=20160101, train_end_date=20211231,
                        test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),
    'period4_roll': dict(train_start_date=20160101, train_end_date=20220630,
                        test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),

    'period5_fit': dict(train_start_date=20160101, train_end_date=20220331,
                     test_start_date=20220401, test_end_date=20220930, fit_start_date=20221001, fit_end_date=20230930),
    'period5': dict(train_start_date=20160101, train_end_date=20220331,
                     test_start_date=20220401, test_end_date=20220930, fit_start_date=20220901, fit_end_date=20220930),
    'period5_roll': dict(train_start_date=20160101, train_end_date=20220930,
                     test_start_date=20220401, test_end_date=20220930, fit_start_date=20220901, fit_end_date=20220930),

    'period6_fit': dict(train_start_date=20160101, train_end_date=20220930,
                     test_start_date=20221001, test_end_date=20230331, fit_start_date=20230401, fit_end_date=20240331),
    'period6': dict(train_start_date=20160101, train_end_date=20220930,
                     test_start_date=20221001, test_end_date=20230331, fit_start_date=20230301, fit_end_date=20230331),
    'period6_roll': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20221001, test_end_date=20230331, fit_start_date=20230301, fit_end_date=20230331),

    'period7_fit': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20230401, test_end_date=20230930, fit_start_date=20230901, fit_end_date=20240930),
    'period7': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20230401, test_end_date=20230930, fit_start_date=20230901, fit_end_date=20230930),
    'period7_roll': dict(train_start_date=20160101, train_end_date=20230930,
                     test_start_date=20230401, test_end_date=20230930, fit_start_date=20230901, fit_end_date=20230930),

    'period8_fit': dict(train_start_date=20160101, train_end_date=20230930,
                     test_start_date=20231001, test_end_date=20240331, fit_start_date=20240401, fit_end_date=20250331),
    'period8': dict(train_start_date=20160101, train_end_date=20230930,
                     test_start_date=20231001, test_end_date=20240331, fit_start_date=20240301, fit_end_date=20240331),
    'period8_roll': dict(train_start_date=20160101, train_end_date=20240331,
                     test_start_date=20231001, test_end_date=20240331, fit_start_date=20240301, fit_end_date=20240331),

    'period9_fit': dict(train_start_date=20160101, train_end_date=20240331,
                     test_start_date=20240401, test_end_date=20240930, fit_start_date=20241001, fit_end_date=20250930),
    'period9': dict(train_start_date=20160101, train_end_date=20240331,
                     test_start_date=20240401, test_end_date=20240930, fit_start_date=20240901, fit_end_date=20240930),
    'period9_roll': dict(train_start_date=20160101, train_end_date=20240930,
                     test_start_date=20240401, test_end_date=20240930, fit_start_date=20240901, fit_end_date=20240930),
}