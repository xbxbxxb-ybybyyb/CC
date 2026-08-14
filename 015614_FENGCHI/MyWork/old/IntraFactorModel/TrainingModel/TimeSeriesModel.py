# @Time : 2020/6/22 10:42
# @Author : Zhichen Lu
# @File : TimeSeriesModel_dev.py


import datetime
import random

import gc
import pandas as pd
import tqdm
from keras.callbacks import *
from keras.layers import Conv2D, Dropout, Input, Reshape, concatenate, Flatten, Dense, BatchNormalization
from keras.models import Model
from keras.models import load_model
from keras.optimizers import SGD
from keras.utils import to_categorical
from sklearn import metrics
from sklearn import preprocessing

from TrainingModel.TimeSeriesTrainBase import TimeSeriesTrainBase
from conf.feature_config_for_time_series import scale_list, non_scale_list
from conf.path_config import model_file_path


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
        logger = CSVLogger(log_path + 'cnn_period%s_log%s.csv' % (
        y_train.index[-1].split('_')[-1][:8], datetime.date.today().strftime('%Y%m%d')))  # lr_scheduler = LearningRateScheduler(schedule=0,verbose=1)
        lr_reduce = ReduceLROnPlateau(monitor='val_loss', factor=0.5, min_lr=0.00001, patience=15)
        early_stop = EarlyStopping(patience=45)
        model.fit(feature[idx_list], label[idx_list], batch_size=1024, epochs=200, verbose=1, validation_split=0.1, shuffle=True, class_weight=class_weight,
                  callbacks=[logger, lr_reduce, early_stop])
        return model

    def feed_model_with_stk_sample(self, Features_train, y_train, path, stk, model):
        Features_train = Features_train.dropna()

        label = to_categorical(y_train.loc[Features_train.items] + 1)
        feature = Features_train.values.reshape(Features_train.shape + (1,))
        sample_weight = np.nansum(label, axis=0) / np.nansum(label)
        class_weight = {i: sample_weight[i] for i in range(len(sample_weight))}  # (y_train+1).apply(lambda x : sample_weight[int(x)] if not np.isnan(x) else 0).values
        idx_list = list(range(len(feature)))
        random.shuffle(idx_list)
        # model = self.CNN(Features_train.shape)
        # model.compile(optimizer=SGD(lr=0.1, momentum=0.5), loss='categorical_crossentropy', metrics=['accuracy'])
        log_path = path + '/NN_stk_Log/'
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        logger = CSVLogger(log_path + 'cnn_%s_period%s_log%s.csv' % (
        str(stk), y_train.index[-1][0], datetime.date.today().strftime('%Y%m%d')))  # lr_scheduler = LearningRateScheduler(schedule=0,verbose=1)
        lr_reduce = ReduceLROnPlateau(monitor='val_loss', factor=0.5, min_lr=0.00001, patience=10)
        early_stop = EarlyStopping(patience=31)
        model.fit(feature[idx_list], label[idx_list], batch_size=1024, epochs=200, verbose=1, validation_split=0.1, shuffle=True, class_weight=class_weight,
                  callbacks=[logger, lr_reduce, early_stop])
        return model

    def load_data_one_stk_for_turning(self, stk, label_method, period_info, train_window):
        train_start, train_end, test_start, test_end = period_info[1]
        dataset = self.fds.get_dataset(stk, None, test_end, label_method)
        no_pause_index = self.get_no_pause_index(stk)
        X_train = dataset[0].loc[no_pause_index].loc[:(train_end, 1500)][-train_window * 242 - 242:]
        test_len = dataset[0].loc[no_pause_index].loc[(test_start, 925):(test_end, 1500)].shape[0]
        X_test = dataset[0].loc[no_pause_index].loc[:(test_end, 1500)][-test_len - 242:]
        y_train, y_test = dataset[1].loc[X_train.index], dataset[1].loc[X_test.index]
        if len(X_train) < 242 * 5:
            return pd.Panel(), pd.Series(), pd.Panel(), pd.Series()
        # fillna
        X_train, X_test = self.fill_nan(X_train, X_test)
        # delete nan in label
        X_train, y_train = self.drop_nan_sample(X_train, y_train)
        X_test, y_test = self.drop_nan_sample(X_test, y_test)
        # preprocessing
        scaler = preprocessing.Normalizer()  # MinMaxScaler()
        if len(X_test) > 0:
            X_train, X_test = self.transformation_scaler(self.scale_list, self.non_scale_list, scaler, X_train, X_test)
        else:
            X_train = self.transformation_scaler(self.scale_list, self.non_scale_list, scaler, X_train)
            X_test = pd.DataFrame()
        Features_train = {}
        Features_test = {}
        for i in list(range(self.lag))[::-1]:
            Features_train[i] = X_train.shift(i).loc[:(train_end, 1500)][-train_window * 242:]
            Features_test[i] = X_test.shift(i).loc[:(test_end, 1500)][-test_len:]
        Features_train = pd.Panel(Features_train)
        Features_test = pd.Panel(Features_test)
        Features_train = Features_train.swapaxes(0, 1)
        Features_test = Features_test.swapaxes(0, 1)
        y_train = y_train.loc[Features_train.items]
        y_test = y_test.loc[Features_test.items]
        return Features_train, y_train, Features_test, y_test

    def tuning_for_stk(self, stk_id, label_method, train_period, base_period=60, period_predict=20, tag=None, model_path=model_file_path):
        out_path = '%s/%s/' % (model_path, tag)
        predict_label_path = out_path + 'stk_label/'
        if not os.path.exists(predict_label_path):
            os.mkdir(predict_label_path)
        if os.path.exists(predict_label_path + '%d.pkl' % stk_id):
            print(stk_id, 'exist')
            return 0
        rolling_index = self.get_rolling_index_by_fixed_interval(self.start_date, self.end_date, base_period, period_predict)
        # model_set = {}
        predict_label = pd.Series()
        true_label = pd.Series()
        bar = tqdm.tqdm(rolling_index[9:])
        for period_info in bar:
            bar.set_description(
                "%s | %d | %d | %d-%d" % (datetime.datetime.now().strftime('%H:%M:%S'),
                                          os.getpid(), stk_id, period_info[1][2], period_info[1][3]))
            X_train, y_train, X_test, y_test = self.load_data_one_stk_for_turning(stk_id, label_method, period_info, train_window=train_period)
            model = load_model(out_path + 'model_train_%d_%d_test_%d_%d.h5' % tuple(period_info[1]))
            model.compile(optimizer=SGD(lr=0.5, momentum=0.5), loss='categorical_crossentropy', metrics=['accuracy'])
            model = self.feed_model_with_stk_sample(X_train, y_train, out_path, stk_id, model)
            prediction = model.predict(X_test.values.reshape(X_test.shape + (1,)))
            prediction = pd.Series(prediction.argmax(axis=1) - 1, index=y_test.index)
            predict_label = pd.concat([predict_label, prediction])
            # print(stk_id,period_info[1])
            # print('acc:',metrics.accuracy_score(y_test,prediction),pd.DataFrame({0:y_test}).groupby(0).size().max()/len(y_test))
            # print('precision:',metrics.precision_recall_fscore_support(y_test,prediction)[0])
            true_label = pd.concat([true_label, y_test])
            del X_train, y_train, X_test, y_test, model
            gc.collect()

        compare = pd.DataFrame({'label': true_label, 'prediction': predict_label})
        print('all acc:', metrics.accuracy_score(true_label, predict_label), compare.groupby('label').size().max() / len(compare))
        print('all precision', metrics.precision_recall_fscore_support(true_label, predict_label))

        pd.to_pickle(compare, predict_label_path + '%d.pkl' % stk_id)

        return compare

    def training_tuninig_process(self, base_stk_list, label_method, period=60, period_predict=20, tag=None, model_path=model_file_path):
        model_set, _ = self.train_base_universe(base_stk_list, label_method, period, period_predict, tag, model_path)

def main():
    stk_list = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/best_model_hyper_params/para_optimization_pool.pkl')
    TSM = TimeSeriesModel(20170103, 20181231, '/data/group/800319/junkData/IntraFactorModel/FactorByStock_new/')
    # TSM.train_base_universe(stk_list, 'rise_down_zero_5min', tag='CNN_20200706')
    # TSM.evaluate_basse_model(stk_list, 'rise_down_zero_5min', tag='CNN_20200622')
    TSM.tuning_for_stk(stk_list[1], 'rise_down_zero_5min', train_period=120, tag='CNN_20200622')

#
# if __name__ == "__main__":
#     main()
