# @Time : 2020/7/8 15:13
# @Author : Zhichen Lu
# @File : run_cnn_fine_tuning.py

import os

import keras.backend.tensorflow_backend as ktf
import tensorflow as tf

from TrainingModel.TimeSeriesModel import TimeSeriesModel
from dataApi.stockList import clean_stock_list

config = tf.ConfigProto()
# config.gpu_options.allow_growth=True
config.gpu_options.per_process_gpu_memory_fraction = 0.15
session = tf.Session(config=config)
ktf.set_session(session)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def fine_tunning_wraper(stk, label='rise_down_zero_5min', tag='CNN_20200622'):
    try:
        TSM = TimeSeriesModel(20170103, 20181231, '/data/group/800319/junkData/IntraFactorModel/FactorByStock_new/')
        TSM.tuning_for_stk(stk, label, train_period=120, tag=tag)
    except:
        print(stk, 'Wrong')


def multi_fine_tunning(piece_id, part_num):
    stock_pool = clean_stock_list('COMMON', no_limit_down=True, no_limit_up=True).loc[20170102:20191231]
    isin = stock_pool.sum(axis=0)
    stk_list = isin[isin > 0].index.tolist()
    stk_num = len(stk_list)
    if piece_id == part_num:
        stk_list = stk_list[(piece_id - 1) * stk_num // part_num:]
    else:
        stk_list = stk_list[(piece_id - 1) * stk_num // part_num:piece_id * stk_num // part_num]
    for stk in stk_list:
        fine_tunning_wraper(stk)
    # pool = Pool(1)
    # pool.map(fine_tunning_wraper, stk_list)
    # pool.close()
    # pool.join()


# def fine_tunning_wraper_test(stk, label='rise_down_zero_5min', tag='CNN_20200622'):
#     TSM = TimeSeriesModel(20170103, 20181231, '/data/group/800319/junkData/IntraFactorModel/FactorByStock_new/')
#     TSM.tuning_for_stk(stk, label, train_period=120, tag=tag)


if __name__ == "__main__":
    # fine_tunning_wraper_test(1)
    multi_fine_tunning(1, 5)
