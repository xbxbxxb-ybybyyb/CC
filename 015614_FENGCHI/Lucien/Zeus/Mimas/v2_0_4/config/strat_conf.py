# coding: utf-8
# Author：fengchi863
# Date ：2023/11/20 15:02

STRATEGY_NAME = 'Mimas'
STRATEGY_VERSION = 'v2_0_4'
PERIOD = 'period1'

bt_out_path = '/data/user/015614/Zeus/backtest/'
pred_out_path = '/data/user/015614/Zeus/pred/'
log_path = '/data/user/015614/Zeus/logs/'
factor_path = '/data/user/015614/Zeus/factor_list/'
factor_select_path = '/data/user/015614/Zeus/factor_select/'
model_save_path = '/data/user/015614/Zeus/pred/'

DATE_CONFIG = {
    'period1_fit': dict(train_start_date=20160101, train_end_date=20200930,
                    test_start_date=20201001, test_end_date=20210331, fit_start_date=20210401, fit_end_date=20220331),
    'period1': dict(train_start_date=20160101, train_end_date=20200930,
                    test_start_date=20201001, test_end_date=20210331, fit_start_date=20210301, fit_end_date=20210331),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20210331,
                    test_start_date=20201001, test_end_date=20210331, fit_start_date=20210301, fit_end_date=20210331),

    'period2_fit': dict(train_start_date=20160101, train_end_date=20210331,
                    test_start_date=20210401, test_end_date=20210930, fit_start_date=20211001, fit_end_date=20220930),
    'period2': dict(train_start_date=20160101, train_end_date=20210331,
                    test_start_date=20210401, test_end_date=20210930, fit_start_date=20210901, fit_end_date=20210930),
    'period2_roll': dict(train_start_date=20160101, train_end_date=20210930,
                    test_start_date=20210401, test_end_date=20210930, fit_start_date=20210901, fit_end_date=20210930),

    'period3_fit': dict(train_start_date=20160101, train_end_date=20210930,
                        test_start_date=20211001, test_end_date=20220331, fit_start_date=20220401, fit_end_date=20230331),
    'period3': dict(train_start_date=20160101, train_end_date=20210930,
                        test_start_date=20211001, test_end_date=20220331, fit_start_date=20220301, fit_end_date=20220331),
    'period3_roll': dict(train_start_date=20160101, train_end_date=20220331,
                        test_start_date=20211001, test_end_date=20220331, fit_start_date=20220301, fit_end_date=20220331),

    'period4_fit': dict(train_start_date=20160101, train_end_date=20220331,
                        test_start_date=20220401, test_end_date=20220930, fit_start_date=20221001, fit_end_date=20230930),
    'period4': dict(train_start_date=20160101, train_end_date=20220331,
                        test_start_date=20220401, test_end_date=20220930, fit_start_date=20220901, fit_end_date=20220930),
    'period4_roll': dict(train_start_date=20160101, train_end_date=20210930,
                        test_start_date=20220401, test_end_date=20220930, fit_start_date=20220901, fit_end_date=20220930),

    'period5_fit': dict(train_start_date=20160101, train_end_date=20220930,
                     test_start_date=20221001, test_end_date=20230331, fit_start_date=20230401, fit_end_date=20240331),
    'period5': dict(train_start_date=20160101, train_end_date=20220930,
                     test_start_date=20221001, test_end_date=20230331, fit_start_date=20230301, fit_end_date=20230331),
    'period5_roll': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20221001, test_end_date=20230331, fit_start_date=20230301, fit_end_date=20230331),

    'period6_fit': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20230401, test_end_date=20230930, fit_start_date=20231001, fit_end_date=20240930),
    'period6': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20230401, test_end_date=20230930, fit_start_date=20230901, fit_end_date=20230930),
    'period6_roll': dict(train_start_date=20160101, train_end_date=20230331,
                     test_start_date=20230401, test_end_date=20230930, fit_start_date=20230901, fit_end_date=20230930),

    'period7_fit': dict(train_start_date=20170110, train_end_date=20221231,
                         test_start_date=20230701, test_end_date=20231231, fit_start_date=20240101, fit_end_date=20241231),
    'period7': dict(train_start_date=20170110, train_end_date=20221231,
                     test_start_date=20230701, test_end_date=20231231, fit_start_date=20231201, fit_end_date=20231231),
    'period7_roll': dict(train_start_date=20170110, train_end_date=20221231,
                     test_start_date=20230701, test_end_date=20231231, fit_start_date=20231201, fit_end_date=20231231),

    'period8_fit': dict(train_start_date=20170110, train_end_date=20230630,
                         test_start_date=20240101, test_end_date=20240630, fit_start_date=20240701, fit_end_date=20250630),
    'period8': dict(train_start_date=20170110, train_end_date=20230630,
                     test_start_date=20240101, test_end_date=20240630, fit_start_date=20240601, fit_end_date=20240630),
    'period8_roll': dict(train_start_date=20170110, train_end_date=20230630,
                     test_start_date=20240101, test_end_date=20240630, fit_start_date=20240601, fit_end_date=20240630),
}