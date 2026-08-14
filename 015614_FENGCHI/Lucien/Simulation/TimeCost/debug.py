# coding: utf-8
# Author：fengchi863
# Date ：2023/4/17 13:29

import pandas as pd

check = pd.read_pickle('/data/group/800463/xiely/order-delay/20230327-uat_lite-20230414/combined_df5.pkl')
check = check.query('source == "JupiterNew"')
check.query('machine_code == "168.62.9.53"')
print(1)