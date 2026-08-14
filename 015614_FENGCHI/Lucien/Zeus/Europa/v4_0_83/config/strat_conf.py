# coding: utf-8
# Author：fengchi863
# Date ：2023/11/20 15:02

STRATEGY_NAME = 'Europa'
STRATEGY_VERSION = 'v4_0_83'
PERIOD = 'period1'

bt_out_path = '/data/user/015614/Zeus/backtest/'
pred_out_path = '/data/user/015614/Zeus/pred/'
log_path = '/data/user/015614/Zeus/logs/'
factor_path = '/data/user/015614/Zeus/factor_list/'
factor_select_path = '/data/user/015614/Zeus/factor_select/'
model_save_path = '/data/user/015614/Zeus/pred/'

DATE_CONFIG = {
    # 'period1': dict(train_start_date=20160101, train_end_date=20190831, valid_start_date=20190901, valid_end_date=20200229,
    #                 test_start_date=20200301, test_end_date=20200831, fit_start_date=20200801, fit_end_date=20210831),
    'period1': dict(train_start_date=20160101, train_end_date=20190831, valid_start_date=20190901, valid_end_date=20200229,
                    test_start_date=20200301, test_end_date=20200831, fit_start_date=20200801, fit_end_date=20210831),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20190831, valid_start_date=20190901, valid_end_date=20200831,
                    test_start_date=20200301, test_end_date=20200831, fit_start_date=20200801, fit_end_date=20210831),

    # 'period2': dict(train_start_date=20160101, train_end_date=20200131, valid_start_date=20200201, valid_end_date=20200831,
    #                 test_start_date=20200901, test_end_date=20210228, fit_start_date=20210301, fit_end_date=20220228),
    'period2': dict(train_start_date=20160101, train_end_date=20200131, valid_start_date=20200201, valid_end_date=20200831,
                    test_start_date=20200901, test_end_date=20210228, fit_start_date=20210201, fit_end_date=20210228),
    'period2_roll': dict(train_start_date=20160101, train_end_date=20200131, valid_start_date=20200201, valid_end_date=20210228,
                     test_start_date=20200901, test_end_date=20210228, fit_start_date=20210201, fit_end_date=20210228),

    # 'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210228,
    #                 test_start_date=20210301, test_end_date=20210831, fit_start_date=20210901, fit_end_date=20220831),
    'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210228,
                        test_start_date=20210301, test_end_date=20210831, fit_start_date=20210801, fit_end_date=20210831),
    'period3_roll': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210831,
                         test_start_date=20210301, test_end_date=20210831, fit_start_date=20210801, fit_end_date=20210831),

    'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210831,
                    test_start_date=20210901, test_end_date=20220228, fit_start_date=20220301, fit_end_date=20230228),
    # 'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210831,
    #                     test_start_date=20210901, test_end_date=20220228, fit_start_date=20220201, fit_end_date=20220228),
    'period4_roll': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20220228,
                         test_start_date=20210901, test_end_date=20220228, fit_start_date=20220201, fit_end_date=20220228),

    # 'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20220228,
    #                 test_start_date=20220301, test_end_date=20220831, fit_start_date=20220901, fit_end_date=20230831),
    'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20220228,
                     test_start_date=20220301, test_end_date=20220831, fit_start_date=20220801, fit_end_date=20220831),
    'period5_roll': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20220831,
                     test_start_date=20220301, test_end_date=20220831, fit_start_date=20220801, fit_end_date=20220831),

    # 'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220831,
    #                 test_start_date=20220901, test_end_date=20230228, fit_start_date=20230301, fit_end_date=20240229),
    'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220831,
                     test_start_date=20220901, test_end_date=20230228, fit_start_date=20230201, fit_end_date=20230228),
    'period6_roll': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20230228,
                     test_start_date=20220901, test_end_date=20230228, fit_start_date=20230201, fit_end_date=20230228),

    # 'period7': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20230228,
    #                 test_start_date=20230301, test_end_date=20230831, fit_start_date=20230901, fit_end_date=20240831),
    'period7': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20230228,
                     test_start_date=20230301, test_end_date=20230831, fit_start_date=20230801, fit_end_date=20230831),
    'period7_roll': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20230831,
                     test_start_date=20230301, test_end_date=20230831, fit_start_date=20230801, fit_end_date=20230831),

    # 'period8': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20230831,
    #                 test_start_date=20230901, test_end_date=20240229, fit_start_date=20240301, fit_end_date=20250228),
    'period8': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20230831,
                     test_start_date=20230901, test_end_date=20240229, fit_start_date=20240201, fit_end_date=20240229),
    'period8_roll': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20240229,
                     test_start_date=20230901, test_end_date=20240229, fit_start_date=20240201, fit_end_date=20240229),
}