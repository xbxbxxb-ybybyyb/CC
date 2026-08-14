# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 9:00

from Zeus.Saturn.v1_1.hyper_param_space import *
from Zeus.Saturn.v1_1.models.ModelFactory import ModelFactory
from Zeus.Saturn.v1_1.path_conf import *
from Zeus.Saturn.v1_1.DataPrepare import DataPrepare


date_config = dict(train_start_date=20160104,
                   train_end_date=20181231,
                   valid_start_date=20191008,
                   valid_end_date=20200630,
                   pred_start_date=20200701,
                   pred_end_date=20201231)

dp = DataPrepare(date_config=date_config)




model_name = 'lr_model'
mf_inst = ModelFactory(model_name=model_name, factor_filter_path=filter_factor_fpath)
X_train, y_trian, X_valid, y_valid = mf_inst.get_dateset()



mf_inst.train_model(X_train, y_trian, param=lr_param)
y_pred = mf_inst.model_predict(X_valid)
acc, rec, prec, f1, auc = mf_inst.calc_model_score(y_valid, y_pred)
