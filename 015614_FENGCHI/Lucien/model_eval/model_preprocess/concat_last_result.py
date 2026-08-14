# coding: utf-8
# Author：fengchi863
# Date ：2022/12/1 14:33

import pandas as pd

period3_root_path = '/data/group/800463/fengc/for_wj/20221126_period3_Europa fac_20221116_FSV8_all_pct_graded/'
lgb_period3_test_fpath = period3_root_path + '20201001~20210630_lgbRegModel_v1.csv'
lgb_period3_fit_fpath = period3_root_path + '20210701~20211231_lgbRegModel_v1.csv'
lr_period3_test_fpath = period3_root_path + '20201001~20210630_lrRegModel_v1.csv'
lr_period3_fit_fpath = period3_root_path + '20210701~20211231_lrRegModel_v1.csv'

lgb_test = pd.read_csv(lgb_period3_test_fpath, index_col=0)
lgb_fit = pd.read_csv(lgb_period3_fit_fpath, index_col=0)
part1 = lgb_test.query('datelist >= 20200401 & datelist <= 20200630')
part2 = lgb_fit.query('datelist >= 20200701')
lgb_all = pd.concat([part1, part2], axis=0)

lr_test = pd.read_csv(lr_period3_test_fpath, index_col=0)
lr_fit = pd.read_csv(lr_period3_fit_fpath, index_col=0)
part1 = lr_test.query('datelist >= 20200401 & datelist <= 20200630')
part2 = lr_fit.query('datelist >= 20200701')
lr_all = pd.concat([part1, part2], axis=0)

from LucienUtil.FileUtil import FileUtil
FileUtil.save_df2csv(lgb_all, '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/', '20210401~20211231_LgbRegModel_old.csv')
FileUtil.save_df2csv(lr_all, '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/', '20210401~20211231_LrRegModel_old.csv')
