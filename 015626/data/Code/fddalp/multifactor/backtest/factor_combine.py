# -*- coding: utf-8 -*-
"""
# Rock Mountain Dew

"""

import matplotlib.pyplot as plt  
import numpy as np
import pandas as pd
import statsmodels.api as sm
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt
from multifactor.backtest.FactorTool import *
from multifactor.backtest import FactorTest
import os


from sklearn import linear_model


####################################################################################################################
""" factor combine xgboost """

import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score,precision_score,recall_score#,roc_auc_score,cconfusion_mat


def evaluate_model(y_true,y_pred,pred_type='reg',measure=None):
    """ classification
        accuracy: (tp+tn)/(p+n)
        precision: tp / (tp + fp)
        recall: tp / (tp + fn)
        
    """      
    if pred_type=='classification':
        model_eval = accuracy_score(y_true,y_pred),precision_score(y_true,y_pred),recall_score(y_true,y_pred)
    elif pred_type=='reg':
        if measure is not None:
            if measure=='r2':
                model_eval = r2_score(y_true,y_pred)
        else:
            model_eval = r2_score(y_true,y_pred), mean_absolute_error(y_true,y_pred),mean_squared_error(y_true,y_pred) 
    return model_eval



def factor_combine_xgboost(combine_dict,holding_period_ret,holding_period,rolling_win=60,param_tuning=None,
                           model_eval=True
                           ):
    """Wrapper xbboost regression
    X: (MultiIndex) index(dt,Ticker), columns: factor
    y: (MI) holding_period_return, index(dt,Ticker), columns: holding_period_return
    holding_period: (int) must match the holding_period_return for lagging purpose
    rolling_win: (int) look back windows
    param_tuning: (int) frequency for adjusting hyperparameter for xgboost regression   
    """
    date_list = holding_period_ret.index.tolist()
    date_num,stock_num = holding_period_ret.shape
    rebal_num = date_num - rolling_win - holding_period
    #params = {"objective": "reg:linear"}    
    params={"objective": "reg:linear", "booster":"gbtree"}
    y_pred = np.empty([date_num,stock_num])
    y_pred [:] = np.nan
    reg_list = list(combine_dict.keys())
    fac_num = len(reg_list)
    y_mat = NormWinsor(holding_period_ret).values 
    x_mat = np.ones([fac_num,date_num,stock_num])
    if model_eval:
        r2_mat = [np.nan]*date_num
    evl_str=''
    for i in range(fac_num):
        fac = reg_list[i]
        x_mat[i,:,:] = combine_dict[fac].values
    print ('Start fiting model')
    for i in range(rebal_num):
        idx = i+rolling_win+holding_period-1
        try:
            #date_train = date_list[i:i+rolling_win]
            #date_test = date_list[idx] # date lag 1 already   5 2 8 
            X_train,y_train = x_mat[:,i:i+rolling_win,:],y_mat[i:i+rolling_win,:]
            X_test,y_test = x_mat[:,idx,:].T,y_mat[idx,:].T
            X_train_MI = X_train.reshape(X_train.shape[1]*X_train.shape[2],X_train.shape[0])                        
            y_train_MI = y_train.reshape(y_train.shape[0]*y_train.shape[1],1)
            mask = np.isfinite(y_train_MI).ravel()
            tic = time.time()
            gbm = xgb.XGBRegressor().fit(X_train_MI[mask,:],y_train_MI[mask])
            toc = time.time()
            train_time = toc-tic
            y_pred[idx,:] = gbm.predict(X_test)
            if model_eval:
                mask_test = np.isfinite(y_test)
                r2_mat[idx] = evaluate_model(y_test[mask_test],y_pred[idx,:][mask_test],pred_type='reg',measure='r2')
                evl_str = 'R2: '+str(round(r2_mat[idx],3))
            print (date_list[idx],' /train time: ',str(round(train_time,2)),'s/',evl_str)
        except:
            print ('failed')
                
    factor_combine=pd.DataFrame(y_pred,index=holding_period_ret.index,columns=holding_period_ret.columns)            

    return factor_combine




# https://www.quantopian.com/posts/simple-machine-learning-example-mk-ii
# Use a random forest classifier. More here: http://scikit-learn.org/stable/user_guide.html
from sklearn.ensemble import RandomForestRegressor
import numpy as np


odel = RandomForestRegressor()
































