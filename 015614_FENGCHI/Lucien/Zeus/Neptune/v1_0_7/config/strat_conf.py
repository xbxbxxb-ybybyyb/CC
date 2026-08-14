# coding: utf-8
# Author：fengchi863
# Date ：2023/11/20 15:02

STRATEGY_NAME = 'Neptune'
STRATEGY_VERSION = 'v1_0_7'
PERIOD = 'period1'

bt_out_path = '/data/user/015614/Zeus/backtest/'
pred_out_path = '/data/user/015614/Zeus/pred/'
log_path = '/data/user/015614/Zeus/logs/'
factor_path = '/data/user/015614/Zeus/factor_list/'
factor_select_path = '/data/user/015614/Zeus/factor_select/'
model_save_path = '/data/user/015614/Zeus/pred/'

DATE_CONFIG = {
    'period1_fit': dict(train_start_date=20170110, train_end_date=20190630,
                    test_start_date=20190701, test_end_date=20191231, fit_start_date=20200701, fit_end_date=20201231),
    'period1': dict(train_start_date=20170110, train_end_date=20190630,
                    test_start_date=20190701, test_end_date=20191231, fit_start_date=20191201, fit_end_date=20191231),
    'period1_roll': dict(train_start_date=20170110, train_end_date=20191231,
                    test_start_date=20190701, test_end_date=20191231, fit_start_date=20191201, fit_end_date=20191231),

    'period2_fit': dict(train_start_date=20170110, train_end_date=20191231,
                        test_start_date=20200101, test_end_date=20200630, fit_start_date=20200701, fit_end_date=20210630),
    'period2': dict(train_start_date=20170110, train_end_date=20191231,
                    test_start_date=20200101, test_end_date=20200630, fit_start_date=20200601, fit_end_date=20200630),
    'period2_roll': dict(train_start_date=20170110, train_end_date=20200630,
                    test_start_date=20200101, test_end_date=20200630, fit_start_date=20200601, fit_end_date=20200630),

    'period3_fit': dict(train_start_date=20170110, train_end_date=20200630,
                        test_start_date=20200701, test_end_date=20201231, fit_start_date=20210101, fit_end_date=20211231),
    'period3': dict(train_start_date=20170110, train_end_date=20200630,
                        test_start_date=20200701, test_end_date=20201231, fit_start_date=20201201, fit_end_date=20201231),
    'period3_roll': dict(train_start_date=20170110, train_end_date=20201231,
                        test_start_date=20200701, test_end_date=20201231, fit_start_date=20201201, fit_end_date=20201231),

    'period4_fit': dict(train_start_date=20170110, train_end_date=20201231,
                        test_start_date=20210101, test_end_date=20210630, fit_start_date=20210701, fit_end_date=20220630),
    'period4': dict(train_start_date=20170110, train_end_date=20201231,
                        test_start_date=20210101, test_end_date=20210630, fit_start_date=20210601, fit_end_date=20210630),
    'period4_roll': dict(train_start_date=20170110, train_end_date=20210630,
                        test_start_date=20210101, test_end_date=20210630, fit_start_date=20210601, fit_end_date=20210630),

    'period5_fit': dict(train_start_date=20170110, train_end_date=20210630,
                     test_start_date=20210701, test_end_date=20211231, fit_start_date=20220101, fit_end_date=20221231),
    'period5': dict(train_start_date=20170110, train_end_date=20210630,
                     test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),
    'period5_roll': dict(train_start_date=20170110, train_end_date=20211231,
                     test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),

    'period6_fit': dict(train_start_date=20170110, train_end_date=20211231,
                     test_start_date=20220101, test_end_date=20220630, fit_start_date=20220701, fit_end_date=20230630),
    'period6': dict(train_start_date=20170110, train_end_date=20211231,
                     test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),
    'period6_roll': dict(train_start_date=20170110, train_end_date=20220630,
                     test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),

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