# @Time : 2020/6/22 10:42
# @Author : Zhichen Lu
# @File : TimeSeriesModel_dev.py


import datetime
import random
from multiprocessing import Pool

import pandas as pd
from keras.callbacks import *
from keras.layers import Conv2D, Dropout, Input, Reshape, concatenate, Flatten, Dense, BatchNormalization
from keras.models import Model
from keras.optimizers import SGD
from keras.utils import to_categorical

from TrainingModel.TimeSeriesTrainBase import TimeSeriesTrainBase
from conf.feature_config_for_time_series import scale_list, non_scale_list

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class TimeSeriesModel(TimeSeriesTrainBase):

    def __init__(self, start_date, end_date, factor_path=None, scale_list_=scale_list, non_scale_list_=non_scale_list, lag=30):
        super().__init__(start_date, end_date, factor_path, scale_list_, non_scale_list_, lag)

    def CNN(self, input_shape, class_num=3):
        input = Input(shape=input_shape[1:] + (1,))
        conv1 = Conv2D(filters=5, kernel_size=(3, input_shape[2]), name='conv1', activation='sigmoid')(input)
        conv1 = Reshape((conv1.shape[1].value, conv1.shape[-1].value, 1))(conv1)
        conv2 = Conv2D(filters=5, kernel_size=(5, input_shape[2]), name='conv2', activation='sigmoid')(input)
        conv2 = Reshape((conv2.shape[1].value, conv2.shape[-1].value, 1))(conv2)
        conv3 = Conv2D(filters=5, kernel_size=(7, input_shape[2]), name='conv3', activation='sigmoid')(input)
        conv3 = Reshape((conv3.shape[1].value, conv3.shape[-1].value, 1))(conv3)
        out_series = concatenate([conv1, conv2, conv3], axis=1)
        out_series = BatchNormalization(axis=-2, momentum=0.5)(out_series)
        # conv4 = Conv2D(filters=8,kernel_size=(10, out_series.shape[2].value),name='conv4',activation='sigmoid')(out_series)
        # conv4 = Reshape((conv4.shape[1].value, conv4.shape[-1].value, 1))(conv4)
        # conv5 = Conv2D(filters=4,kernel_size=(15, conv4.shape[2].value),name='conv5',activation='sigmoid')(conv4)
        # conv5 = Reshape((conv5.shape[1].value, conv5.shape[-1].value, 1))(conv5)
        # full_conn = Flatten()(conv5)

        full_conn = Flatten()(out_series)

        full_conn = Dropout(0.5)(full_conn)
        hidden = Dense(5, activation='sigmoid')(full_conn)
        soft = Dense(class_num, activation='softmax')(hidden)
        cnn = Model(input, soft)
        return cnn

    def intra_normalize_sample_scaler(self, sample):
        # sample = Features_train_arr
        sample_mean = np.array([np.nanmean(sample[i]) for i in range(sample.shape[0])])
        sample_std = np.array([np.nanstd(sample[i]) for i in range(sample.shape[0])])
        normalized_sample = (sample.transpose(1, 2, 0) - sample_mean) / sample_std
        return normalized_sample.transpose(2, 0, 1)


    def load_data_one_stk_intrsample_scale(self, stk, label_method, period_info, for_universe=False):
        train_start, train_end, test_start, test_end = period_info[1]
        dataset = self.fds.get_dataset(stk, train_start, test_end, label_method)
        no_pause_index = self.get_no_pause_index(stk)
        X_train, X_test = dataset[0].loc[no_pause_index].loc[(train_start, 925):(train_end, 1500)], \
                          dataset[0].loc[no_pause_index].loc[(test_start, 925):(test_end, 1500)]
        y_train, y_test = dataset[1].loc[X_train.index], dataset[1].loc[X_test.index]
        if len(X_train) < 242 * 5:
            return pd.Panel(), pd.Series(), pd.Panel(), pd.Series()
        # fillna
        X_train, X_test = self.fill_nan(X_train, X_test)
        # delete nan in label
        X_train, y_train = self.drop_nan_sample(X_train, y_train)
        X_test, y_test = self.drop_nan_sample(X_test, y_test)

        Features_train = {}
        Features_test = {}
        for i in list(range(self.lag))[::-1]:
            Features_train[i] = X_train.shift(i)
            Features_test[i] = X_test.shift(i)
        Features_train = pd.Panel(Features_train)
        Features_test = pd.Panel(Features_test)
        Features_train = Features_train.swapaxes(0, 1)
        Features_test = Features_test.swapaxes(0, 1)
        Features_train_arr = self.intra_normalize_sample_scaler(Features_train.values)
        Features_test_arr = self.intra_normalize_sample_scaler(Features_test.values)
        Features_train.loc[:, :, :] = Features_train_arr
        Features_test.loc[:, :, :] = Features_test_arr
        if for_universe:
            Features_train.items = ['%d_%d' % (stk, x[0] * 10000 + x[1]) for x in Features_train.items]
            Features_test.items = ['%d_%d' % (stk, x[0] * 10000 + x[1]) for x in Features_test.items]
            y_train.index = Features_train.items
            y_test.index = Features_test.items
        return Features_train, y_train, Features_test, y_test

    def load_data_universe(self, stk_list, label_method, period_info):
        print('subclass version')
        training_set, test_set, label_train, label_test = [], [], [], []
        pool = Pool(10)
        dataset_dict = {}
        for stk in stk_list:
            # self.load_data_one_stk(*(stk, label_method, period_info, True))
            # Features_train, y_train, Features_test, y_test = self.load_data_one_stk(stk,label_method, period_info,True)
            dataset_dict[stk] = pool.apply_async(self.load_data_one_stk_intrsample_scale, (*(stk, label_method, period_info, True),))
            # print(stk)
        pool.close()
        pool.join()
        for stk in stk_list:
            Features_train, y_train, Features_test, y_test = dataset_dict[stk].get()
            training_set.append(Features_train)
            test_set.append(Features_test)
            label_train.append(y_train)
            label_test.append(y_test)

        training_set = pd.concat(training_set, axis='items')
        test_set = pd.concat(test_set, axis='items')
        label_train = pd.concat(label_train)
        label_test = pd.concat(label_test)
        return training_set, label_train, test_set, label_test

    def feed_model_with_universe(self, Features_train, y_train, path):
        print(Features_train.shape)
        Features_train = Features_train.dropna()

        label = to_categorical(y_train.loc[Features_train.items] + 1)
        feature = Features_train.values.reshape(Features_train.shape + (1,))
        sample_weight = np.nansum(label, axis=0) / np.nansum(label)
        class_weight = {i: sample_weight[i] for i in range(len(sample_weight))}  # (y_train+1).apply(lambda x : sample_weight[int(x)] if not np.isnan(x) else 0).values
        idx_list = list(range(len(feature)))
        random.shuffle(idx_list)
        model = self.CNN(Features_train.shape)
        model.compile(optimizer=SGD(lr=0.1, momentum=0.5), loss='categorical_crossentropy', metrics=['accuracy'])
        log_path = path + '/NN_Log/'
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        logger = CSVLogger(log_path + 'cnn_period%s_log%s.csv' % (y_train.index[-1].split('_')[-1][:8], datetime.date.today().strftime('%Y%m%d')))
        # lr_scheduler = LearningRateScheduler(schedule=0,verbose=1)
        lr_reduce = ReduceLROnPlateau(monitor='val_loss', factor=0.5, min_lr=0.00001, patience=15)
        early_stop = EarlyStopping(patience=45)
        K.tensorflow_backend._get_available_gpus()
        model.fit(feature[idx_list], label[idx_list], batch_size=1024, epochs=200, verbose=1, validation_split=0.1, shuffle=True, class_weight=class_weight,
                  callbacks=[logger, lr_reduce, early_stop])
        return model


def main():
    stk_list = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/best_model_hyper_params/para_optimization_pool.pkl')
    TSM = TimeSeriesModel(20170103, 20181231, '/data/group/800319/junkData/IntraFactorModel/FactorByStock_new/')
    TSM.train_base_universe(stk_list, 'rise_down_zero_5min', tag='CNN_20200706_intrasample_normalize')
    # TSM.evaluate_basse_model(stk_list, 'rise_down_zero_5min', tag='CNN_20200622')

    # compare = pd.read_pickle(root_path+'label_compare.pkl')


if __name__ == "__main__":
    main()
