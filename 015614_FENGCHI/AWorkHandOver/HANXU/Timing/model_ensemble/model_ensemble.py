# coding: utf-8
# Author：fengchi863
# Date ：2022/7/1 14:43

from HANXU.Timing.model_ensemble.multi_losses_model import loss_dict
import pandas as pd
import numpy as np

model_name = 'XGB400_dc_multiLoss'

loss_list = list(loss_dict.keys())

base_signal = pd.read_pickle(f'/data/group/800442/800319/Timing/BackTest/Signal/model_ensemble/{loss_list[0]}/' + model_name + '.pkl')

# for loss_func_name in loss_list:
#     signal_path = f'/data/group/800442/800319/Timing/BackTest/Signal/model_ensemble/{loss_func_name}/'
all_signal = np.r_['0, 3', tuple(pd.read_pickle(f'/data/group/800442/800319/Timing/BackTest/Signal/model_ensemble/{loss_func_name}/' +
                                              model_name + '.pkl').values for loss_func_name in loss_list)]
all_signal = all_signal.transpose(1, 2, 0).reshape(-1, 4)

# 第一种集成方式，投票
signal1 = all_signal.copy()
_signal_short = (signal1 == -1).sum(axis=1) > signal1.shape[1] / 2
_signal_long = (signal1 == 1).sum(axis=1) > signal1.shape[1] / 2
# _signal_0 = (signal1 == 0).sum(axis=1) > signal1.shape[1] / 2
# ensemble_signal = np.zeros(signal1.shape[0]) - _signal_short + _signal_long + _signal_0
ensemble_signal = np.zeros(signal1.shape[0]) - _signal_short + _signal_long

ensemble_signal = ensemble_signal.reshape(base_signal.shape[0], base_signal.shape[1])
ensemble_signal = pd.DataFrame(ensemble_signal, index=base_signal.index, columns=base_signal.columns)
# TODO：保存signal到指定文件并进行回测


