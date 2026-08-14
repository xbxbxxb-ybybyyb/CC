import numpy as np
import pandas as pd
# ind数量20日的标准差
'''
每日IC的均值： -0.03907380547553648
2021IC的均值： -0.03523416597104022
2022IC的均值： -0.03702742927135151
2023IC的均值： -0.04553649977872814
'''
factor_name = 'factor_qyh_heat_20231206_6'
def factor_qyh_heat_20231206_6(df_ori):
    df_ori[factor_name] = df_ori['ind'].unstack().rolling(20,1).std().stack()
    return df_ori[[factor_name]]