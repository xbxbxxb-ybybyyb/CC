from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import pandas as pd

# factor_df = pd.read_hdf('/data/group/800319/capemmmmm.h5', 'capm')
MA_period_list = [2, 3, 4]
tag = 'RelativeMA_%s' % ('_'.join(list(map(str, MA_period_list))))
factor_df = pd.read_hdf('%s/temp_daily_by_lzc/RelativeMA/result/%s.h5' % (root_path, tag), tag)
###########################
n = 8
Lag = 3
factor_df_daily = calc_Factor_(n,Lag)
#pd.read_hdf('%s/temp_daily_by_lzc/DailyRegRet/DailyRegRet_n%d_Lag%d.h5' % (root_path, n, Lag), 'DailyRegRet_n%d_Lag%d' % (n, Lag))

factor_df1 = factor_df*factor_df_daily
tag = tag+'DailyRegRet_n%d_Lag%d' % (n, Lag)+'_std'
#################################
print(factor_df1.shape)
factor_test = FactorBackTest(factor_df1)
factor_test.evaluation(30)

factor_test.result_output(fileroot='%s/temp_daily_by_lzc/RelativeMA/result/' % root_path,filename=tag)
print(factor_test.evaluation_result)
if not os.path.exists('%s/temp_daily_by_lzc/RelativeMA/result/fig_%s' % (root_path,tag)):
    os.mkdir('%s/temp_daily_by_lzc/RelativeMA/result/fig_%s' % (root_path,tag))
factor_test.check_part_signal(80,'%s/temp_daily_by_lzc/RelativeMA/result/fig_%s/' % (root_path,tag),18)
print(factor_test.running_time)

