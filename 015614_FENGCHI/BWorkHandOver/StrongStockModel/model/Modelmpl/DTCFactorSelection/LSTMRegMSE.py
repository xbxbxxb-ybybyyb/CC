# @Time : 2020/12/9 10:24
# @Author : Zhichen Lu
# @File : LSTMRegHXLoading.py

import pandas as pd
from keras.callbacks import *
from keras.layers import Dropout, SimpleRNN, Input, Reshape, LSTM,Dense,BatchNormalization,Flatten
from keras import Model
from keras.losses import mean_squared_error
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from sklearn import metrics
import tensorflow as tf
import gc
from keras.applications import resnet50
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from dataApi.DataPrepare import DataPrepare
from dataApi.tradeDate import get_desample_minute_dict
from tqdm import tqdm
import gc, time, datetime
from StrongStockModel.conf.path_config import root_path
from scipy.ndimage.interpolation import shift

time_list = get_desample_minute_dict(5)
time_list = list(set([time_list[x] for x in time_list]))
time_list.sort()
# param_lstm = {'hidden_dim': (16, ), 'input_drop_rate': 0.2, 'recurrent_dropout': 0.2, 'full_conn_dropout': 0.2,'full_conn_dim':8,
#               'optimizer': 'sgd', 'learning_rate_init': 0.070311, 'momentum': 0.5, 'nb_epoch': 50, 'batch_size': 2 ** 17}

param_lstm = {'batch_size': 131072,
 'full_conn_dim': 32,
 'full_conn_dropout': 0,
 'hidden_dim': (32,),
 'input_drop_rate': 0,
 'learning_rate_init': 0.070311,
 'momentum': 0.5,
 'nb_epoch': 200,
 'optimizer': 'sgd',
 'recurrent_dropout': 0}

def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1 - K.mean((y_true - K.mean(y_true)) * (y_pred - K.mean(y_pred))) / (K.std(y_true) * K.std(y_pred)))


def res_std(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.std(y_true - y_pred)


# def myloss(y_true_, y_pred_):
#     return 0.5 * K_corr(y_true_, y_pred_) + res_std(y_true_, y_pred_)


def ts_stf_mse(y_true_, y_pred_):
    y_pred, y_true = K.cast(y_pred_, 'float32'), K.cast(y_true_, 'float32')
    return 0.5 * K.std(y_true - y_pred, axis=1) + mean_squared_error(y_true, y_pred)


class LSTMRegMSE(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        if feature_address is None:
            self.dp = DataPrepare(idx_address='/data/group/800319/LittleJunkFix/')
        else:
            self.dp = DataPrepare(idx_address=feature_address)
        self.eval_indicator = factor_eval_indicator

    def predict(self, model, X_test, end_date=None):
        pred_label = model.predict(X_test)
        return pred_label

    def feature_engineering(self, train_feature, train_label, test_feature, test_label):
        train_feature_arr = train_feature.values
        train_label_arr = train_label.values
        test_feature_arr = test_feature.values
        test_label_arr = test_label.values

        train_nan_count, test_nan_count = np.isnan(train_feature_arr).sum(axis=2), np.isnan(test_feature_arr).sum(axis=2)
        train_nan_count, test_nan_count = (train_nan_count > train_feature.shape[-1] * 0.2).sum(axis=1), \
                                          (test_nan_count > test_feature.shape[-1] * 0.2).sum(axis=1)
        train_label_nan, test_label_nan = np.isnan(train_label_arr), np.isnan(test_label_arr)
        selected_train, selected_test = (train_nan_count == 0) & (~train_label_nan), (test_nan_count == 0) & (~test_label_nan)
        train_feature_arr, train_label_arr = train_feature_arr[selected_train], train_label_arr[selected_train]
        test_feature_arr, test_label_arr = test_feature_arr[selected_test], test_label_arr[selected_test]
        selected_train, selected_test = pd.Series(selected_train, index=train_feature.items), \
                                        pd.Series(selected_test, index=test_feature.items)
        selected_train, selected_test = selected_train[selected_train], selected_test[selected_test]
        train_feature_arr[np.isnan(train_feature_arr)] = 0
        test_feature_arr[np.isnan(test_feature_arr)] = 0
        return train_feature_arr.clip(-5, 5), train_label_arr, test_feature_arr.clip(-5, 5), \
               test_label_arr, selected_train, selected_test

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        self.dp.set_date_range(train_idx[0], test_idx[1])
        fix_factor = self.dp.load_data(fix_factor_list + ['future'])
        fix_factor = fix_factor.sort_index(level=[2, 1])
        ts_feature_pn = pd.Panel({x: fix_factor.shift(x).sort_index() for x in list(range(7))[::-1]}).swapaxes(0, 1)

        ts_label = ts_feature_pn.loc[:, 0, 'future']
        ts_feature_pn = ts_feature_pn.drop('future', axis=2)
        ts_label = ts_label.iloc[ts_label.loc[train_idx[0]].shape[0]:]
        ts_feature_pn = ts_feature_pn.iloc[-ts_label.shape[0]:]
        train_feature, train_label, test_feature, test_label = ts_feature_pn.loc[:train_idx[1]], \
                                                               ts_label.loc[:train_idx[1]], \
                                                               ts_feature_pn.loc[test_idx[0]:test_idx[1]], \
                                                               ts_label.loc[test_idx[0]:test_idx[1]]
        train_feature, train_label, test_feature, test_label, train_index, test_index = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label)
        gc.collect()
        # X_train_old, y_train_old, _, _ = pd.read_pickle('/data/user/015664/AFuckingTrigger/seek_para/dataset20180329.pkl')
        return train_feature, train_label, test_feature, test_label, train_index, test_index, time.time() - e

    def get_fix_factor_evaluation(self, num):
        if self.eval_indicator == 'intersection':
            return self.get_fix_factor_evaluation_intersection(num)
        elif self.eval_indicator == 'union':
            return self.get_fix_factor_evaluation_union(num)
        elif self.eval_indicator == 'std_adjusted':
            return self.get_factor_std()
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        factor_list = factor_evaluation.loc[inter_col, self.eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        return factor_list

    def get_factor_std(self):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_eval_path = '/data/group/800319/FixFactorTestResult/'
        eval_res_list = os.listdir(factor_eval_path)
        eval_res_list = list(set(eval_res_list).intersection(set(sample.columns)))
        barly_ret = []
        for each in eval_res_list:
            temp_res = pd.read_pickle(factor_eval_path + each)
            barly_ret.append([each] + temp_res['dc_t_all_ret'].tolist())
        check = pd.DataFrame(barly_ret).set_index(0)
        check['std'], check['mean'] = check.std(axis=1), check.mean(axis=1)
        check['adjusted_std'] = (check['std'] / check['mean']).apply(abs)
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        check[['ic_all_t', 'ic_all_d', 'ic_all_c', 'ic_all_dtc']] = abs(factor_evaluation[['ic_all_t', 'ic_all_d', 'ic_all_c', 'ic_all_dtc']])
        check['t_to_std'] = check['ic_all_t'] / check['adjusted_std']
        check['c_to_std'] = check['ic_all_c'] / check['adjusted_std']
        check['d_to_std'] = check['ic_all_d'] / check['adjusted_std']
        check['score'] = check[['t_to_std', 'c_to_std', 'd_to_std']].mean(axis=1)

        selected = check.sort_values('score', ascending=False)[:500]
        selected = selected[((selected['ic_all_t'] > check['ic_all_t'].quantile(0.8)) +
                             (selected['ic_all_c'] > check['ic_all_c'].quantile(0.8)) +
                             (selected['ic_all_d'] > check['ic_all_d'].quantile(0.8))) > 0]
        return selected.index.tolist()

    def get_fix_factor_evaluation_union(self, num):
        # sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        all_factor = os.listdir(self.feature_address)
        all_factor = [x.replace('.npy', '') for x in all_factor]
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(all_factor)))
        for individual_num in range(10, num + 1):
            factor_list = {}
            for eval_indicator in ['ic_all_t', 'ic_all_c', 'ic_all_d']:
                factor_list[eval_indicator] = factor_evaluation.loc[inter_col, eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:individual_num]
            factor_set = set(factor_list['ic_all_t']).union(set(factor_list['ic_all_c'])).union(set(factor_list['ic_all_d']))
            factor_num = len(factor_set)
            if factor_num >= num:
                print('factor_num', factor_num)
                break
        return ['Close2BarHigh', 'FactorMin70_diff', 'WilliamsIndicator_13h', 'MinExtremRet', 'FWRMin', 'MinPrePriceAutoCorr', 'HighCloseDistance', 'CorrCloseVol_Mean_1', 'HF_VwapAmtUpCorrInLowVolatility_13h', 'SwingPriceCorr', 'HighLowVwapRatio', 'hfMktLSCap', 'GTJA27_weight12', 'HFPSCorrStdAdj', 'HF_ForecastEPDelta40d', 'TwapSkewToVwap', 'HFPVCorr', 'ReLow_13h', 'MinCapitalGainBetaEwm', 'WR_13h', 'MinVwapHLRateBetaBias', 'VwapBollingerBand30min_13h', 'HF_DVwapDVolumeCorrZscore_13h', 'HF_VwapTopTRRatio_13h', 'L2C5', 'HF_MeanIntradayReturnAcrossLosingInvestors_13h', 'StdUpDown', 'CorrHighLowAvgToAmt_Mean_1', 'HF_OpenVwapSkew', 'LogRtn2Amt5', 'WR2d_13h', 'subrr2adjwms_intraday_5', 'Ret30RankMean_5', 'MinPriceAutoCorr', 'hfMktLSCapSR', 'SplitVolumeRatio', 'VwapStdCorrDistanceLow10d_13h', 'HighFreqRelativeClose', 'PDS', 'FactorMin215_mean', 'GTJA2', 'adjstdstm_intraday_5', 'WRMean5d_13h', 'HF_VmL2HmVStdRatio', 'SignDownWick', 'FactorMin450_mean_re', 'MinuteVolatilityPriceCorr', 'FactorAlpha027', 'HLTR_mean5_intraday', 'CRCS_raw_rank_ms10', 'HF_CorrMaxVolumeZScore_13h', 'MinPre30mAutoCorr', 'VolBurstReturn', 'Close2High', 'FactorMin87_diff', 'hfPVcorrHD', 'WilliamsPriceVolCorrMultiple_13h', 'MaxDrawDown', 'HfSwingCloseCorr', 'HF_WR2d', 'HF_RetHHIZscore', 'MinVwapHLRateBetaDelta', 'TemporalVolumePriceCorr', 'WilliamUp_diffstd5', 'PriceDeviationBias10d', 'HF_PriceDiffRatio', 'CorrMaxRePriceRank', 'MinCorrAbsRePriceRank2D', 'RevExclu4mean', 'HighLowMeanVwapRetSharpe', 'CorrDelVolumePriceMean', 'dailyms_intraday_5', 'MinMaxRet', 'RSRS_Mean_1', 'WAPResistBackTop_13h', 'MinCorrVolumePrice_1', 'HF_RSRS', 'HFPSCorr', 'VolaDownward20', 'VwapmaLowDiffSkew_13h', 'CorrVWAPdt', 'CorrAmpVwap_1', 'MinCapitalGainOverhang', 'CGO', 'LogDeltaVol', 'PriceRange_5', 'FactorMin129_diff', 'HFPVCorrStdAdj', 'HighLowStdBias20d', 'sistdwfiavg2_3_re', 'Min1WeightedFlow_1', 'VwapStdCorrBias20d_13h', 'CloseExcessPercent_1', 'VwapSwingCorr', 'HF_RSRSZScore', 'DrawdownSkew', 'PVSwingCorr', 'Ret30Mean2Std_10', 'hfCPVCorrHD_13h', 'VolumeUpPVCorr_13h', 'adjEMAbc_intraday5']

        # return list(factor_set)

    def get_fix_factor_evaluation_intersection(self, num):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        for individual_num in range(num, num * 2):
            factor_list = {}
            for eval_indicator in ['ic_all_t', 'ic_all_c', 'ic_all_d']:
                factor_list[eval_indicator] = factor_evaluation.loc[inter_col, eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:individual_num]
            factor_set = set(factor_list['ic_all_t']).intersection(set(factor_list['ic_all_c'])).intersection(set(factor_list['ic_all_d']))
            factor_num = len(factor_set)
            if factor_num >= num:
                print('factor_num', factor_num)
                break
        return sorted(list(factor_set))

    def Network(self, input_shape, param=None):
        inputs = Input(input_shape, name='daily_factor_sequence')
        lstm = LSTM(param['hidden_dim'][0], dropout=param['full_conn_dropout'], recurrent_dropout=param['recurrent_dropout'], return_sequences=True, name='lstm0')(inputs)
        for idx, hiddem_dim in enumerate(param['hidden_dim'][1:]):
            lstm = LSTM(hiddem_dim, dropout=param['full_conn_dropout'], recurrent_dropout=param['recurrent_dropout'], return_sequences=True, name='lstm%d' % (idx + 1))(lstm)
            lstm = BatchNormalization(axis=-2, name='BN%d' % idx)(lstm)
        flatten = Flatten(name='flatten')(lstm)
        if param['full_conn_dropout'] > 0:
            drop = Dropout(param['full_conn_dropout'])(flatten)
            full_conn = Dense(param['full_conn_dim'], activation='sigmoid', name='Full_Conn')(drop)
        else:
            full_conn = Dense(param['full_conn_dim'], activation='sigmoid', name='Full_Conn')(flatten)
        out = Dense(1, activation='sigmoid')(full_conn)
        model = Model(inputs=inputs, outputs=out)
        optimizer = SGD(lr=param['learning_rate_init'], momentum=param['momentum'])
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae', 'mse'])
        return model

    def train_model(self, X, y_train, params, end_date=None):
        if not os.path.exists(params['train_log_path']):
            os.mkdir(params['train_log_path'])
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        X_train, train_index = X
        date_list = sorted(list(set([x[0] for x in train_index.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_id, val_id = pd.Series(False, index=train_index.index), pd.Series(False, index=train_index.index)
        train_id.loc[date_list] = True
        val_id.loc[val_date] = True
        train_features, train_label = X_train[train_id.values], y_train[train_id.values]
        # params['learning_rate_init'] = 0.070311
        model = self.Network(input_shape=X_train.shape[1:], param=params)
        # model = Network(input_shape=X_train.shape[1:], param=params)
        early_stopping = EarlyStopping(monitor='val_loss', patience=15)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.6,
                                      patience=4, min_lr=0.001)
        train_log = CSVLogger(params['train_log_path'] + '%d.csv' % val_date[0])
        callbacks_list = [early_stopping, reduce_lr, train_log]
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.h5' % val_date[0]):
            model.load_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
            print('load model from local')
        else:
            model.fit(train_features, train_label, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=0, \
                      shuffle=True, callbacks=callbacks_list, validation_split=0.05)
            model.save_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train[val_id.values], y_train[val_id.values]
            val_labels = pd.DataFrame({'future':val_labels})
            val_labels['prediction'] =model.predict(val_features)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % val_date[0])
        return model

        # for cell_num in param['hidden_dim']:
        #     x = SimpleRNN(cell_num,dropout=param['full_conn_dropout'],recurrent_dropout=param['recurrent_dropout'],return_sequences=True)(x)

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()  # {'actual_label':pd.DataFrame(),'prediction':pd.DataFrame()}
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None
        fix_factor_list = self.get_fix_factor_evaluation(factor_nums)
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])
            # if test_end_idx!= 20170607:
            #     continue
            X_train, y_train, X_test, y_test, train_index, test_index, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()
            if len(X_test) == 0:
                print('zero sample')
                continue
            if len(X_train) > 2000 > 1:
                print('re-train in this round')
                model = self.train_model((X_train, train_index), y_train, params, train_end_idx)
            # pd.to_pickle([X_train,y_train,X_test,y_test],'/data/user/015664/AFuckingTrigger/seek_para/dataset20180329.pkl')
            if model is None:
                continue
            training_time = time.time() - e
            pred_label = self.predict(model, X_test, train_end_idx)

            y_test = pd.DataFrame({'actual_label':y_test},index=test_index.index)
            y_test['prediction'] = pred_label
            print(train_end_idx,y_test.corr())
            label = label.append(y_test)
            del X_train, y_train, X_test, y_test, pred_label
            gc.collect()
        return label
