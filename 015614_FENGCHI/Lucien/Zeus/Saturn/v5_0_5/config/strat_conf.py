# coding: utf-8
# Author：fengchi863
# Date ：2023/11/20 15:02

STRATEGY_NAME = 'Saturn'
STRATEGY_VERSION = 'v5_0_5'
PERIOD = 'period1'

bt_out_path = '/data/user/015614/Zeus/backtest/'
pred_out_path = '/data/user/015614/Zeus/pred/'
log_path = '/data/user/015614/Zeus/logs/'
factor_path = '/data/user/015614/Zeus/factor_list/'
factor_select_path = '/data/user/015614/Zeus/factor_select/'
model_save_path = '/data/user/015614/Zeus/pred/'

DATE_CONFIG = {
    # 'period1': dict(train_start_date=20160101, train_end_date=20191231, valid_start_date=20200101, valid_end_date=20200630,
    #                 test_start_date=20200701, test_end_date=20201231, fit_start_date=20210101, fit_end_date=20211231),
    'period1': dict(train_start_date=20160101, train_end_date=20191231, valid_start_date=20200101, valid_end_date=20200630,
                    test_start_date=20200701, test_end_date=20201231, fit_start_date=20201201, fit_end_date=20201231),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20190831, valid_start_date=20190901, valid_end_date=20201231,
                    test_start_date=20200701, test_end_date=20201231, fit_start_date=20201201, fit_end_date=20201231),

    # 'period2': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201231,
    #                     test_start_date=20210101, test_end_date=20210630, fit_start_date=20210701, fit_end_date=20220630),
    'period2': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201231,
                    test_start_date=20210101, test_end_date=20210630, fit_start_date=20210601, fit_end_date=20210630),
    'period2_roll': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210630,
                    test_start_date=20210101, test_end_date=20210630, fit_start_date=20210601, fit_end_date=20210630),

    # 'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210630,
    #                         test_start_date=20210701, test_end_date=20211231, fit_start_date=20220101, fit_end_date=20221231),
    'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210630,
                        test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),
    'period3_roll': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20211231,
                        test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),

    # 'period4': dict(train_start_date=20160101, train_end_date=20210630, valid_start_date=20210701, valid_end_date=20211231,
    #                         test_start_date=20220101, test_end_date=20220630, fit_start_date=20220701, fit_end_date=20230630),
    'period4': dict(train_start_date=20160101, train_end_date=20210630, valid_start_date=20210701, valid_end_date=20211231,
                        test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),
    'period4_roll': dict(train_start_date=20160101, train_end_date=20210630, valid_start_date=20210701, valid_end_date=20220630,
                        test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),

    # 'period5': dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20220101, valid_end_date=20220630,
    #                      test_start_date=20220701, test_end_date=20221231, fit_start_date=20230101, fit_end_date=20231231),
    'period5': dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20220101, valid_end_date=20220630,
                     test_start_date=20220701, test_end_date=20221231, fit_start_date=20221201, fit_end_date=20221231),
    'period5_roll': dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20220101, valid_end_date=20220701,
                     test_start_date=20220701, test_end_date=20221231, fit_start_date=20221201, fit_end_date=20221231),

    # 'period6': dict(train_start_date=20160101, train_end_date=20220630, valid_start_date=20220701, valid_end_date=20221231,
    #                      test_start_date=20230101, test_end_date=20230630, fit_start_date=20230701, fit_end_date=20240630),
    'period6': dict(train_start_date=20160101, train_end_date=20220630, valid_start_date=20220701, valid_end_date=20221231,
                     test_start_date=20230101, test_end_date=20230630, fit_start_date=20230601, fit_end_date=20230630),
    'period6_roll': dict(train_start_date=20160101, train_end_date=20220630, valid_start_date=20220701, valid_end_date=20230630,
                     test_start_date=20230101, test_end_date=20230630, fit_start_date=20230601, fit_end_date=20230630),

    # 'period7': dict(train_start_date=20160101, train_end_date=20221231, valid_start_date=20230101, valid_end_date=20230630,
    #                      test_start_date=20230701, test_end_date=20231231, fit_start_date=20240101, fit_end_date=20241231),
    'period7': dict(train_start_date=20160101, train_end_date=20221231, valid_start_date=20230101, valid_end_date=20230630,
                     test_start_date=20230701, test_end_date=20231231, fit_start_date=20231201, fit_end_date=20231231),
    'period7_roll': dict(train_start_date=20160101, train_end_date=20221231, valid_start_date=20230101, valid_end_date=20231231,
                     test_start_date=20230701, test_end_date=20231231, fit_start_date=20231201, fit_end_date=20231231),

    # 'period8': dict(train_start_date=20160101, train_end_date=20230630, valid_start_date=20230701, valid_end_date=20231231,
    #                      test_start_date=20240101, test_end_date=20240630, fit_start_date=20240701, fit_end_date=20250630),
    'period8': dict(train_start_date=20160101, train_end_date=20230630, valid_start_date=20230701, valid_end_date=20231231,
                     test_start_date=20240101, test_end_date=20240630, fit_start_date=20240601, fit_end_date=20240630),
    'period8_roll': dict(train_start_date=20160101, train_end_date=20230630, valid_start_date=20230701, valid_end_date=20240630,
                     test_start_date=20240101, test_end_date=20240630, fit_start_date=20240601, fit_end_date=20240630),
}