# @Time : 2021/8/3 10:53
# @Author : Zhichen Lu
# @File : ParamSeeking.py


import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from typing import Dict, List, Tuple, Type, Union
import os,time,gc,datetime
from StrongStockModel.conf.path_config import root_path
import torch
# from torch import nn
from tqdm import tqdm
from torch.utils.data import DataLoader,TensorDataset
import numpy as np
torch.set_default_tensor_type(torch.DoubleTensor)

def ic(y_pred,y_true):
    return ((y_pred - y_pred.mean(dim=0)).transpose(0,1)*(y_true-y_true.mean())).mean(dim=1)/(y_pred.std(dim=0)*y_true.std())

def corr_matrix(y_pred):
    norm_y = (y_pred - y_pred.mean(dim=0))/y_pred.std(dim=0)
    shape = torch.ones(norm_y.shape)
    return (norm_y.transpose(0,1)@norm_y)/(shape.sum(dim=0)-1)

def myloss(y_pred,y_true,inter_corr_eof=0):
    corr_loss = ic(y_pred, y_true)
    corr_m = corr_matrix(y_pred)
    loss = 1 - (corr_loss).mean() + inter_corr_eof * (corr_m ** 2).mean() ** 0.5
    return loss,corr_loss,corr_m



model_conf_path = f'{root_path}TempData/model_conf/'
log_path = f'{root_path}TempData/log/'

if not os.path.exists(model_conf_path):
    os.makedirs(model_conf_path)
if not os.path.exists(log_path):
    os.makedirs(log_path)


X_train,y_train = pd.read_pickle(f'{root_path}TempData/TrainSetForNNexTractorOpt.pkl')

split_ratio = 0.2
split_num = int(X_train.shape[0]*split_ratio)

X_val,y_val =torch.from_numpy(X_train[-split_num:].values).double(),torch.from_numpy(y_train[-split_num:]['actual_label'].values).double()

X = torch.from_numpy(X_train[:-split_num].values).double()
y = torch.from_numpy(y_train[:-split_num]['actual_label'].values).double()

train_set = TensorDataset(X,y)
train_loder = DataLoader(dataset=train_set,batch_size=2**12,shuffle=True,num_workers=2)

dim = X_train.shape[1]
model = torch.nn.Sequential(torch.nn.Linear(dim,400),torch.nn.LogSigmoid(),torch.nn.Linear(400,100))
model.double()
learning_rate = 0.1
inter_eof = 0.5
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

train_log,val_log = [],[]

for i in range(2):
    bar = tqdm(train_loder)
    loss_eval,corr_loss_eval,corr_m_eval =np.nan,np.nan,np.nan
    for batch in bar:
        bar.set_description(f'loss:{loss_eval:.4f}  corr:{corr_loss_eval:.4f}  inter_corr:{corr_m_eval:.4f}')
        inputs,labels = batch
        pred = model(inputs)
        loss,corr_loss,corr_m = myloss(pred,labels,inter_eof)
        loss_eval, corr_loss_eval, corr_m_eval = loss.item(), abs(corr_loss).mean().item(), abs(corr_m).mean().item()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # y_pred,y_true = pred,labels
        # ((y_pred - y_pred.mean(dim=0)).transpose(0, 1) * (y_true - y_true.mean())).mean(dim=1) / (y_pred.std(dim=0) * y_true.std())

    # loss, corr_loss, corr_m = myloss(X, y, inter_eof)
    # loss_eval, corr_loss_eval, corr_m_eval = loss.item(), abs(corr_loss).mean().item(), abs(corr_m).mean().item()
    val_pred = model(X_val)
    val_loss, val_corr_loss,val_corr_m = myloss(val_pred,y_val,inter_eof)
    _, val_ic_loss,_ = myloss(X_val,y_val,inter_eof)
    val_loss, val_corr_loss, val_corr_m = val_loss.item(), abs(val_corr_loss).mean().item(),abs(val_corr_m).mean().item()

    train_log.append([loss_eval,corr_loss_eval,corr_m_eval ])
    val_log.append([val_loss, val_corr_loss, val_corr_m])
    print(f'tain_total_loss {loss_eval:.4f} train_corr:{corr_loss_eval:.4f} train_inter_corr{corr_m_eval:.4f}||',
          f'val_total_loss {val_loss:.4f} val_corr:{val_corr_loss:.4f} val_inter_corr{val_corr_m:.4f}')







X_test,y_test = pd.read_pickle(f'{root_path}TempData/TestSetForNNexTractorOpt.pkl')
# X_val,y_val = torch.from_numpy(X_test.values),torch.from_numpy(y_test['actual_label'].values)

# a = pd.Series({each:y_test.corrwith(X_test[each]) for each in X_test.columns})
# a.apply(lambda x : x['actual_label'])

Feature_test = model(torch.from_numpy(X_test.values))

Feature_test = pd.DataFrame(Feature_test.detach().numpy())
Feature_test.index = y_test.index
Feature_test['label'] = y_test
corr = Feature_test.corr()
corr_label = corr['label'].drop('label')
corr_label.min()


