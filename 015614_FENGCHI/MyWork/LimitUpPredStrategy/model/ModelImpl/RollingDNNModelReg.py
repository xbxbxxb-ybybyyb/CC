
from LimitUpPredStrategy.model.ModelBase.RollingModelBaseReg import RollingModelBaseReg
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation
from LimitUpPredStrategy.Util.DataUtil import DataUtil
from keras.optimizers import Adam
import datetime, time, gc, os
import pandas as pd
from tqdm import tqdm

class RollingDNNModelReg(RollingModelBaseReg):
    def __init__(self, start_date=20140101, end_date=20191231):
        super().__init__(start_date, end_date)

    def train_model(self, X_train, y_train, params,end_date=None):
        adam = Adam(lr=0.00001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=5e-04)
        n = len(y_train)
        train_features = X_train[:int(n*0.9)]
        train_labels = y_train[:int(n*0.9)]
        val_features = X_train[int(n * 0.9):]
        val_labels = y_train[int(n * 0.9):]
        # date_list = sorted(list(set([x[0] for x in X_train.index])))
        # val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        # date_list = list(set(date_list) - set(val_date))
        # train_features, train_labels = X_train.loc[date_list], y_train.loc[date_list]
        # val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
        model = Sequential()
        model.add(Dense(16, input_shape=(X_train.shape[1],)))
        model.add(Activation('relu'))
        model.add(Dense(32))
        model.add(Activation('relu'))
        model.add(Dense(128))
        model.add(Activation('relu'))
        model.add(Dense(32))
        model.add(Activation('relu'))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer=adam)
        model.fit(train_features, train_labels,epochs=20,batch_size=64,validation_data=(val_features, val_labels), verbose=2, shuffle=False,)

        if 'val_pred_path' in params:
            val_labels = pd.DataFrame(val_labels)
            val_labels['prediction'] = self.predict(model, val_features)
            val_labels.columns.name = ['actual_label', 'prediction']
            DataUtil.save_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date, verbose=False)

        if 'train_pred_path' in params:
            train_label = pd.DataFrame(train_labels)
            train_label['prediction'] = self.predict(model, train_features)
            train_label.columns.name = ['actual_label', 'prediction']
            DataUtil.save_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date, verbose=False)
        return model

    def predict(self, model, X_test, true_pct=0.5):
        predict = model.predict(X_test)
        #predict = pd.DataFrame(predict.reshape(-1, 1), index=X_test.index)
        return predict

    def rolling_train_and_predict(self, params={}, period=60, predict_period=10,factor_num=80):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, training_sample = 0, 0, 0
        model = None
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            X_train, y_train, X_test, y_test = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),factor_num)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e
            e = time.time()

            if len(X_train) > 300 and len(set(y_train)) > 1:
                model = self.train_model(X_train, y_train, params, test_start_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test)
                y_test = pd.DataFrame(y_test)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label
