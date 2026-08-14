# @Time : 2021/3/9 10:21
# @Author : Zhichen Lu
# @File : NNExtractor_test.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from keras.callbacks import *
from keras.layers import Dropout, Dense
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
import xgboost as xgb
import tensorflow as tf
from keras.utils.training_utils import multi_gpu_model

# y_true_ = train_label[:10000].values
# y_pred_ = model.predict(train_features[:10000].values)
def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.mean((y_true - K.mean(y_true,axis=0))*(y_pred-K.mean(y_pred,axis=0)),axis=0)/ (K.std(y_true,axis=0) * K.std(y_pred,axis=0))



def myloss(y_true_, y_pred_):

    corr = K_corr(y_true_, y_pred_)
    mean_corr = K.mean(corr)
    std_corr = K.std(corr)
    return -1*mean_corr#+std_corr
    # y_true, y_pred = K.cast(y_true_,dtype='float32'),K.cast(y_pred_,dtype='float32')
    # return mean_squared_error(y_pred,y_true) + 2*K_corr(y_true_,y_pred_)

best_param_clf_nn = {
    'activation': 'sigmoid',
    'alpha': 9.756090506594905e-05,
    'hidden_layer_sizes': (100,),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.15,#0.0703114914234283,
    'momentum': 0.1669382592981298, 'solver': 'sgd',
    'nb_epoch': 200,
    'batch_size': 2 ** 17
}

best_param_clf_nn = {'activation': 'relu',
 'alpha': 9.756090506594905e-05,
 'batch_size': 131072,
 'dropout': 0.2,
 'hidden_layer_sizes': (100,),
 'learning_rate': 'adaptive',
 'learning_rate_init': 0.1,
 'momentum': 0.5,
 'nb_epoch': 300,
 'solver': 'sgd'}

def NN( input_dim, params):
    print('CorrOnly')
    hidden_layer_sizes = params['hidden_layer_sizes']
    model = Sequential()
    model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
    for dim in hidden_layer_sizes[1:]:
        model.add(Dense(dim, activation=params['activation']))
    optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
    model = compile_model(model, optimizer, [])
    # print(model.summary())
    return model


def compile_model(model4compile, opt_er, metrics_eval):
    model4compile.compile(loss=myloss, \
                          optimizer=opt_er, metrics=metrics_eval)
    return model4compile


end_date = 20160328
params = best_param_clf_nn
params['train_log_path'] = '/data/user/015664/AFuckingTrigger/model_test/'
best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}

key_list = set(best_param_clf_xgb.keys()).intersection(set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
args_param = {x:best_param_clf_xgb[x] for x in key_list}


X_train, y_train, X_test, y_test,sorted_factor_list = pd.read_pickle('/data/user/015664/AFuckingTrigger/model_test/dataset6.pkl')
feature_to_extract = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/NNExtractor_ic_half_t_train200_test10_factor_num600_norm_window_40_feature_path/%d.pkl'%end_date)
factor_list = X_train.columns.tolist()
feature_use_direct = sorted(list(set(factor_list) - set(feature_to_extract)))

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

model_extracted = NN(300,params=params)
model_extracted = multi_gpu_model(model_extracted,gpus=None)
model_extracted.load_weights(
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/NNExtractor_ic_half_t_train200_test10_factor_num600_norm_window_40_model_conf/%d.h5' % end_date)

extracted_train_feature = model_extracted.predict(X_train[feature_to_extract].values)

X_train = pd.concat([X_train[feature_use_direct], pd.DataFrame(extracted_train_feature, index=X_train.index)], axis=1)

train_features, train_label = X_train, y_train
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000].values)
d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)


model = xgb.train(args_param, d_train, num_boost_round=args_param['n_estimators'],evals=[(d_eval,'d_eval')],early_stopping_rounds=15,verbose_eval=False)

extracted_test_feature = model_extracted.predict(X_test[feature_to_extract])
X_test = pd.concat([X_test[feature_use_direct], pd.DataFrame(extracted_test_feature, index=X_test.index)], axis=1)
d_test = xgb.DMatrix(X_test)
pred_label = model.predict(d_test)
y_test['prediction'] = pred_label
y_test.corr()

check = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40/%d.pkl'%end_date)
check.corr()

"""
train_features,train_label = X_train[sorted_factor_list[300:]][:1000000],y_train[:1000000]
val_feature,val_label = X_train[sorted_factor_list[300:]][1000000:],y_train[1000000:]


model = NN(input_dim=300, params=params)
early_stopping = EarlyStopping(monitor='val_loss', patience=10)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                              patience=5, min_lr=0.001)
train_log = CSVLogger(params['train_log_path'] + 'train_log.csv' )
callbacks_list = [early_stopping, reduce_lr, train_log]

model.fit(train_features.values, train_label.values, epochs=50, \
          batch_size=params['batch_size'], verbose=1, \
          shuffle=True, callbacks=callbacks_list, validation_split=0.1)
pred = model.predict(train_features.values)
pred_df = pd.DataFrame(pred,index=train_label.index)
pred_df['label'] = train_label[train_label.columns[0]]
corr = pred_df.corr()

val_pred = model.predict(val_feature.values)
val_pred_df = pd.DataFrame(val_pred,index=val_feature.index)
val_pred_df['label'] = val_label[val_label.columns[0]]
val_corr = val_pred_df.corr()
val_corr['label'].drop('label').mean()

origin_corr = val_feature.corrwith(val_label['actual_label'])

all_corr = pd.concat([pred_df,val_pred_df]).corr()
all_corr['label'].drop('label').mean()

# corr['label'].apply(abs).drop('label').max()
#
# y_true,y_pred = train_label.values,pred[:,[0]]
# pd.concat([pd.DataFrame(y_true),pd.DataFrame(y_pred)],axis=1).corr()
# np.nanmean((y_true - np.nanmean(y_true,axis=0))*(y_pred - np.nanmean(y_pred,axis=0)),axis=0)/(np.nanstd(y_true,axis=0)*np.nanstd(y_pred,axis=0))
#
# corr_K = K_corr(train_label.values,pred)
# a = K.eval(corr_K)

# loss = myloss(train_label.values,pred)
# loss = K.eval(loss)
# loss.shape
"""