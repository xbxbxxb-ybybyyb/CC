from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import pandas as pd

factor_df = pd.read_hdf('/data/group/800319/fator_test_TX.h5', 'fator_test_TX')
factor_df1 = factor_df#.T[:50].T
print(factor_df1.shape)
factor_test = FactorBackTest(factor_df1)
factor_test.evaluation(30)
# factor_test.single_stock_back_test(601888)
factor_test.check_part_signal(100,root_path+'temp_daily_by_lzc/fig/')
# factor_test.result_output(fileroot=root_path,filename='camp_500_old')
print(factor_test.evaluation_result)
print(factor_test.running_time)


