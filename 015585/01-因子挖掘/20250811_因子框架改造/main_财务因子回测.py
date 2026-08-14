import pandas as pd
import IO
import os
import numpy as np
import NeptuneFinanceFactorTest

factor_df = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/neptune/qyh_neptune_20250515_12.h5')

factor_test = NeptuneFinanceFactorTest.FactorTest(20170110,20201231)
print(os.getcwd())

res = factor_test.factor_test(factor_df, [np.nan], '/data/user/015585/01-因子挖掘/20250811_因子框架改造/', factor_corr_test=True, generate_pdf=False)



