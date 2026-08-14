import pandas as pd
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os
import shutil
from h5data.IO import IO

paths = '/dfs/user/023859/neptune/20250720/20210101_20231231/factor_value/neptune'
h5_files = [f.split('.')[0] for f in os.listdir(paths) if f.endswith('.h5')]
filtered_df = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
filtered_df=filtered_df[~filtered_df['factor_type'].str.contains('T1mTransaction|T1mTickab|T1mTick1s|T1mCancel|T1mTickfulladdorder|T1mOrder|xdb_trade|xdb_tickex|xdb_order')]
filtered_df=filtered_df[filtered_df['提交时间'] < 20250724]
factors_check_res = pd.read_excel('/dfs/group/800463/public/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx')
factors_pass = factors_check_res[(factors_check_res['pre_check']=='pass')]['factor_name'].to_list()
factor_list_ = filtered_df[filtered_df['factor_name'].isin(factors_pass)]['factor_name'].to_list()
factor_list_ = list(set(factor_list_) - set(h5_files))
factor_list = ['factor_'+f for f in factor_list_]
print(len(factor_list), factor_list)
for factor in factor_list:
    if factor == 'factor_tsq_newneptune_longterm_20250612_6':
        strategy = 'neptune'
        start_date, end_date = 20210101, 20231231
        output_dir = f'/dfs/user/023859/neptune/20250720/{start_date}_{end_date}'
        os.makedirs(output_dir,exist_ok=True)

        res, check_res = Runner.run(factor_name_list=[factor], start_date=start_date, end_date=end_date, strategy=strategy,
                         output_dir=output_dir, # 结果的输出路径，包括回测报告等
                         options={
                             "calc.num_cpus": 1,
                             "local_evaluator": "",
                             'precheck': False,
                             "factor_test": False,
                             'report':False,
                             'mode': RunMode.research,})
# for i in factor_list:
#     print(i)
#     print('score:', check_res[i[7:] + '_' + strategy]['check_score_res'].loc['score','tot_score'])
#     print('IC:',check_res[i[7:] + '_' + strategy]['corr_sta'].loc['corr_tot', 'value'])
#     print('库内高相关因子：', check_res[i[7:] + '_' + strategy]['factor_corr_summary'])


