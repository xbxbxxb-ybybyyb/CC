# coding: utf-8
# Author：fengchi863
# Date ：2023/5/4 16:09

import gzip
import datetime
import pandas as pd

sim_date_list = [20230505]
create_date = 20230508
for sim_date in sim_date_list:
    print(sim_date)
    sim_date_str = pd.to_datetime(str(sim_date)).strftime('%Y-%m-%d')
    f_in = open(f'/data/user/015614/shared/for_wj/log/StrongStrategy-{sim_date_str}-uat_lite-{create_date}.txt', 'rb')   # 创建日期
    f_out = gzip.open(f'/data/group/800463/日内强势股/log/StrongStrategy-{sim_date_str}-uat_lite.log.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    print(f'{sim_date}转换结束')