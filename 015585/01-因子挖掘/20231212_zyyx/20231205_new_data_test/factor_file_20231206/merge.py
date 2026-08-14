import pandas as pd
import os
#
factor_list = ['factor_qyh_heat_20231206_' + str(i) for i in range (1,17)]
res_df = pd.DataFrame()
for factor_name in factor_list:
    print(factor_name)
    df_factor = pd.read_pickle('/data/user/015585/01-因子挖掘/20231205_new_data_test/factor_file_20231206/' + factor_name + '.pkl')
    res_df[factor_name] = df_factor[factor_name]
res_df.to_pickle('/data/user/015585/01-因子挖掘/20231205_new_data_test/factor_file_20231206/' + 'new_factor' + '.pkl')