from dataApi.testFactor import FactorBackTest
import pandas as pd
import time
e = time.time()
factor_df = pd.read_hdf('/data/group/800319/capm.h5', 'capm')
test_factor = FactorBackTest()
test_factor.evaluate(factor_df)
print('total_run_time',time.time()-e)