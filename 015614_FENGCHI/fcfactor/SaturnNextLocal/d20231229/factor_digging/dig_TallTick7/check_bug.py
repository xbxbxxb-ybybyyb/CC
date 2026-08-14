# coding: utf-8
# Author：fengchi863
# Date ：2023/12/28 20:31

import pandas as pd

check1 = pd.read_hdf("/data/user/015614/factor/dig_TallTick7_20231228202841/('TotalOfferQty', 0.75, 'Sell1NumOrders').h5")
check2 = pd.read_hdf("/data/user/015614/factor/dig_TallTick7_20231228105221/('TotalOfferQty', 0.75, 'Sell1NumOrders').h5")

basic_file_path = '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5'
basic_df = pd.read_hdf(basic_file_path)
print(1)