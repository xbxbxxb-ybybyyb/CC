# coding: utf-8
# Author：fengchi863
# Date ：2025/3/31 15:06

import os
import re
import time
from Zeus.Mimas.v2_0_4.config.strat_conf import DATE_CONFIG
from Zeus.Mimas.v2_0_4.backtest.SimBackTest import SimBackTest
import importlib
module_name = f'Zeus.Mimas.v2_0_4.config.path_conf'
module = importlib.import_module(module_name)

def start_backtest(pred_dir, period):
    pred4bt = list()
    config_set = set()
    for dirpath, dirnames, filenames in os.walk(pred_dir):
        if f'bt_result_{period}.xlsx' in filenames: continue
        for filename in filenames:
            if '~' in filename and period in dirpath:
                test_start_date = DATE_CONFIG[period]['test_start_date']
                test_end_date = DATE_CONFIG[period]['test_end_date']
                fit_start_date = DATE_CONFIG[period]['fit_start_date']
                fit_end_date = DATE_CONFIG[period]['fit_end_date']
                pred4bt.append((dirpath, f'{test_start_date}~{test_end_date}.csv', f'{fit_start_date}~{fit_end_date}.csv'))
                config = f'config{re.findall(r"config(.*?)/", dirpath)[0]}'
                config_set.add(config)

    pred4bt = list(set(pred4bt))
    pred_fpath_list = [f'{pred4bt[idx][0]}/{pred4bt[idx][1]}' for idx in range(len(pred4bt))]
    fit_fpath_list = [f'{pred4bt[idx][0]}/{pred4bt[idx][2]}' for idx in range(len(pred4bt))]

    if len(pred_fpath_list) == 0:
        print('当前扫描为空，没有需要回测的文件')
    else:
        print(f'当前需要回测{len(pred_fpath_list)}个')

    for config in config_set:   # 不同的config可能对应不同的收益文件
        print(config)
        t1 = time.time()
        PT = getattr(module, config)
        data_fpath = PT['data_fpath']
        profit_data_fpath = PT['profit_data_fpath']
        tmp_pred_fpath_list = list(filter(lambda x: config in x, pred_fpath_list))
        tmp_fit_fpath_list =list(filter(lambda x: config in x, fit_fpath_list))
        sbt = SimBackTest(pred_fpath_list=tmp_pred_fpath_list,
                          fit_fpath_list=tmp_fit_fpath_list,
                          data_fpath=data_fpath,
                          config=config,
                          profit_data_fpath=profit_data_fpath,
                          date_dict=DATE_CONFIG[period],
                          period=period,
                          attend_ratio_range=(20, 50),
                          save_flag=True,
                          multi_attend=True)
        sbt.start_backtest(multi=False)
        print(f'{config}耗时{time.time() - t1}')


if __name__ == '__main__':
    while True:
        start_backtest('/data/user/015614/Zeus/pred/Mimas/v2_0_4/', 'period3')