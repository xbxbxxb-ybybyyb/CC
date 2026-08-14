import sys
sys.path.append('/data/user/015614/fcfactor')
sys.path.append('/data/user/015614/fcfactor/fefactorframework')
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import datetime as dt
import os

# factor_list = ['factor_fc_LastZTLastTick_n20240307_2'] # 不能带.py
strategy = 'europa'

cur_datetime = dt.datetime.today().strftime('%Y%m%d%H%M%S')
d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
print(d_date, digging_name, strategy_name)
if 'app' in d_date:
    d_date = 'd20240801'
    digging_name = 'factor_digging_1'
    strategy_name = 'Europa'
dir_output = f'/data/user/015614/fefactorframework/{strategy}_{d_date}_{digging_name}/'
os.makedirs(dir_output, exist_ok=True)

factor_list = list()
for i in sorted(os.listdir(f'/data/user/015614/fcfactor/fefactorframework/batch_factor/{strategy_name}/{d_date}/{digging_name}/factor/')):
    if ".py" in i:
        factor_list.append(i.split(".py")[0])

exists_factor_list = os.listdir('/data/user/015614/fefactorframework/europa_d20240801_factor_digging_1/factor_test/europa/')
exists_factor_list = list(filter(lambda x: 'pdf' in x, exists_factor_list))
exists_factor_list = list(map(lambda x: '_'.join(x.split('_')[:4]), exists_factor_list))
exists_factor_list = list(map(lambda x: 'factor_' + x, exists_factor_list))
factor_list = list(sorted(list(set(factor_list).difference(set(exists_factor_list)))))
len(factor_list)
print(f'本次批量跑因子数{len(factor_list)}个')
factor_list = factor_list[:227]
print(f'本次批量跑因子数{len(factor_list)}个')

res, check_res = Runner.run(factor_name_list=factor_list, start_date=20160101, end_date=20191231, strategy=strategy,
                 output_dir=dir_output, # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 20,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": True,
                     'report':True,
                     'mode': RunMode.research})
for i in factor_list:
    print(i)
    print(check_res[i[7:] + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
    print(check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])

