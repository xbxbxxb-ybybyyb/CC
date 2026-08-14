# coding: utf-8
# Author：fengchi863
# Date ：2021/5/25 17:17

from FaaMonitor.Util.tools import send_message
from LimitUpPredStrategy.conf.path_conf import pred_output_path

send_message(['015624'],pred_output_path + 'linear_reg/linear_reg_trainPeriod60_predictPeriod10_factorNum80_pctThreshold0.02_signal_r2s3.pkl')