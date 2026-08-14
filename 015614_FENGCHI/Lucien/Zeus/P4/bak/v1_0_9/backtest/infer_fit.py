# coding: utf-8
# Author：fengchi863
# Date ：2025/4/2 10:45

import os
import re
import time
import pandas as pd
from Zeus.P4.v1_0_9.config.strat_conf import DATE_CONFIG
from Zeus.P4.v1_0_9.submit_model.infer import infer
import importlib
module_name = f'Zeus.P4.v1_0_9.config.path_conf'
module = importlib.import_module(module_name)


def start_backtest(pred_dir, period):
    config_set = set()
    fit_start_date = DATE_CONFIG[period]['fit_start_date']
    fit_end_date = DATE_CONFIG[period]['fit_end_date']
    multi_tuple_list = list()
    for dirpath, dirnames, filenames in os.walk(pred_dir):
        for filename in filenames:
            if '_factorName' in filename:
                model = dirpath + '/XgbRegModel.pkl'
                datapro_file = dirpath + '/_factorScaler.json'
                factor_list_file = dirpath + '/_factorName.json'
                threshold_file = dirpath + '/_score_threshold.json'
                model_file = model
                config = f'config{re.findall(r"config(.*?)/", dirpath)[0]}'
                multi_tuple_list.append((config, factor_list_file, model_file, threshold_file, datapro_file))   # 传入infer所需要的路径集合，便于后续多进程推理
                config_set.add(config)

    for config in config_set:   # 不同的config可能对应不同的收益文件
        print(config)
        t1 = time.time()
        PT = getattr(module, config)
        data_fpath = PT['data_fpath']
        data_df = pd.read_pickle(data_fpath)
        data_end_date = data_df.index.get_level_values(0).strftime('%Y%m%d').map(int).max()
        begin_date = fit_start_date
        end_date = min(data_end_date, fit_end_date)

        t1 = time.time()
        tmp_multi_tuple_list = list(filter(lambda x: x[0] == config, multi_tuple_list))
        for idx, *tmp_multi_tuple in tmp_multi_tuple_list:
            result, _ = infer(data_df, tmp_multi_tuple[0], tmp_multi_tuple[1], str(begin_date), str(end_date), tmp_multi_tuple[2], tmp_multi_tuple[3])
            FileUtil.save_df2csv()
        print(f'本次参数空间搜索耗时{time.time() - t1}秒')


if __name__ == '__main__':
    start_backtest('/data/user/015614/Zeus/pred/P4/v1_0_9/', 'period6_fit')