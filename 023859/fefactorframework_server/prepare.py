import pandas as pd
all_factor_inf = pd.DataFrame(columns = ['factor_name','factor_type','factor_owner','因子逻辑','提交时间','emotion','填充值','是否针对注册制做调整','T-1日类别','逻辑类别'])
all_factor_inf.to_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx',index=False)
