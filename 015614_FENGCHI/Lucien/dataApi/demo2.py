"""
# 一个回测的demo，用于郭攀时期的内容
from TrueSendStrategy.FactorTest import FactorTest
from TrueSendStrategy.operators import *
from TrueSendStrategy.utils import __freq__, _load_factor, save_pickle

def load_basic_factor(basic_factor_list, ft):

    for basic_factor in basic_factor_list:
        if basic_factor not in globals():
            globals()[basic_factor] = _load_factor(
                basic_factor, ft.start_date, ft.end_date, ft.code_list)


start_date = 20140101
end_date = 20181231
ft = FactorTest(start_date, end_date, __freq__)
ft.set_stock_pool()
ft.set_future()
code_list = ft.code_list



df = pd.read_hdf('/data/user/hanxu/20200911HeredityFactorMerge.xlsx')['formula'].to_list()
num = 0
for formula in tqdm(df):
    num += 1
    result = test_factor(formula, ft)
    print(result['factor_ret'])
    save_pickle('/data/user/hanxu/TrueSendStrategy/heredityFactor911/hanxu%s' % str(num).zfill(4), result)
"""