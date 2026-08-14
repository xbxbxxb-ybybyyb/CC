# coding: utf-8
# Author：fengchi863
# Date ：2020/7/8 16:09
from TrainingModel.TimeSeriesTrainBase import TimeSeriesTrainBase
from conf.feature_config_for_time_series import scale_list, non_scale_list
from conf.path_config import model_file_path
from dataApi.tradeDate import get_date_range
import numpy as np, pandas as pd

from keras.models import Sequential
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.utils import to_categorical
from keras.optimizers import SGD
import random

class LSTM_MODEL(TimeSeriesTrainBase):

    def __init__(self, start_date, end_date, factor_path=None, scale_list_=scale_list, non_scale_list_=non_scale_list, lag=30):
        super().__init__(start_date, end_date, factor_path, scale_list_, non_scale_list_, lag)

    def get_lstm_model(self, input_shape, class_num=3):
        model = Sequential()
        model.add(LSTM(unit=5, input_shape=input_shape))


    def feed_model_with_stk_sample(self, X_train, y_train, path, stk, model):
        Features_train = X_train.dropna()

        label = to_categorical(y_train.loc[Features_train.items] + 1)
        feature = Features_train.values.reshape(Features_train.shape + (1,))
        sample_weight = np.nansum(label, axis=0) / np.nansum(label)
        class_weight = {i: sample_weight[i] for i in range(
            len(sample_weight))}  # (y_train+1).apply(lambda x : sample_weight[int(x)] if not np.isnan(x) else 0).values
        idx_list = list(range(len(feature)))
        random.shuffle(idx_list)
        model = self.get_lstm_model(X_train.shape)
        model.compile(optimizer=SGD(lr=0.1, momentum=0.5), loss='categorical_crossentropy', metrics=['accuracy'])
