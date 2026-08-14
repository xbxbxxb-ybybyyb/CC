# coding: utf-8
# Author：fengchi863
# Date ：2025/1/10 16:39

import pandas as pd
import numpy as np

check = pd.read_pickle('/data/user/015614/junkData/yugao_all_df.pkl')
print(1)

group = check.groupby(['预告报告期', '预告类型']).count()