import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os

factor_list = ['factor_tsq_20241128_2'] # 不能带.py
strategy = 'europa'
# for i in os.listdir(os.path.join(os.getcwd(), "factor")):
#     if ".py" in i:
#         factor_list.append(i.split(".py")[0])
res, check_res = Runner.run(factor_name_list=factor_list, start_date=20190301, end_date=20190331, strategy=strategy,
                 output_dir="/data/user/023859/test/", # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 10,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": True,
                     'report':True,
                     'mode': RunMode.research})
for i in factor_list:
    print(check_res[i[7:] + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
    print(check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])

