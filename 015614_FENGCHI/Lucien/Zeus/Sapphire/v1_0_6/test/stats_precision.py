# coding: utf-8
# Author：fengchi863
# Date ：2024/8/20 10:11

import os
import pandas as pd
import numpy as np

root_path = '/data/user/015614/Zeus/pred/Sapphire/v1_0_6/'

model_list = list(sorted(os.listdir(root_path)))
res = pd.DataFrame(index=model_list, columns=['precision', 'recall', 'rmse', 'ic'])
for model in model_list:
    precision_list = list()
    recall_list = list()
    rmse_list = list()
    ic_list = list()
    for idx in range(0, 90):
        result = pd.read_json(root_path + model + f'/hyper/{idx}/train_result.json')
        precision, recall, rmse, ic = result.loc[0][2], result.loc[0][3], result.loc[0][4], result.loc[0][5]
        precision_list.append(precision)
        recall_list.append(recall)
        rmse_list.append(rmse)
        ic_list.append(ic)
    res.loc[model] = [np.mean(precision_list), np.mean(recall_list), np.mean(rmse_list), np.mean(ic_list)]
from dataApi.sendInfo import send_file
send_file(res)



