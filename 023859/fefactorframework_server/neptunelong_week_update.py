import os
import shutil
import datetime
import pandas as pd
from loguru import logger
from settings import RunMode
from xfactor.FactorUtil import update_xlsx, get_factor_class
import xfactor.runner.BasicRunner as Runner
import json
from xquant.compute.aimr import AIMR


#参数设置
strategy='NeptuneLong'
append_factor_inf=True
module_base_dir='factor_lib'
path_factor_lib = '/data/user/023859/fefactorframework_server/factor_lib/' # 框架的factor文件夹地址

# 判断入库时间（上周四）
today=datetime.date.today()
today_weekday=today.weekday()
if today_weekday>=3:
    last_thursday=today-datetime.timedelta(days=today_weekday-3)
else:
    last_thursday = today - datetime.timedelta(days=today_weekday +7- 3)
last_thursday=last_thursday.strftime('%Y%m%d')
print('入库时间为{}'.format(last_thursday))

#加入到excel中
if append_factor_inf:
    new_factors_local_dir = os.path.join(module_base_dir, strategy.lower(), 'factor_' + str(int(last_thursday)))
    new_factors_dir = os.path.join(os.getcwd(), new_factors_local_dir)
    factor_list = [i[:-3] for i in os.listdir(new_factors_dir) if i.endswith(".py")]
    factor_list.sort()
    kls_list = [get_factor_class(new_factors_local_dir, i) for i in factor_list]
    update_xlsx(strategy.lower(), kls_list, last_thursday)


# 筛选df后
df = pd.read_excel('/data/user/023859/factor_zooZZmkt/all_factor_inf.xlsx')
count = df['factor_name'].value_counts().head()
assert count.max() == 1
filtered_df = df[df['factor_type'].str.contains('\[')]#新平台框架的因子，factor_type中会带[]
filtered_df = filtered_df[~filtered_df['factor_type'].str.contains('T1mTransaction|T1mTickab|T1mTick1s|T1mCancel|T1mTickfulladdorder|T1mOrder|xdb_tickex|xdb_order|xdb_trade')]

filtered_df=filtered_df[filtered_df['提交时间']==int(last_thursday)]

# paths = '/data/user/023859/factor_zooZZmkt/all_factor/931/'
# h5_files = [f for f in os.listdir(paths)]
# filtered_df = filtered_df[~filtered_df['factor_name'].isin(h5_files)]

print('新平台入库数量：',len(filtered_df),list(filtered_df['factor_name']))


dock_num=100
dock_pool_num=24
factor_list=filtered_df['factor_name'].unique()

# 因子数<=100
# parallel_list=['%s;%s;%s;%s'%(last_thursday,strategy,factor_name,dock_pool_num) for factor_name in factor_list]
# dock_num = min(len(factor_list),dock_num)
#
# params = {"parallel_list": parallel_list,
#           "tag":"xquant", "cpu":dock_pool_num, "gpu":0, "memory":300*1024}
# AIMR.runTasks('neptune_week_update_aimr.py', json.dumps(params))

# 因子数超100
dock_num=min(dock_num,len(factor_list))
print('并行化：%s*%s'%(dock_num,dock_pool_num))
parallel_list=['%s;%s;%s;%s'%(last_thursday,strategy,dock_pool_num,'-'.join(factor_list[i::dock_num])) for i in range(dock_num)]
print(parallel_list)
params = {"parallel_list": parallel_list,
          "tag":"xquant", "cpu":dock_pool_num, "gpu":0, "memory":200*1024}
AIMR.runTasks('neptunelong_week_update_aimr.py',json.dumps(params))