# coding: utf-8
# Author：fengchi863
# Date ：2024/8/7 10:54

import os

model_path = '/data/user/015614/Zeus/pred/Sinope/v1_0_17/'
model_list = os.listdir(model_path)

for model_name in model_list:
    os.rename(model_path + model_name, model_path + model_name + 'RegModel')