import sys
sys.path.append("/data/user/023859/fefactorframework_train/")
import os
import pandas as pd
import xfactor.runner.BasicRunner as Runner
from xquant.compute.aimr import AIMR
from settings import RunMode

# param = AIMR.getParam()
# print(param)
# param_list=param.split(';')
# strategy=param_list[0]
# factor_name=param_list[1]
# dock_pool_num=int(param_list[2])

param = AIMR.getParam()
print(param)
param_list=param.split(';')
strategy_version=int(param_list[0])
start_date=int(param_list[1])
end_date=int(param_list[2])
strategy=param_list[3]
dock_pool_num=int(param_list[4])
factor_name_list=param_list[5].split('-')

output_dir = f'/dfs/user/023859/neptune/{strategy_version}/{start_date}_{end_date}/'
os.makedirs(output_dir,exist_ok=True)
# df = pd.read_excel(f'/dfs/user/023859/neptune/{strategy_version}/factor_bank_inf_s1.xlsx')
# filtered_df = df[df['factor_name']==factor_name]
# filtered_df = df[df['factor_name'].isin(factor_name_list)]

factor_list = []
for factor_name in factor_name_list:
# for index, inf in filtered_df.iterrows():
#     if strategy.lower() in ["saturn", "sell", "mimas", "neptune"]:
#         factor_name, factor_date = inf['factor_name'], inf['提交时间']
#     elif strategy.lower() in ["europa", "jupiter", "metis"]:
#         factor_name, factor_date = inf['factor_name'], inf['factor_date']
#     else:
#         raise Exception("策略名不在规定范围内！input_strategy={}".format(strategy))

    factor_list.append(
        'factor_' + factor_name
    )

# 入库
if len(factor_list) > 0:
    print(strategy, len(factor_list), factor_list)
    _,_ = Runner.run(factor_name_list=factor_list, start_date=start_date, end_date=end_date, strategy=strategy,
               output_dir=output_dir,  # 结果的输出路径，包括回测报告等
               options={
                   "calc.num_cpus": dock_pool_num,
                   "local_evaluator": "",
                   'precheck': False,
                   "factor_test": False,
                   'report': False,
                   'mode': RunMode.research, })
    print('{}策略尝试生成{}个因子'.format(strategy, str(len(factor_list))))