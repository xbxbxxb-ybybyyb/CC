# @Time : 2020/12/24 10:15
# @Author : Zhichen Lu
# @File : LSTMRegHXLoading.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
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
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
# from dataApi.DataPrepare import DataPrepare
from tqdm import tqdm
import gc, time, datetime
from StrongStockModel.conf.path_config import root_path
from scipy.ndimage.interpolation import shift

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


def myloss(y_true_, y_pred_):
    return 0.5 * K_corr(y_true_, y_pred_) + res_std(y_true_, y_pred_)


def ts_stf_mse(y_true_, y_pred_):
    y_pred, y_true = K.cast(y_pred_, 'float32'), K.cast(y_true_, 'float32')
    return 0.5 * K.std(y_true - y_pred, axis=1) + mean_squared_error(y_true, y_pred)


class LSTMRegHXLoading(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.eval_indicator = factor_eval_indicator
        if factor_eval_indicator == 'union':
            self.dp = FixFactorRollPrepare(factor_list=self.get_fix_factor_evaluation_union(101))
        else:
            raise Exception('')
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
        X, y, idx_date, idx_time, idx_code = self.dp.load_data(start_date=train_idx[0],end_date=test_idx[-1],return_idx=True)
        X, y, idx_date, idx_time, idx_code = self.dp.feature_engineering(X, y, idx_date, idx_time, idx_code)
        index = pd.MultiIndex.from_tuples(list(zip(idx_date.tolist(),idx_time.tolist(),idx_code.tolist())))
        index = pd.Series(True,index=index)
        train_index, test_index = index.loc[train_idx[0]:train_idx[1]],index.loc[test_idx[0]:test_idx[1]]
        train_feature, train_label, test_feature, test_label = X[:train_index.shape[0]],y[:train_index.shape[0]],X[train_index.shape[0]:],y[train_index.shape[0]:]
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
        model.compile(optimizer=optimizer, loss=myloss, metrics=['mae', 'mse'])
        return model

    def train_model(self, X, y_train, params, end_date=None):
        if not os.path.exists(params['train_log_path']):
            os.mkdir(params['train_log_path'])
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        X_train, train_index = X
        date_list = sorted(list(set([x[0] for x in train_index.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9,-11]]
        date_list = list(set(date_list) - set(val_date))
        train_id, val_id = pd.Series(False, index=train_index.index), pd.Series(False, index=train_index.index)
        train_id.loc[date_list] = True
        val_id.loc[val_date[1:]] = True
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
            print('load model from local %d'%val_date[0])
        else:
            model.fit(train_features, train_label, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=0, \
                      shuffle=True, callbacks=callbacks_list, validation_split=0.05)
            model.save_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train[val_id.values], y_train[val_id.values]
            val_labels = pd.DataFrame({'future':val_labels},index=val_id[val_id].index)
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


param_list = [(0, (20150309, 20151225, 20151228, 20160111)),
              (1, (20150323, 20160111, 20160112, 20160125)),
              (2, (20150407, 20160125, 20160126, 20160215)),
              (3, (20150421, 20160215, 20160216, 20160229)),
              (4, (20150506, 20160229, 20160301, 20160314)),
              (5, (20150520, 20160314, 20160315, 20160328)),
              (6, (20150603, 20160328, 20160329, 20160412)),
              (7, (20150617, 20160412, 20160413, 20160426)),
              (8, (20150702, 20160426, 20160427, 20160511)),
              (9, (20150716, 20160511, 20160512, 20160525)),
              (10, (20150730, 20160525, 20160526, 20160608)),
              (11, (20150813, 20160608, 20160613, 20160624)),
              (12, (20150827, 20160624, 20160627, 20160708)),
              (13, (20150914, 20160708, 20160711, 20160722)),
              (14, (20150928, 20160722, 20160725, 20160805)),
              (15, (20151019, 20160805, 20160808, 20160819)),
              (16, (20151102, 20160819, 20160822, 20160902)),
              (17, (20151116, 20160902, 20160905, 20160920)),
              (18, (20151130, 20160920, 20160921, 20161011)),
              (19, (20151214, 20161011, 20161012, 20161025)),
              (20, (20151228, 20161025, 20161026, 20161108)),
              (21, (20160112, 20161108, 20161109, 20161122)),
              (22, (20160126, 20161122, 20161123, 20161206)),
              (23, (20160216, 20161206, 20161207, 20161220)),
              (24, (20160301, 20161220, 20161221, 20170104)),
              (25, (20160315, 20170104, 20170105, 20170118)),
              (26, (20160329, 20170118, 20170119, 20170208)),
              (27, (20160413, 20170208, 20170209, 20170222)),
              (28, (20160427, 20170222, 20170223, 20170308)),
              (29, (20160512, 20170308, 20170309, 20170322)),
              (30, (20160526, 20170322, 20170323, 20170407)),
              (31, (20160613, 20170407, 20170410, 20170421)),
              (32, (20160627, 20170421, 20170424, 20170508)),
              (33, (20160711, 20170508, 20170509, 20170522)),
              (34, (20160725, 20170522, 20170523, 20170607)),
              (35, (20160808, 20170607, 20170608, 20170621)),
              (36, (20160822, 20170621, 20170622, 20170705)),
              (37, (20160905, 20170705, 20170706, 20170719)),
              (38, (20160921, 20170719, 20170720, 20170802)),
              (39, (20161012, 20170802, 20170803, 20170816)),
              (40, (20161026, 20170816, 20170817, 20170830)),
              (41, (20161109, 20170830, 20170831, 20170913)),
              (42, (20161123, 20170913, 20170914, 20170927)),
              (43, (20161207, 20170927, 20170928, 20171018)),
              (44, (20161221, 20171018, 20171019, 20171101)),
              (45, (20170105, 20171101, 20171102, 20171115)),
              (46, (20170119, 20171115, 20171116, 20171129)),
              (47, (20170209, 20171129, 20171130, 20171213)),
              (48, (20170223, 20171213, 20171214, 20171227)),
              (49, (20170309, 20171227, 20171228, 20180111)),
              (50, (20170323, 20180111, 20180112, 20180125)),
              (51, (20170410, 20180125, 20180126, 20180208)),
              (52, (20170424, 20180208, 20180209, 20180301)),
              (53, (20170509, 20180301, 20180302, 20180315)),
              (54, (20170523, 20180315, 20180316, 20180329)),
              (55, (20170608, 20180329, 20180330, 20180416)),
              (56, (20170622, 20180416, 20180417, 20180502)),
              (57, (20170706, 20180502, 20180503, 20180516)),
              (58, (20170720, 20180516, 20180517, 20180530)),
              (59, (20170803, 20180530, 20180531, 20180613)),
              (60, (20170817, 20180613, 20180614, 20180628)),
              (61, (20170831, 20180628, 20180629, 20180712)),
              (62, (20170914, 20180712, 20180713, 20180726)),
              (63, (20170928, 20180726, 20180727, 20180809)),
              (64, (20171019, 20180809, 20180810, 20180823)),
              (65, (20171102, 20180823, 20180824, 20180906)),
              (66, (20171116, 20180906, 20180907, 20180920)),
              (67, (20171130, 20180920, 20180921, 20181012)),
              (68, (20171214, 20181012, 20181015, 20181026)),
              (69, (20171228, 20181026, 20181029, 20181109)),
              (70, (20180112, 20181109, 20181112, 20181123)),
              (71, (20180126, 20181123, 20181126, 20181207)),
              (72, (20180209, 20181207, 20181210, 20181221))]


def main(i):
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/LittleJunkFix/'#'/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d_and_binary/' % N
    train_period = 200
    test_period = 10
    factor_num = 100
    indicator = 'union'
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LSTM_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
        indicator, train_period, test_period, factor_num, N)
    print(out_file)
    para = param_list[i][1]
    print(para)
    base_dir = out_file.replace('.pkl', '/')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % para[1]):
        print(base_dir + '%d.pkl' % para[1], 'exist')
        # return
    model = LSTMRegHXLoading(para[0], para[-1], None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path, factor_eval_indicator=indicator)
    # best_param_clf_xgb['objective'] = 'reg:squarederror'
    param_lstm.update({
        'val_pred_path':out_file.replace('.pkl', '_val_pred/'),
        'train_log_path':out_file.replace('.pkl', '_train_log/'),
        'model_conf_path':out_file.replace('.pkl', '_model_conf/'),
        'load local model':True
    })
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl','_train_pred/')
    label = model.rolling_train_and_predict(params=param_lstm, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % para[1])
    print(base_dir + '%d.pkl' % para[1])

from xquant.compute.aimr import AIMR

idx = 33#int(AIMR.getParam())
main(idx)