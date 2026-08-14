import pandas as pd
import IO
from project_2_factor_test_origin import FactorTest
sft_basic_path = '/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5'  # 这个文件里有label和所有因子
df_sft = IO.read_data([20160101, 20160110], alt=sft_basic_path)
factor_test = FactorTest(20160101, 20191231, df_sft, cal_mi=False)